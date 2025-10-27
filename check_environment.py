"""
環境檢查腳本 - 確保所有依賴都已安裝
"""

import sys
import subprocess
import os
from pathlib import Path

# 設定 UTF-8 編碼 (Windows)
if sys.platform == "win32":
    try:
        # 設定控制台為 UTF-8
        os.system("chcp 65001 >nul 2>&1")
    except:
        pass


def check_python():
    """檢查Python版本"""
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("⚠️ 警告: 建議使用Python 3.7+")
        return False
    return True


def check_module(module_name):
    """檢查Python模組"""
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
        return True
    except ImportError:
        print(f"❌ {module_name} 未安裝")
        return False


def check_sra_toolkit():
    """檢查SRA Toolkit"""
    # 檢查本地 sratoolkit 資料夾（在 data_collector 目錄）
    parent_dir = Path.cwd().parent  # 從 auto_downloader 回到 data_collector
    local_bin = parent_dir / "sratoolkit.3.2.1-win64" / "bin"

    print(f"檢查路徑: {local_bin}")

    if not local_bin.exists():
        print(f"❌ SRA Toolkit 未找到")
        print(f"   請執行 SETUP.bat 自動下載")
        return False

    # 檢查關鍵工具
    tools = {
        "prefetch.exe": "下載工具",
        "fasterq-dump.exe": "解壓工具",
        "vdb-validate.exe": "驗證工具",
    }

    all_found = True
    print(f"✅ 找到 SRA Toolkit 目錄")

    for tool, desc in tools.items():
        exe = local_bin / tool
        if exe.exists():
            print(f"  ✅ {tool} ({desc})")
        else:
            print(f"  ❌ {tool} ({desc}) 未找到")
            all_found = False

    return all_found


def check_disk_space():
    """檢查磁碟空間"""
    try:
        import shutil

        d_drive = Path("D:/")
        if d_drive.exists():
            stat = shutil.disk_usage("D:/")
            free_gb = stat.free / (1024**3)
            print(f"✅ D槽可用空間: {free_gb:.2f} GB")
            if free_gb < 200:
                print(f"⚠️ 警告: D槽可用空間不足200GB，建議清理")
                return False
            return True
        else:
            print("⚠️ D槽不存在")
            return False
    except Exception as e:
        print(f"❌ 檢查磁碟空間失敗: {e}")
        return False


def check_nas_connection():
    """檢查NAS連接"""
    try:
        import paramiko

        print("正在連接NAS...")
        t = paramiko.Transport(("bioailab.synology.me", 22))
        t.banner_timeout = 30  # 增加超時時間
        t.window_size = 2147483647
        t.packetizer.REKEY_BYTES = pow(2, 40)
        t.packetizer.REKEY_PACKETS = pow(2, 40)
        t.connect(username="bioailab", password="Ncueailab403")
        sftp = paramiko.SFTPClient.from_transport(t)

        # 測試訪問
        try:
            sftp.listdir("/Bee_metagenomics/Bee_metagenomics/fastq_data")
            print("✅ NAS連接正常")
            result = True
        except:
            print("❌ NAS目錄訪問失敗")
            result = False

        sftp.close()
        t.close()
        return result

    except Exception as e:
        print(f"❌ NAS連接失敗: {e}")
        return False


def main():
    print("=" * 70)
    print("🔍 環境檢查")
    print("=" * 70)

    results = []
    all_passed = True

    # Python檢查
    print("\n[1/5] Python環境")
    results.append(check_python())

    # Python模組檢查
    print("\n[2/5] Python套件")
    module_ok = check_module("paramiko")
    results.append(module_ok)
    if not module_ok:
        print("   安裝: pip install paramiko")

    # SRA Toolkit檢查
    print("\n[3/5] SRA Toolkit")
    sra_ok = check_sra_toolkit()
    results.append(sra_ok)

    # 磁碟空間檢查
    print("\n[4/5] 磁碟空間")
    results.append(check_disk_space())

    # NAS連接檢查
    print("\n[5/5] NAS連接")
    results.append(check_nas_connection())

    # 總結
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)

    if all(results):
        print(f"✅ 所有檢查通過！({passed}/{total})")
        print("\n🚀 系統準備就緒！")
        return 0  # 成功
    else:
        print(f"⚠️  {passed}/{total} 項檢查通過，請解決上述問題")
        print("\n📝 解決方案:")
        if not results[1]:  # paramiko
            print("   • 安裝套件: pip install paramiko")
        if not results[2]:  # SRA Toolkit
            print("   • 執行 SETUP.bat 自動下載 SRA Toolkit")
            print("   • 或執行 一鍵安裝_SRA_Toolkit.bat")
        if not results[3]:  # 磁碟空間
            print("   • 清理 D 槽空間（建議至少 200GB）")
        if not results[4]:  # NAS
            print("   • 檢查網路連線和 NAS 憑證")
        print("=" * 70)
        return 1  # 失敗


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ 檢查中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 檢查錯誤: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
