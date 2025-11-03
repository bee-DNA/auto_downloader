#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查並修復 NAS 上的 FASTQ 檔案
- 對照 runs.txt 檢查缺失的樣本
- 刪除多餘的檔案
- 確保所有樣本都有成對的 _1.fastq 和 _2.fastq
- 標記異常檔案（只有單個檔案、檔案大小異常等）
"""

import sys
from pathlib import Path
from collections import defaultdict
import posixpath

# 導入配置
try:
    from config import *
    from nas_uploader import NASUploader
except ImportError as e:
    print(f"❌ 導入失敗: {e}")
    print("請確保 config.py 和 nas_uploader.py 在同一目錄")
    sys.exit(1)

# NAS 設置
NAS_CONFIG = {
    "host": NAS_HOST,
    "port": NAS_PORT,
    "username": NAS_USER,
    "password": NAS_PASS,
    "fastq_path": NAS_FASTQ_PATH,
    "sra_path": NAS_SRA_PATH,
}


def read_runs_file():
    """讀取 runs.txt 獲取所有應該存在的樣本 ID"""
    runs_file = Path(RUNS_FILE)
    if not runs_file.exists():
        print(f"❌ 找不到 {RUNS_FILE}")
        sys.exit(1)
    
    expected_runs = set()
    with open(runs_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                expected_runs.add(line)
    
    print(f"📋 runs.txt 中有 {len(expected_runs)} 個樣本")
    return expected_runs


def list_nas_fastq_files(nas_uploader):
    """列出 NAS 上所有的 FASTQ 檔案"""
    print(f"\n🔍 掃描 NAS 上的 FASTQ 檔案...")
    
    try:
        # 列出遠端目錄
        remote_path = NAS_CONFIG['fastq_path']
        files = nas_uploader.sftp.listdir(remote_path)
        
        # 過濾出 .fastq 檔案
        fastq_files = [f for f in files if f.endswith('.fastq')]
        
        print(f"✅ 找到 {len(fastq_files)} 個 FASTQ 檔案")
        return fastq_files
    
    except Exception as e:
        print(f"❌ 列出 NAS 檔案失敗: {e}")
        return []


def analyze_fastq_files(fastq_files):
    """分析 FASTQ 檔案，按樣本分組"""
    samples = defaultdict(list)
    other_files = []  # _3, _4 等其他讀段檔案（保留，不處理）
    
    for filename in fastq_files:
        # 解析檔名：run_id_1.fastq 或 run_id_2.fastq
        if filename.endswith('_1.fastq'):
            run_id = filename[:-8]  # 移除 _1.fastq
            samples[run_id].append('_1')
        elif filename.endswith('_2.fastq'):
            run_id = filename[:-8]  # 移除 _2.fastq
            samples[run_id].append('_2')
        elif filename.endswith('_3.fastq') or filename.endswith('_4.fastq'):
            # _3, _4 等其他讀段，忽略（保留在 NAS 上，不處理）
            other_files.append(filename)
        else:
            # 真正的異常檔名（不符合 *_N.fastq 格式）
            samples['__INVALID__'].append(filename)
    
    # 顯示其他讀段檔案資訊
    if other_files:
        print(f"\nℹ️  發現 {len(other_files)} 個其他讀段檔案（_3, _4 等），將保留不處理")
    
    return samples


def get_file_size(nas_uploader, remote_file_path):
    """獲取遠端檔案大小"""
    try:
        stat = nas_uploader.sftp.stat(remote_file_path)
        return stat.st_size
    except Exception:
        return -1


def verify_and_fix():
    """主要檢查和修復流程"""
    print("=" * 80)
    print("🔍 FASTQ 檔案檢查與修復工具")
    print("=" * 80)
    
    # 1. 讀取預期的樣本列表
    expected_runs = read_runs_file()
    
    # 2. 連接 NAS
    print(f"\n🔌 連接 NAS...")
    nas_uploader = NASUploader(
        host=NAS_CONFIG['host'],
        port=NAS_CONFIG['port'],
        username=NAS_CONFIG['username'],
        password=NAS_CONFIG['password']
    )
    
    if not nas_uploader.connect():
        print("❌ NAS 連接失敗")
        sys.exit(1)
    
    print("✅ NAS 連接成功")
    
    try:
        # 3. 列出 NAS 上的 FASTQ 檔案
        fastq_files = list_nas_fastq_files(nas_uploader)
        
        # 4. 分析檔案
        samples = analyze_fastq_files(fastq_files)
        
        # 5. 檢查結果
        print(f"\n{'='*80}")
        print("📊 檢查結果")
        print(f"{'='*80}")
        
        complete_samples = []  # 有 _1 和 _2 的樣本
        incomplete_samples = []  # 只有 _1 或 _2 的樣本
        missing_samples = []  # runs.txt 中有但 NAS 上沒有的
        extra_samples = []  # NAS 上有但 runs.txt 中沒有的
        invalid_files = samples.get('__INVALID__', [])
        
        # 檢查每個樣本
        for run_id in expected_runs:
            if run_id not in samples:
                missing_samples.append(run_id)
            elif set(samples[run_id]) == {'_1', '_2'}:
                complete_samples.append(run_id)
            else:
                incomplete_samples.append((run_id, samples[run_id]))
        
        # 檢查多餘的樣本
        for run_id in samples:
            if run_id != '__INVALID__' and run_id not in expected_runs:
                extra_samples.append(run_id)
        
        # 6. 顯示統計
        print(f"\n✅ 完整樣本（有 _1 和 _2）: {len(complete_samples)}")
        print(f"⚠️  不完整樣本（缺少 _1 或 _2）: {len(incomplete_samples)}")
        print(f"❌ 缺失樣本（runs.txt 有但 NAS 沒有）: {len(missing_samples)}")
        print(f"🗑️  多餘樣本（NAS 有但 runs.txt 沒有）: {len(extra_samples)}")
        print(f"⚠️  異常檔名: {len(invalid_files)}")
        
        # 7. 詳細報告
        if incomplete_samples:
            print(f"\n⚠️  不完整樣本列表:")
            for run_id, parts in incomplete_samples[:20]:
                print(f"   - {run_id}: 只有 {parts}")
            if len(incomplete_samples) > 20:
                print(f"   ... 還有 {len(incomplete_samples) - 20} 個")
        
        if missing_samples:
            print(f"\n❌ 缺失樣本列表:")
            for run_id in missing_samples[:20]:
                print(f"   - {run_id}")
            if len(missing_samples) > 20:
                print(f"   ... 還有 {len(missing_samples) - 20} 個")
        
        if extra_samples:
            print(f"\n🗑️  多餘樣本列表:")
            for run_id in extra_samples[:20]:
                parts = samples[run_id]
                print(f"   - {run_id}: {parts}")
            if len(extra_samples) > 20:
                print(f"   ... 還有 {len(extra_samples) - 20} 個")
        
        if invalid_files:
            print(f"\n⚠️  異常檔名列表:")
            for filename in invalid_files[:20]:
                print(f"   - {filename}")
            if len(invalid_files) > 20:
                print(f"   ... 還有 {len(invalid_files) - 20} 個")
        
        # 8. 檢查檔案大小異常
        print(f"\n🔍 檢查檔案大小異常...")
        size_issues = []
        remote_base = NAS_CONFIG['fastq_path']
        
        for run_id in complete_samples[:50]:  # 抽查前 50 個
            file_1 = posixpath.join(remote_base, f"{run_id}_1.fastq")
            file_2 = posixpath.join(remote_base, f"{run_id}_2.fastq")
            
            size_1 = get_file_size(nas_uploader, file_1)
            size_2 = get_file_size(nas_uploader, file_2)
            
            # 檢查檔案大小（成對的檔案大小不應相差太大）
            if size_1 > 0 and size_2 > 0:
                ratio = max(size_1, size_2) / min(size_1, size_2)
                if ratio > 2.0:  # 大小相差超過 2 倍可能異常
                    size_issues.append((run_id, size_1, size_2))
            elif size_1 <= 0 or size_2 <= 0:
                size_issues.append((run_id, size_1, size_2))
        
        if size_issues:
            print(f"⚠️  發現 {len(size_issues)} 個大小異常的樣本:")
            for run_id, size_1, size_2 in size_issues[:10]:
                print(f"   - {run_id}: _1={size_1/1024/1024:.1f}MB, _2={size_2/1024/1024:.1f}MB")
        
        # 9. 詢問是否執行修復
        print(f"\n{'='*80}")
        print("🔧 修復選項")
        print(f"{'='*80}")
        
        actions = []
        
        if missing_samples:
            actions.append(f"1. 下載 {len(missing_samples)} 個缺失樣本")
        
        if extra_samples or invalid_files:
            total_delete = len(extra_samples) * 2 + len(invalid_files)  # 每個樣本有 _1 和 _2
            actions.append(f"2. 刪除 {total_delete} 個多餘/異常檔案")
        
        if incomplete_samples:
            actions.append(f"3. 重新下載 {len(incomplete_samples)} 個不完整樣本")
        
        if not actions:
            print("✅ 沒有需要修復的問題！所有檔案都正確。")
            return
        
        print("\n需要執行的操作:")
        for action in actions:
            print(f"   {action}")
        
        # 生成修復腳本
        print(f"\n📝 生成修復報告...")
        
        # 生成缺失樣本列表（用於重新下載）
        if missing_samples or incomplete_samples:
            fix_runs_file = Path("runs_to_fix.txt")
            with open(fix_runs_file, 'w') as f:
                for run_id in sorted(missing_samples):
                    f.write(f"{run_id}\n")
                for run_id, _ in incomplete_samples:
                    f.write(f"{run_id}\n")
            print(f"✅ 已生成 {fix_runs_file}（{len(missing_samples) + len(incomplete_samples)} 個樣本需要重新下載）")
        
        # 生成刪除列表
        if extra_samples or invalid_files or incomplete_samples:
            delete_list_file = Path("files_to_delete.txt")
            with open(delete_list_file, 'w') as f:
                # 多餘的樣本
                for run_id in extra_samples:
                    for suffix in samples[run_id]:
                        f.write(f"{run_id}{suffix}.fastq\n")
                # 異常檔名
                for filename in invalid_files:
                    f.write(f"{filename}\n")
                # 不完整的樣本
                for run_id, parts in incomplete_samples:
                    for suffix in parts:
                        f.write(f"{run_id}{suffix}.fastq\n")
            
            total_to_delete = sum([len(samples[r]) for r in extra_samples]) + len(invalid_files) + sum([len(p) for _, p in incomplete_samples])
            print(f"✅ 已生成 {delete_list_file}（{total_to_delete} 個檔案需要刪除）")
        
        print(f"\n{'='*80}")
        print("📋 後續步驟")
        print(f"{'='*80}")
        print("\n1. 刪除多餘/異常檔案:")
        print("   python delete_extra_files.py")
        print("\n2. 重新下載缺失/不完整樣本:")
        print("   # 將 runs_to_fix.txt 複製為 runs.txt")
        print("   # 或修改 complete_downloader.py 的 RUNS_FILE 設定")
        print("   docker run --rm -v \"${pwd}\\data:/app/data\" -e RUNS_FILE=runs_to_fix.txt auto_downloader")
        
    finally:
        nas_uploader.disconnect()
        print(f"\n✅ NAS 連接已關閉")


if __name__ == "__main__":
    try:
        verify_and_fix()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用戶中斷程序")
    except Exception as e:
        print(f"\n❌ 程序錯誤: {e}")
        import traceback
        traceback.print_exc()
