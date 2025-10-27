"""
測試 NAS 檢查邏輯 - 確認只下載缺少的樣本
"""

import sys
from pathlib import Path

print("=" * 70)
print("🔍 測試 NAS 檢查邏輯")
print("=" * 70)

# 導入必要模組
try:
    from config import *
    from nas_uploader import NASUploader
    from complete_downloader import (
        get_all_runs_from_file,
        get_nas_samples,
        get_missing_samples,
    )
except ImportError as e:
    print(f"❌ 導入失敗: {e}")
    sys.exit(1)

print("\n[1/3] 讀取 runs.txt...")
try:
    all_runs = get_all_runs_from_file()
    print(f"✅ runs.txt 中的樣本: {len(all_runs)} 個")
    print(f"   前5個: {sorted(list(all_runs))[:5]}")
except Exception as e:
    print(f"❌ 讀取失敗: {e}")
    sys.exit(1)

print("\n[2/3] 檢查 NAS 上已有的樣本...")
try:
    nas_samples = get_nas_samples()
    print(f"✅ NAS 已有: {len(nas_samples)} 個樣本")
    if nas_samples:
        print(f"   前5個: {sorted(list(nas_samples))[:5]}")
    else:
        print(f"   ⚠️  NAS 上沒有找到任何 FASTQ 檔案")
except Exception as e:
    print(f"❌ 檢查 NAS 失敗: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n[3/3] 計算需要下載的樣本...")
try:
    missing_samples = get_missing_samples()
    print(f"✅ 需要下載: {len(missing_samples)} 個樣本")
    if missing_samples:
        print(f"   前10個: {missing_samples[:10]}")
except Exception as e:
    print(f"❌ 計算失敗: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("📊 檢查結果總結")
print("=" * 70)

print(f"\n✅ 邏輯正確:")
print(f"   • runs.txt 總數: {len(all_runs)}")
print(f"   • NAS 已有: {len(nas_samples)}")
print(f"   • 需要下載: {len(missing_samples)}")
print(f"   • 驗證: {len(all_runs)} = {len(nas_samples)} + {len(missing_samples)}")

if len(all_runs) == len(nas_samples) + len(missing_samples):
    print(f"\n✅ 數量驗證通過! ✅")
else:
    print(f"\n⚠️  數量不匹配,可能有重複或遺漏")

# 檢查是否會重複下載
if nas_samples:
    overlap = nas_samples & set(missing_samples)
    if overlap:
        print(f"\n❌ 警告: 有 {len(overlap)} 個樣本重複!")
        print(f"   前5個重複: {list(overlap)[:5]}")
    else:
        print(f"\n✅ 確認: 不會重複下載 NAS 上已有的樣本!")

print("\n" + "=" * 70)

if len(missing_samples) == 0:
    print("🎉 所有樣本都已在 NAS 上,無需下載!")
elif len(nas_samples) > 0:
    print(
        f"📥 程式將跳過 {len(nas_samples)} 個已有樣本,只下載 {len(missing_samples)} 個缺少的"
    )
else:
    print(f"📥 程式將下載全部 {len(missing_samples)} 個樣本")

print("=" * 70)
