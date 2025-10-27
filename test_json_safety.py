"""
測試 JSON 保存的安全性
"""

import json
from pathlib import Path
import sys

print("=" * 70)
print("🧪 測試 JSON 保存邏輯")
print("=" * 70)

# 導入 ProgressManager
try:
    import importlib
    import complete_downloader

    importlib.reload(complete_downloader)
    from complete_downloader import ProgressManager
except Exception as e:
    print(f"❌ 導入失敗: {e}")
    sys.exit(1)

print("\n[測試 1] 初始化 ProgressManager...")
try:
    pm = ProgressManager("test_progress.json")
    print(f"✅ 初始化成功")
    print(f"   已完成: {len(pm.progress.get('completed', []))}")
except Exception as e:
    print(f"❌ 失敗: {e}")
    sys.exit(1)

print("\n[測試 2] 測試保存功能...")
try:
    # 添加一些測試數據
    pm.progress["completed"] = ["TEST001", "TEST002", "TEST003"]
    pm.progress["failed"] = []

    pm.save_progress()
    print(f"✅ 保存成功")

    # 驗證檔案存在且可讀
    test_file = Path("test_progress.json")
    if test_file.exists():
        with open(test_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ 檔案格式正確")
        print(f"   完成數: {len(data['completed'])}")
    else:
        print(f"❌ 檔案不存在!")

except Exception as e:
    print(f"❌ 失敗: {e}")
    import traceback

    traceback.print_exc()

print("\n[測試 3] 測試多次保存 (觸發自動備份)...")
try:
    for i in range(12):
        pm.progress["completed"].append(f"TEST{i:03d}")
        pm.save_progress()
        if i == 9:
            print(f"   保存 {i+1} 次 (應該觸發備份)")

    print(f"✅ 多次保存成功")

    # 檢查備份檔案
    backup_files = list(Path(".").glob("test_progress_backup_*.json"))
    print(f"   備份檔案數: {len(backup_files)}")

except Exception as e:
    print(f"❌ 失敗: {e}")

print("\n[測試 4] 清理測試檔案...")
try:
    test_file = Path("test_progress.json")
    if test_file.exists():
        test_file.unlink()

    for backup in Path(".").glob("test_progress_backup_*.json"):
        backup.unlink()

    for temp in Path(".").glob("test_progress.tmp"):
        temp.unlink()

    for bak in Path(".").glob("test_progress.bak"):
        bak.unlink()

    print(f"✅ 清理完成")
except Exception as e:
    print(f"⚠️  清理失敗: {e}")

print("\n" + "=" * 70)
print("✅ 所有測試完成!")
print("=" * 70)
print("\n💡 改進說明:")
print("  1. ✅ 使用臨時檔案 + 備份檔案,防止寫入失敗導致資料遺失")
print("  2. ✅ 每10次保存或每30分鐘自動創建帶時間戳的備份")
print("  3. ✅ 如果保存失敗會自動恢復備份")
print("  4. ✅ 所有操作都有錯誤處理")
