import sys
import os
from pathlib import Path
import shutil

# 導入配置，以便使用其中的路徑變數
try:
    from config import PREFETCH_EXE, FASTERQ_DUMP_EXE, SRA_TOOLKIT_DIR
except ImportError:
    print("❌ 無法導入 config.py。請確保檔案存在且無語法錯誤。")
    sys.exit(1)

def check_sra_toolkit():
    """
    檢查 SRA Toolkit 是否可用。
    它會檢查 config.py 中定義的路徑或系統 PATH。
    """
    print("1️⃣  檢查 SRA Toolkit...")

    # 檢查 prefetch
    prefetch_path = shutil.which(PREFETCH_EXE)
    if not prefetch_path:
        print(f"   - ❌ 'prefetch' 未找到。")
        print(f"     預期路徑: {PREFETCH_EXE}")
        return False
    print(f"   - ✅ 'prefetch' 已找到: {prefetch_path}")

    # 檢查 fasterq-dump
    fasterq_dump_path = shutil.which(FASTERQ_DUMP_EXE)
    if not fasterq_dump_path:
        print(f"   - ❌ 'fasterq-dump' 未找到。")
        print(f"     預期路徑: {FASTERQ_DUMP_EXE}")
        return False
    print(f"   - ✅ 'fasterq-dump' 已找到: {fasterq_dump_path}")

    return True

def check_python_packages():
    """檢查必要的 Python 套件"""
    print("\n2️⃣  檢查 Python 套件...")
    try:
        import paramiko
        import tqdm
        print("   - ✅ 'paramiko' 和 'tqdm' 已安裝。")
        return True
    except ImportError as e:
        print(f"   - ❌ 缺少套件: {e.name}")
        print("     請執行: pip install -r requirements.txt")
        return False

def main():
    print("=" * 70)
    print("🔍 快速環境檢查 (Docker-Ready Version)")
    print("=" * 70)

    sra_ok = check_sra_toolkit()
    pkg_ok = check_python_packages()

    print("-" * 70)

    if sra_ok and pkg_ok:
        print("✅ 環境檢查通過！")
        return 0
    else:
        print("❌ 環境檢查失敗，請解決上述問題。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
