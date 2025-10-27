"""
詳細檢查 NAS 路徑和檔案
"""

from config import *
from nas_uploader import NASUploader

print("=" * 70)
print("🔍 詳細檢查 NAS 路徑")
print("=" * 70)

print(f"\n配置的 NAS 路徑:")
print(f"  FASTQ: {NAS_FASTQ_PATH}")
print(f"  SRA: {NAS_SRA_PATH}")

uploader = NASUploader(NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS)

if not uploader.connect():
    print("\n❌ 無法連接到 NAS")
    exit(1)

print("\n✅ 已連接到 NAS")

# 測試各種可能的路徑
test_paths = [
    NAS_FASTQ_PATH,
    "/homes/bioailab/Bee_metagenomics/Bee_metagenomics/fastq_data",
    "/Bee_metagenomics/Bee_metagenomics/fastq_data",
    "/volume1/homes/bioailab/Bee_metagenomics/Bee_metagenomics/fastq_data",
]

print("\n" + "=" * 70)
print("測試不同路徑:")
print("=" * 70)

for path in test_paths:
    print(f"\n測試路徑: {path}")
    try:
        files = uploader.sftp.listdir(path)
        fastq_files = [
            f for f in files if f.endswith(".fastq") or f.endswith(".fastq.gz")
        ]
        print(f"  ✅ 路徑存在")
        print(f"  📁 總檔案數: {len(files)}")
        print(f"  📄 FASTQ 檔案: {len(fastq_files)}")

        if fastq_files:
            print(f"  前5個 FASTQ: {fastq_files[:5]}")

            # 測試樣本名稱提取
            sample = fastq_files[0].rsplit("_", 1)[0]
            print(f"  範例樣本ID: {sample}")

    except FileNotFoundError:
        print(f"  ❌ 路徑不存在")
    except PermissionError:
        print(f"  ❌ 沒有權限訪問")
    except Exception as e:
        print(f"  ❌ 錯誤: {e}")

# 嘗試列出上層目錄
print("\n" + "=" * 70)
print("嘗試列出上層目錄結構:")
print("=" * 70)

parent_paths = [
    "/homes/bioailab",
    "/homes/bioailab/Bee_metagenomics",
    "/homes/bioailab/Bee_metagenomics/Bee_metagenomics",
]

for path in parent_paths:
    print(f"\n{path}:")
    try:
        items = uploader.sftp.listdir(path)
        print(f"  📁 子目錄/檔案: {items[:10]}")
    except Exception as e:
        print(f"  ❌ 無法訪問: {e}")

uploader.disconnect()

print("\n" + "=" * 70)
print("檢查完成")
print("=" * 70)
