"""
完整的環境驗證和問題修復腳本
"""

import json
from pathlib import Path
import sys


def check_json_file():
    """檢查並修復 JSON 檔案"""
    print("=" * 70)
    print("📋 檢查 JSON 檔案")
    print("=" * 70)

    json_file = Path("download_progress.json")

    if not json_file.exists():
        print("❌ download_progress.json 不存在")
        return False

    # 檢查檔案大小
    file_size = json_file.stat().st_size
    print(f"檔案大小: {file_size:,} bytes")

    if file_size == 0:
        print("❌ 檔案為空!")
        return False

    # 檢查 JSON 格式
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"✅ JSON 格式正確")
        print(f"   已完成: {len(data.get('completed', []))} 個")
        print(f"   失敗: {len(data.get('failed', []))} 個")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式錯誤: {e}")
        return False


def check_sra_toolkit():
    """檢查 SRA Toolkit"""
    print("\n" + "=" * 70)
    print("🔧 檢查 SRA Toolkit 配置")
    print("=" * 70)

    try:
        from config import PREFETCH_EXE, FASTERQ_DUMP_EXE

        print(f"PREFETCH: {PREFETCH_EXE}")
        prefetch_exists = Path(PREFETCH_EXE).exists()
        print(
            f"  {'✅' if prefetch_exists else '❌'} {'存在' if prefetch_exists else '不存在'}"
        )

        print(f"FASTERQ: {FASTERQ_DUMP_EXE}")
        fasterq_exists = Path(FASTERQ_DUMP_EXE).exists()
        print(
            f"  {'✅' if fasterq_exists else '❌'} {'存在' if fasterq_exists else '不存在'}"
        )

        return prefetch_exists and fasterq_exists

    except Exception as e:
        print(f"❌ 配置載入失敗: {e}")
        return False


def check_progress_manager():
    """測試 ProgressManager"""
    print("\n" + "=" * 70)
    print("🔍 測試 ProgressManager")
    print("=" * 70)

    try:
        # 動態導入以測試最新修改
        import importlib
        import complete_downloader

        importlib.reload(complete_downloader)

        from complete_downloader import ProgressManager

        pm = ProgressManager()
        print("✅ ProgressManager 初始化成功")
        print(f"   已載入 {len(pm.progress.get('completed', []))} 個已完成樣本")
        return True

    except Exception as e:
        print(f"❌ ProgressManager 初始化失敗: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("🚀 完整環境驗證")
    print("=" * 70)
    print()

    results = []

    # 檢查 JSON
    results.append(("JSON 檔案", check_json_file()))

    # 檢查 SRA Toolkit
    results.append(("SRA Toolkit", check_sra_toolkit()))

    # 檢查 ProgressManager
    results.append(("ProgressManager", check_progress_manager()))

    # 總結
    print("\n" + "=" * 70)
    print("📊 驗證結果")
    print("=" * 70)

    all_passed = True
    for name, passed in results:
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n✅ 所有檢查通過! 可以開始下載了!")
        print("\n執行: python complete_downloader.py")
        return 0
    else:
        print("\n❌ 部分檢查失敗,請先修復問題")
        print("\n修復方案:")

        for name, passed in results:
            if not passed:
                if "JSON" in name:
                    print("  • JSON 檔案: 執行 python fix_json.py")
                elif "SRA" in name:
                    print("  • SRA Toolkit: 執行 一鍵安裝_SRA_Toolkit.bat")
                elif "Progress" in name:
                    print("  • ProgressManager: 檢查 complete_downloader.py 語法")

        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ 驗證過程出錯: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
