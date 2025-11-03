"""
完整的自動化下載、解壓、上傳系統
適用於I7-11代 (8核16線程)

【獨立可移植版本】
- 使用 config.py 進行配置
- 包含完整的 NAS 上傳器
- 可移動到任何有 Python 和 SRA Toolkit 的環境
"""

import json
import subprocess
import time
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import sys
import os
import threading

# 導入配置和工具
try:
    from config import *
    from nas_uploader import NASUploader
    from tqdm import tqdm
except ImportError as e:
    print(f"❌ 導入失敗: {e}")
    if "tqdm" in str(e):
        print("請安裝 tqdm: pip install tqdm")
    else:
        print("請確保 config.py 和 nas_uploader.py 在同一目錄")
    sys.exit(1)

# ==================== 從 config.py 讀取配置 ====================

# 並行設置 (從 config.py 讀取)
# MAX_WORKERS = 6
# FASTERQ_THREADS = 5
# 總解壓線程: 6 × 5 = 30線程

# 路徑設置 (從 config.py 讀取)
SRA_TEMP_DIR = Path(SRA_TEMP_DIR)
TMP_DIR = Path(FASTQ_TEMP_DIR)
FASTQ_OUTPUT_DIR = Path(FASTQ_OUTPUT_DIR)

# NAS設置 (從 config.py 讀取)
NAS_CONFIG = {
    "host": NAS_HOST,
    "port": NAS_PORT,
    "username": NAS_USER,
    "password": NAS_PASS,
    "fastq_path": NAS_FASTQ_PATH,
    "sra_path": NAS_SRA_PATH,
}

# 超時設置（可透過環境變數調整）
PREFETCH_TIMEOUT = int(os.environ.get("PREFETCH_TIMEOUT", 10800))  # 3小時（大檔案需要更長時間）
FASTERQ_TIMEOUT = int(os.environ.get("FASTERQ_TIMEOUT", 10800))  # 3小時
UPLOAD_TIMEOUT = int(os.environ.get("UPLOAD_TIMEOUT", 7200))  # 2小時

# ==================== 進度管理 ====================
# 注意: NASUploader 已從 nas_uploader.py 導入


class ProgressManager:
    def __init__(self, progress_file="download_progress.json"):
        self.progress_file = Path(progress_file)
        self.progress = self.load_progress()
        self.save_count = 0  # 追蹤保存次數
        self.last_backup_time = None  # 上次備份時間

    def load_progress(self):
        """載入進度檔案,自動處理錯誤並恢復備份"""
        if self.progress_file.exists():
            try:
                # 檢查檔案是否為空
                if self.progress_file.stat().st_size == 0:
                    print("⚠️  進度檔案為空,嘗試恢復備份...")
                    return self._restore_from_backup()

                # 嘗試載入 JSON
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    return json.load(f)

            except json.JSONDecodeError as e:
                print(f"⚠️  進度檔案格式錯誤: {e}")
                print("   嘗試恢復備份...")
                return self._restore_from_backup()

            except Exception as e:
                print(f"⚠️  載入進度檔案失敗: {e}")
                print("   使用新的進度記錄")

        return {"completed": [], "failed": [], "remaining": []}

    def _restore_from_backup(self):
        """從備份檔案恢復"""
        import glob

        # 尋找最新的備份檔案
        backup_pattern = str(
            self.progress_file.parent / "download_progress_backup_*.json"
        )
        backups = sorted(glob.glob(backup_pattern), reverse=True)

        if backups:
            latest_backup = backups[0]
            try:
                print(f"   找到備份: {Path(latest_backup).name}")
                with open(latest_backup, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 恢復備份到主檔案
                import shutil

                shutil.copy(latest_backup, self.progress_file)
                print(f"✅ 已恢復備份!")
                return data

            except Exception as e:
                print(f"❌ 恢復備份失敗: {e}")
        else:
            print("   找不到備份檔案")

        return {"completed": [], "failed": [], "remaining": []}

    def save_progress(self):
        """安全地儲存進度檔案 (先寫臨時檔,再重命名)"""
        import os
        from datetime import datetime

        try:
            # 每10次保存或每30分鐘創建一個帶時間戳的備份
            self.save_count += 1
            current_time = datetime.now()

            should_backup = False
            if self.save_count % 10 == 0:  # 每10次保存
                should_backup = True
            elif (
                self.last_backup_time is None
                or (current_time - self.last_backup_time).total_seconds() > 1800
            ):  # 30分鐘
                should_backup = True

            if should_backup:
                backup_name = f"download_progress_backup_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = self.progress_file.parent / backup_name
                try:
                    if self.progress_file.exists():
                        import shutil

                        shutil.copy2(self.progress_file, backup_path)
                        self.last_backup_time = current_time
                        print(f"💾 已創建備份: {backup_name}")
                except Exception as e:
                    print(f"⚠️  創建備份失敗 (繼續執行): {e}")

            # 寫入臨時檔案
            temp_file = self.progress_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.progress, f, indent=2, ensure_ascii=False)

            # 驗證 JSON 格式正確
            with open(temp_file, "r", encoding="utf-8") as f:
                json.load(f)

            # 原子性替換 - Windows 安全做法
            # 先創建備份,再替換,最後刪除備份
            backup_file = None
            try:
                if self.progress_file.exists():
                    # 創建備份
                    backup_file = self.progress_file.with_suffix(".bak")
                    if backup_file.exists():
                        backup_file.unlink()
                    self.progress_file.rename(backup_file)

                # 重命名臨時檔案為正式檔案
                temp_file.rename(self.progress_file)

                # 成功後刪除備份
                if backup_file and backup_file.exists():
                    backup_file.unlink()

            except Exception as e:
                # 如果替換失敗,恢復備份
                if backup_file and backup_file.exists():
                    if not self.progress_file.exists():
                        backup_file.rename(self.progress_file)
                        print(f"⚠️  儲存失敗,已恢復備份: {e}")
                raise

        except Exception as e:
            print(f"⚠️  儲存進度檔案失敗: {e}")
            # 清理臨時檔案
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass

    def mark_completed(self, run_id):
        """標記為完成"""
        if run_id not in self.progress["completed"]:
            self.progress["completed"].append(run_id)
            self.progress["completed"].sort()

        # 從failed移除
        self.progress["failed"] = [
            f
            for f in self.progress.get("failed", [])
            if (isinstance(f, dict) and f.get("run_id") != run_id) or f != run_id
        ]

        self.save_progress()

    def mark_failed(self, run_id, step, error):
        """標記為失敗"""
        failure_entry = {
            "run_id": run_id,
            "step": step,
            "error": str(error),
            "time": datetime.now().isoformat(),
        }

        # 更新或新增失敗記錄
        failed_list = self.progress.get("failed", [])
        if (
            isinstance(failed_list, list)
            and len(failed_list) > 0
            and isinstance(failed_list[0], dict)
        ):
            # 移除舊記錄
            failed_list = [f for f in failed_list if f.get("run_id") != run_id]
        else:
            failed_list = []

        failed_list.append(failure_entry)
        self.progress["failed"] = failed_list

        self.save_progress()


# ==================== 下載器 ====================


def get_nas_samples():
    """獲取NAS上已有的樣本"""
    uploader = NASUploader(
        NAS_CONFIG["host"],
        NAS_CONFIG["port"],
        NAS_CONFIG["username"],
        NAS_CONFIG["password"],
    )

    try:
        if not uploader.connect():
            print(f"⚠️ 無法連接到NAS")
            return set()

        samples = set()
        try:
            files = uploader.sftp.listdir(NAS_CONFIG["fastq_path"])
            for f in files:
                if f.endswith(".fastq"):
                    sample = f.rsplit("_", 1)[0]
                    samples.add(sample)
        except:
            pass

        uploader.disconnect()
        return samples

    except Exception as e:
        print(f"⚠️ 無法檢查NAS: {e}")
        uploader.disconnect()
        return set()


def get_all_runs_from_file():
    """從runs.txt讀取所有樣本 (SRR, ERR, DRR)"""
    # 支援透過環境變數指定不同的 runs 檔案
    runs_filename = os.environ.get("RUNS_FILE", "runs.txt")
    runs_file = Path(runs_filename)
    
    if not runs_file.exists():
        print(f"⚠️ 找不到 {runs_filename}")
        return set()

    all_runs = set()
    with open(runs_file, "r") as f:
        for line in f:
            run_id = line.strip()
            # 處理所有Run類型: SRR, ERR, DRR
            if run_id and (
                run_id.startswith("SRR")
                or run_id.startswith("ERR")
                or run_id.startswith("DRR")
            ):
                all_runs.add(run_id)

    return all_runs


def get_missing_samples():
    """獲取需要下載的樣本清單（606個runs.txt - NAS已有的 - 進度檔案已完成的）"""
    # 從runs.txt讀取所有SRR樣本
    all_runs = get_all_runs_from_file()

    print(f"📄 runs.txt中的SRR樣本: {len(all_runs)} 個")

    # 獲取進度管理器
    progress_mgr = ProgressManager()
    completed_from_progress = set(progress_mgr.progress.get("completed", []))
    
    print(f"📋 進度檔案記錄已完成: {len(completed_from_progress)} 個")

    # 獲取NAS已有的
    print(f"🔍 正在檢查NAS已有樣本...")
    nas_samples = get_nas_samples()

    print(f"✅ NAS已有: {len(nas_samples)} 個")

    # 合併已完成的樣本（NAS上的 + 進度檔案記錄的）
    completed_samples = nas_samples | completed_from_progress
    print(f"📊 總共已完成: {len(completed_samples)} 個（NAS + 進度檔案）")

    # 計算缺少的
    missing = all_runs - completed_samples

    print(f"📊 需要下載: {len(missing)} 個")

    return sorted(list(missing))


def download_sample(run_id, progress_mgr):
    """下載、解壓、上傳單個樣本 (每個線程獨立連接NAS)"""
    print(f"\n{'='*70}")
    print(f"🔄 處理樣本: {run_id}")
    print(f"{'='*70}")

    nas_uploader = NASUploader(
        NAS_CONFIG["host"],
        NAS_CONFIG["port"],
        NAS_CONFIG["username"],
        NAS_CONFIG["password"],
    )

    sra_file = SRA_TEMP_DIR / run_id / f"{run_id}.sra"
    fastq_1 = FASTQ_OUTPUT_DIR / f"{run_id}_1.fastq"
    fastq_2 = FASTQ_OUTPUT_DIR / f"{run_id}_2.fastq"

    try:
        # ==================== 建立獨立的NAS連接 ====================
        if not nas_uploader.connect():
            raise Exception("NAS連接失敗")
        print(f"    🔌 樣本 {run_id} 的獨立NAS連接已建立")
        # ==================== 步驟1: 下載 SRA ====================
        print(f"\n[1/5] 📥 下載SRA...", flush=True)
        
        # 檢查磁碟空間
        import shutil as shutil_disk
        disk_usage = shutil_disk.disk_usage(str(SRA_TEMP_DIR))
        free_gb = disk_usage.free / (1024**3)
        print(f"    💾 可用磁碟空間: {free_gb:.2f} GB", flush=True)
        
        # 如果空間不足，警告但不自動清理其他樣本的目錄（避免並行衝突）
        if free_gb < 50:
            print(f"    ⚠️  磁碟空間偏低: {free_gb:.2f} GB")
            print(f"    提示: 建議手動執行 cleanup_disk.py 清理殘留檔案")
        
        if free_gb < 10:
            raise Exception(f"磁碟空間不足: 僅剩 {free_gb:.2f} GB，請手動清理或增加磁碟空間")
        
        # 只清理當前樣本的舊目錄（避免誤刪其他執行緒的目錄）
        if sra_file.parent.exists():
            # 先清理所有臨時檔案和鎖檔
            for tmp_file in sra_file.parent.glob("*.tmp"):
                try:
                    tmp_file.unlink()
                    print(f"    🗑️  已刪除臨時檔: {tmp_file.name}")
                except:
                    pass
            for lock_file in sra_file.parent.glob("*.lock"):
                try:
                    lock_file.unlink()
                    print(f"    🗑️  已刪除鎖檔: {lock_file.name}")
                except:
                    pass
            
            # 然後刪除整個目錄
            shutil.rmtree(sra_file.parent)
            print(f"    🗑️  已刪除舊的 SRA 目錄: {sra_file.parent}")
        
        # 重新創建乾淨的目錄
        sra_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 確認目錄創建成功
        if not sra_file.parent.exists():
            raise Exception(f"無法創建目錄: {sra_file.parent}")
        
        # 檢查是否使用 aria2 加速下載
        use_aria2 = USE_ARIA2 and shutil.which("aria2c") is not None
        start_time = time.time()
        result = None
        
        if use_aria2:
            print(f"    🚀 使用 aria2 多連接加速下載（{ARIA2_CONNECTIONS} 連接）...")
            
            # 構建 SRA 下載 URL（嘗試多個鏡像）
            prefix = run_id[:6]
            mirrors = [
                f"https://sra-downloadb.be-md.ncbi.nlm.nih.gov/sos4/sra-pub-run-28/{prefix}/{run_id}/{run_id}.sra",
                f"https://sra-download.ncbi.nlm.nih.gov/traces/sra68/SRZ/{prefix}/{run_id}/{run_id}.sra",
                f"https://sra-pub-run-odp.s3.amazonaws.com/sra/{run_id}/{run_id}",
            ]
            
            # 嘗試每個鏡像直到成功
            download_success = False
            for mirror_idx, url in enumerate(mirrors, 1):
                print(f"    🌐 嘗試鏡像 {mirror_idx}/{len(mirrors)}")
                
                aria2_cmd = [
                    "aria2c",
                    f"--max-connection-per-server={ARIA2_CONNECTIONS}",
                    f"--split={ARIA2_CONNECTIONS}",
                    "--min-split-size=1M",
                    "--max-concurrent-downloads=1",
                    "--continue=true",
                    "--max-tries=5",
                    "--retry-wait=3",
                    "--timeout=60",
                    "--connect-timeout=30",
                    f"--dir={sra_file.parent}",
                    f"--out={sra_file.name}",
                    url
                ]
                
                try:
                    result = subprocess.run(
                        aria2_cmd, capture_output=True, text=True, timeout=PREFETCH_TIMEOUT
                    )
                    
                    if result.returncode == 0 and sra_file.exists():
                        download_success = True
                        print(f"    ✅ aria2 下載成功！")
                        break
                    else:
                        print(f"    ⚠️ 鏡像 {mirror_idx} 失敗，嘗試下一個...")
                        
                except subprocess.TimeoutExpired:
                    print(f"    ⚠️ 鏡像 {mirror_idx} 超時，嘗試下一個...")
                except Exception as e:
                    print(f"    ⚠️ 鏡像 {mirror_idx} 錯誤: {e}")
            
            # 如果 aria2 全部失敗，回退到 prefetch
            if not download_success:
                print(f"    ⚠️ aria2 所有鏡像都失敗，回退到 prefetch...")
                use_aria2 = False
        
        # 如果不使用 aria2 或 aria2 失敗，使用傳統 prefetch
        if not use_aria2:
            # 構建 prefetch 命令
            cmd = [
                PREFETCH_EXE,
                run_id,
                "--output-directory",
                str(SRA_TEMP_DIR),
                "--max-size",
                "100GB",
                "--force", "all",
                "--type", "sra",
                "--progress",
            ]
            
            # 嘗試啟用 Aspera 加速
            use_aspera = os.environ.get("USE_ASPERA", "yes").lower() in ["yes", "true", "1"]
            if use_aspera:
                pass  # prefetch 會自動偵測並使用 Aspera
            
            print(f"    執行指令: {' '.join(cmd)}")
            
            # 加入重試機制（最多 3 次）
            max_retries = 3
            retry_delay = 10
            
            for attempt in range(1, max_retries + 1):
                try:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=PREFETCH_TIMEOUT
                    )
                    
                    # 如果成功或非網路錯誤，跳出重試
                    if result.returncode == 0:
                        break
                        
                    # 檢查是否為網路/連接錯誤
                    error_msg = result.stderr.lower()
                    is_network_error = any(keyword in error_msg for keyword in [
                        "connection failed", "timeout", "network", "failed to download"
                    ])
                    
                    if is_network_error and attempt < max_retries:
                        print(f"    ⚠️ 網路錯誤，{retry_delay}秒後重試 ({attempt}/{max_retries})...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        break
                        
                except subprocess.TimeoutExpired:
                    if attempt < max_retries:
                        print(f"    ⚠️ 超時，{retry_delay}秒後重試 ({attempt}/{max_retries})...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise
        
        elapsed = time.time() - start_time

        # 給檔案系統一點時間同步（Docker volume 可能需要）
        time.sleep(2)

        # 如果檔案還沒有出現，嘗試輪詢並搜尋可能的位置（例如 NCBI cache）
        file_exists = sra_file.exists()
        postcheck_wait = int(os.environ.get("PREFETCH_POSTCHECK_WAIT", 120))
        poll_interval = 2
        checked_alt = []

        if not file_exists and result.returncode == 0:
            print(f"    ⚠️ Prefetch 返回成功但檔案尚未可見，開始輪詢最多 {postcheck_wait}s...")
            t0 = time.time()
            while time.time() - t0 < postcheck_wait:
                if sra_file.exists():
                    file_exists = True
                    break
                # 搜尋同目錄下的候選檔案
                if sra_file.parent.exists():
                    for f in sra_file.parent.iterdir():
                        try:
                            if f.is_file():
                                name = f.name.lower()
                                # 常見情況: 檔名包含 run id 或副檔名為 .sra
                                if run_id.lower() in name or name.endswith(".sra"):
                                    # 嘗試將它移到預期位置（如果不同）
                                    try:
                                        if f.resolve() != sra_file.resolve():
                                            print(f"    🔁 發現候選檔案，嘗試重命名: {f} -> {sra_file}")
                                            f.rename(sra_file)
                                    except Exception:
                                        # 解析路徑可能失敗，改用 copy
                                        try:
                                            shutil.copy2(f, sra_file)
                                        except Exception:
                                            pass
                                    file_exists = sra_file.exists()
                                    break
                        except Exception:
                            continue
                # 搜尋 NCBI 預設快取位置
                try:
                    home_cache = Path.home() / ".ncbi" / "public" / "sra"
                    if home_cache.exists() and home_cache not in checked_alt:
                        checked_alt.append(home_cache)
                        for f in home_cache.rglob("*"):
                            if f.is_file() and run_id.lower() in f.name.lower():
                                print(f"    🔎 在 NCBI cache 發現候選: {f}，複製到 {sra_file}")
                                try:
                                    shutil.copy2(f, sra_file)
                                except Exception:
                                    pass
                                file_exists = sra_file.exists()
                                break
                except Exception:
                    pass

                if file_exists:
                    break
                time.sleep(poll_interval)

        # 檢查 prefetch 是否成功（檢查檔案而非目錄，避免誤判）
        if result.returncode != 0 or not file_exists:
            # 輸出完整錯誤訊息以便除錯
            print(f"    ❌ Prefetch返回碼: {result.returncode}")
            print(f"    📋 STDOUT: {result.stdout}")
            print(f"    📋 STDERR: {result.stderr}")
            print(f"    📁 檔案存在: {file_exists}")
            print(f"    📂 預期路徑: {sra_file}")

            # 列出實際下載的內容（如果目錄存在）
            if sra_file.parent.exists():
                actual_files = list(sra_file.parent.rglob("*"))
                print(f"    📂 實際檔案: {[str(f) for f in actual_files[:20]]}")

            # 檢查是否為路徑問題（可能是並行衝突）
            error_msg = result.stderr.lower()
            if "path not found" in error_msg or "cannot openfilewrite" in error_msg:
                raise Exception(f"Prefetch路徑錯誤（可能是並行衝突或權限問題）: {result.stderr}")

            # 檢查是否為樣本不存在的錯誤
            if "item not found" in error_msg or "cannot resolve" in error_msg:
                raise Exception(f"樣本不存在於SRA數據庫（可能已下架）: {run_id}")

            # 檢查是否僅為參考序列下載失敗（但 SRA 本身已下載成功）
            is_refseq_only_error = (
                "failed to download" in error_msg and 
                "refseq" in error_msg and 
                sra_file.exists()
            )
            
            if is_refseq_only_error:
                print(f"    ⚠️ 參考序列下載失敗，但 SRA 本身已下載完成，繼續處理...")
                # 不拋出異常，讓流程繼續
            elif result.returncode == 0 and not file_exists:
                # 如果返回碼是0但檔案不存在，可能是網路問題或檔案格式問題
                raise Exception(f"Prefetch顯示成功但檔案不存在（可能是網路中斷或格式錯誤）。STDOUT: {result.stdout[:200]}")
            else:
                raise Exception(f"Prefetch失敗: {result.stderr}")

        if not sra_file.exists():
            raise Exception(f"SRA檔案不存在: {sra_file}")

        sra_size = sra_file.stat().st_size / (1024**3)
        print(f"✅ Prefetch完成 ({elapsed:.1f}秒, {sra_size:.2f} GB)")

        # ==================== 步驟1.5: 驗證SRA檔案完整性 ====================
        print(f"\n[1.5/5] 🔍 驗證SRA檔案完整性...", flush=True)
        
        cmd_validate = [
            VDB_VALIDATE_EXE,
            str(sra_file)
        ]
        
        start_time = time.time()
        result_validate = subprocess.run(
            cmd_validate, capture_output=True, text=True, timeout=1800  # 30分鐘超時
        )
        elapsed_validate = time.time() - start_time
        
        if result_validate.returncode != 0:
            # 校驗失敗，表示SRA檔案不完整或損壞
            print(f"    ❌ SRA檔案校驗失敗 ({elapsed_validate:.1f}秒)")
            print(f"    錯誤訊息: {result_validate.stderr[:200]}")
            
            # 刪除損壞的SRA檔案
            if sra_file.parent.exists():
                shutil.rmtree(sra_file.parent)
                print(f"    🗑️  已刪除損壞的SRA檔案: {sra_file.parent}")
            
            raise Exception(f"SRA檔案完整性校驗失敗，檔案可能下載不完整 (實際大小: {sra_size:.2f} GB)")
        
        print(f"✅ SRA檔案校驗通過 ({elapsed_validate:.1f}秒)")

        # ==================== 步驟2: Fasterq-dump ====================
        print(f"\n[2/5] 🔓 解壓FASTQ...", flush=True)
        FASTQ_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        cmd = [
            FASTERQ_DUMP_EXE,  # 使用配置中的路徑
            str(sra_file),
            "-e",
            str(FASTERQ_THREADS),
            "-O",
            str(FASTQ_OUTPUT_DIR),
            "-t",
            str(TMP_DIR),
            "--split-files",  # 分離成 _1.fastq 和 _2.fastq
            "-f",
        ]

        start_time = time.time()
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=FASTERQ_TIMEOUT
        )
        elapsed = time.time() - start_time

        if result.returncode != 0:
            # 如果解壓失敗，很有可能是SRA檔案損壞，刪除它以便重試
            if sra_file.parent.exists():
                shutil.rmtree(sra_file.parent)
                print(f"    ⚠️  偵測到解壓失敗，已刪除損壞的SRA目錄: {sra_file.parent}")
            raise Exception(f"Fasterq-dump失敗: {result.stderr}")

        # 增加對單端(Single-End)和雙端(Paired-End)的檢查
        is_paired = fastq_1.exists() and fastq_2.exists()
        
        # 檢查是否至少有一個 FASTQ 檔案存在
        # Note: This logic is simplified. A more robust check might be needed if single-end files don't follow {run_id}.fastq pattern
        if not is_paired and not next(FASTQ_OUTPUT_DIR.glob(f"{run_id}*.fastq"), None):
            # 如果SRA檔案存在，則刪除它，因為它可能已損壞
            if sra_file.parent.exists():
                shutil.rmtree(sra_file.parent)
                print(f"    ⚠️  解壓後未生成任何FASTQ檔案，已刪除可能損壞的SRA目錄: {sra_file.parent}")
            raise Exception(f"FASTQ檔案不完整或未生成")

        fastq_files_to_upload = []
        if is_paired:
            fastq_files_to_upload.extend([fastq_1, fastq_2])
            total_size = (fastq_1.stat().st_size + fastq_2.stat().st_size) / (1024**3)
            print(f"✅ 解壓完成 (雙端, {elapsed:.1f}秒, {total_size:.2f} GB)")
        else:
            # 處理單端情況或檔名不為 _1/_2 的情況
            single_fastq = next(FASTQ_OUTPUT_DIR.glob(f"{run_id}*.fastq"), None)
            if single_fastq and single_fastq.exists():
                fastq_files_to_upload.append(single_fastq)
                total_size = single_fastq.stat().st_size / (1024**3)
                print(f"✅ 解壓完成 (單端, {elapsed:.1f}秒, {total_size:.2f} GB)")
            else:
                # This case should be caught by the check above, but as a fallback
                if sra_file.parent.exists():
                    shutil.rmtree(sra_file.parent)
                raise Exception("找不到解壓後的FASTQ檔案，已清理SRA檔案以便重試")

        # ==================== 步驟2.5: 立即刪除SRA檔案釋放空間 ====================
        print(f"\n[2.5/5] 🗑️  刪除SRA檔案釋放空間...", flush=True)
        if sra_file.parent.exists():
            sra_size_gb = sra_file.stat().st_size / (1024**3) if sra_file.exists() else 0
            shutil.rmtree(sra_file.parent)
            print(f"    ✅ 已刪除SRA檔案 (釋放 {sra_size_gb:.2f} GB): {sra_file.parent}")

        # ==================== 步驟3: 上傳FASTQ到NAS ====================
        print(f"\n[3/5] 📤 上傳FASTQ到NAS...", flush=True)

        for fastq_file in fastq_files_to_upload:
            remote_path = f"{NAS_CONFIG['fastq_path']}/{fastq_file.name}"
            if not nas_uploader.upload_file(fastq_file, remote_path, show_progress=True):
                raise Exception(f"FASTQ上傳失敗: {fastq_file.name}")

        # ==================== 步驟4: 上傳SRA到NAS（已停用） ====================
        # 註解：由於 SRA 檔案上傳經常失敗且不是必需的（FASTQ 已足夠），因此停用此步驟
        # print(f"\n[4/5] 📤 上傳SRA到NAS...")
        # sra_remote_dir = f"{NAS_CONFIG['sra_path']}/{run_id}"
        # sra_remote_path = f"{sra_remote_dir}/{sra_file.name}"
        # nas_uploader.create_remote_dir(sra_remote_dir)
        # if not nas_uploader.upload_file(sra_file, sra_remote_path, show_progress=True):
        #     raise Exception("SRA上傳失敗")
        
        print(f"\n[4/5] ⏭️  跳過SRA上傳（FASTQ已足夠）", flush=True)

        # ==================== 步驟5: 清理本地檔案 ====================
        print(f"\n[5/5] 🧹 清理本地檔案...", flush=True)

        # 刪除FASTQ
        for f in fastq_files_to_upload:
            if f.exists():
                f.unlink()
                print(f"    ✅ 已刪除: {f.name}")

        # SRA 已在步驟 2.5 刪除，這裡不需要再刪除
        # 但保留檢查以防萬一
        if sra_file.parent.exists():
            shutil.rmtree(sra_file.parent)
            print(f"    ⚠️  發現殘留的SRA目錄，已刪除: {sra_file.parent}")

        # 標記為完成
        progress_mgr.mark_completed(run_id)

        print(f"\n✅ 樣本完成: {run_id}")
        return True

    except Exception as e:
        print(f"\n❌ 樣本失敗: {run_id}")
        print(f"   錯誤: {e}")

        # 清理失敗的檔案
        try:
            # Re-define paths for cleanup in case of early failure
            fastq_1 = FASTQ_OUTPUT_DIR / f"{run_id}_1.fastq"
            fastq_2 = FASTQ_OUTPUT_DIR / f"{run_id}_2.fastq"
            sra_file_parent = SRA_TEMP_DIR / run_id

            # Clean up any partial fastq files
            for f in list(FASTQ_OUTPUT_DIR.glob(f"{run_id}*.fastq")):
                if f.exists():
                    f.unlink()
            
            # Clean up SRA directory
            if sra_file_parent.exists():
                shutil.rmtree(sra_file_parent)
        except Exception as cleanup_error:
            print(f"    ⚠️ 清理失敗檔案時發生錯誤: {cleanup_error}")

        # 標記為失敗
        # Extract step from error message if possible
        error_str = str(e).lower()
        
        # 區分不同類型的失敗
        if "樣本不存在" in error_str or "item not found" in error_str:
            step = "sample_not_found"  # 樣本在數據庫中不存在
        else:
            step = "unknown_process"
        if "prefetch" in error_str:
            step = "prefetch"
        elif "fasterq-dump" in error_str or "fastq" in error_str:
            step = "dumping"
        elif "upload" in error_str:
            step = "upload"
        elif "nas" in error_str:
            step = "nas_connect"
        
        progress_mgr.mark_failed(run_id, step, str(e))

        return False
    
    finally:
        # 無論成功或失敗，都確保斷開NAS連接
        if nas_uploader and nas_uploader.sftp:
            nas_uploader.disconnect()
            print(f"    🔌 樣本 {run_id} 的獨立NAS連接已關閉")


# ==================== 主程序 ====================


def main():
    print("=" * 80)
    print("🚀 自動化下載、解壓、上傳系統")
    print("=" * 80)
    print(f"\n系統配置:")
    print(f"  CPU優化: I7-11代 (8核16線程)")
    print(f"  並行數: {MAX_WORKERS} 個樣本同時處理")
    print(f"  每個樣本解壓線程: {FASTERQ_THREADS}")
    print(f"  總解壓線程數: {MAX_WORKERS * FASTERQ_THREADS}")
    print(f"  系統預留: 2線程")

    # 創建必要目錄（更安全的方式）
    try:
        SRA_TEMP_DIR.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        # 目錄已存在但可能是掛載點，檢查是否可寫
        if not SRA_TEMP_DIR.exists():
            raise Exception(f"無法創建目錄: {SRA_TEMP_DIR}")
    
    try:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        if not TMP_DIR.exists():
            raise Exception(f"無法創建目錄: {TMP_DIR}")
    
    try:
        FASTQ_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        if not FASTQ_OUTPUT_DIR.exists():
            raise Exception(f"無法創建目錄: {FASTQ_OUTPUT_DIR}")

    # 移除主函數中的NAS連接，改為在每個線程中獨立創建
    # print(f"\n🔌 正在連接NAS...")
    # nas_uploader = NASUploader(...)
    # if not nas_uploader.connect():
    #     print("❌ NAS連接失敗，程序終止")
    #     return
    # print("✅ NAS連接成功")

    # 初始化進度管理
    progress_mgr = ProgressManager()

    # 獲取缺少的樣本
    print(f"\n🔍 正在檢查缺少的樣本...")
    missing_samples = get_missing_samples()

    print(f"\n📊 統計:")
    print(f"  需要下載: {len(missing_samples)} 個樣本")
    print(f"  NAS路徑:")
    print(f"    FASTQ: {NAS_CONFIG['fastq_path']}")
    print(f"    SRA: {NAS_CONFIG['sra_path']}")

    if not missing_samples:
        print("\n✅ 所有樣本都已在NAS上！")
        # nas_uploader.disconnect() # No longer needed here
        return

    # 確認開始
    print(f"\n" + "=" * 80)
    print(f"準備開始下載 {len(missing_samples)} 個樣本")
    print(f"預估時間: {len(missing_samples) / MAX_WORKERS * 0.5:.1f} - {len(missing_samples) / MAX_WORKERS * 1.5:.1f} 小時")
    print(f"=" * 80)

    # 如果在非互動式環境中（例如 Docker），則跳過等待
    if not sys.stdout.isatty() and os.environ.get("DEBIAN_FRONTEND") == "noninteractive":
        print("\n在非互動式環境中，自動開始...")
    else:
        input("\n按Enter開始，或Ctrl+C取消...")

    # 開始處理
    start_time = time.time()
    success_count = 0
    fail_count = 0

    print(f"\n🚀 開始處理...")

    # 使用 tqdm 進度條
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 將 progress_mgr 傳遞給每個任務，不再傳遞共享的 nas_uploader
        futures = {
            executor.submit(download_sample, run_id, progress_mgr): run_id
            for run_id in missing_samples
        }

        # 創建進度條
        with tqdm(total=len(missing_samples), desc="總體進度", unit="樣本", 
                  ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
            
            for future in as_completed(futures):
                run_id = futures[future]
                try:
                    if future.result():
                        success_count += 1
                        pbar.set_postfix({"成功": success_count, "失敗": fail_count})
                    else:
                        fail_count += 1
                        pbar.set_postfix({"成功": success_count, "失敗": fail_count})
                except Exception as e:
                    print(f"\n❌ 執行錯誤 {run_id}: {e}")
                    fail_count += 1
                    pbar.set_postfix({"成功": success_count, "失敗": fail_count})
                
                # 更新進度條
                pbar.update(1)

    # 完成
    elapsed = time.time() - start_time

    print("\n" + "=" * 80)
    print("✅ 所有任務完成")
    print("=" * 80)
    print(f"總耗時: {elapsed/3600:.2f} 小時")
    print(f"成功: {success_count} 個")
    print(f"失敗: {fail_count} 個")

    # 顯示不存在的樣本列表
    if fail_count > 0:
        failed_list = progress_mgr.progress.get("failed", [])
        not_found_samples = [
            f["run_id"] for f in failed_list 
            if f.get("step") == "sample_not_found"
        ]
        
        if not_found_samples:
            print(f"\n⚠️  以下 {len(not_found_samples)} 個樣本在SRA數據庫中不存在（可能已下架）:")
            for sample in not_found_samples:
                print(f"   - {sample}")
            print(f"\n   這些樣本將被跳過，是正常現象。")
        
        # 顯示其他真正的錯誤
        real_errors = [
            f for f in failed_list 
            if f.get("step") != "sample_not_found"
        ]
        
        if real_errors:
            print(f"\n❌ 以下 {len(real_errors)} 個樣本發生真正的錯誤:")
            for error in real_errors[:10]:  # 最多顯示10個
                print(f"   - {error['run_id']}: {error.get('step', 'unknown')}")
                print(f"     {error.get('error', '')[:100]}")

    # nas_uploader.disconnect() # No longer needed here


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用戶中斷程序")
    except Exception as e:
        print(f"\n❌ 程序錯誤: {e}")
        import traceback

        traceback.print_exc()
