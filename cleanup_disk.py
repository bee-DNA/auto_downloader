#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理 sra_temp 和 fastq_output 中的空資料夾和殘留檔案
釋放磁碟空間
"""

import shutil
from pathlib import Path
from config import SRA_TEMP_DIR, FASTQ_OUTPUT_DIR, FASTQ_TEMP_DIR

def cleanup_empty_dirs(base_dir):
    """刪除空資料夾"""
    base_path = Path(base_dir)
    if not base_path.exists():
        print(f"目錄不存在: {base_path}")
        return 0
    
    removed_count = 0
    for item in base_path.iterdir():
        if item.is_dir():
            # 檢查是否為空
            if not any(item.iterdir()):
                try:
                    item.rmdir()
                    print(f"✅ 刪除空資料夾: {item.name}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ 無法刪除 {item.name}: {e}")
    
    return removed_count

def cleanup_temp_files(base_dir):
    """刪除臨時檔案和鎖檔"""
    base_path = Path(base_dir)
    if not base_path.exists():
        print(f"目錄不存在: {base_path}")
        return 0
    
    removed_count = 0
    patterns = ["*.tmp", "*.lock", "*.partial"]
    
    for pattern in patterns:
        for tmp_file in base_path.rglob(pattern):
            try:
                if tmp_file.is_file():
                    size_mb = tmp_file.stat().st_size / (1024**2)
                    tmp_file.unlink()
                    print(f"✅ 刪除臨時檔: {tmp_file.name} ({size_mb:.2f} MB)")
                    removed_count += 1
            except Exception as e:
                print(f"❌ 無法刪除 {tmp_file.name}: {e}")
    
    return removed_count

def cleanup_incomplete_sra(base_dir):
    """刪除不完整的 SRA 資料夾（沒有 .sra 檔案的）"""
    base_path = Path(base_dir)
    if not base_path.exists():
        print(f"目錄不存在: {base_path}")
        return 0
    
    removed_count = 0
    for item in base_path.iterdir():
        if item.is_dir():
            # 檢查是否有 .sra 檔案
            sra_files = list(item.glob("*.sra"))
            if not sra_files:
                try:
                    shutil.rmtree(item)
                    print(f"✅ 刪除不完整的 SRA 資料夾: {item.name}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ 無法刪除 {item.name}: {e}")
    
    return removed_count

def get_disk_usage(path):
    """獲取磁碟使用情況"""
    usage = shutil.disk_usage(path)
    total_gb = usage.total / (1024**3)
    used_gb = usage.used / (1024**3)
    free_gb = usage.free / (1024**3)
    used_percent = (usage.used / usage.total) * 100
    
    return total_gb, used_gb, free_gb, used_percent

if __name__ == "__main__":
    print("=" * 80)
    print("清理磁碟空間")
    print("=" * 80)
    
    # 顯示清理前的磁碟使用情況
    total, used, free, percent = get_disk_usage(SRA_TEMP_DIR)
    print(f"\n清理前:")
    print(f"  總容量: {total:.2f} GB")
    print(f"  已使用: {used:.2f} GB ({percent:.1f}%)")
    print(f"  可用: {free:.2f} GB")
    
    print(f"\n開始清理...")
    print("-" * 80)
    
    # 1. 清理 SRA_TEMP_DIR
    print(f"\n清理 SRA 目錄: {SRA_TEMP_DIR}")
    temp_files = cleanup_temp_files(SRA_TEMP_DIR)
    incomplete = cleanup_incomplete_sra(SRA_TEMP_DIR)
    empty_dirs = cleanup_empty_dirs(SRA_TEMP_DIR)
    
    # 2. 清理 FASTQ_OUTPUT_DIR
    print(f"\n清理 FASTQ 目錄: {FASTQ_OUTPUT_DIR}")
    fastq_temp = cleanup_temp_files(FASTQ_OUTPUT_DIR)
    
    # 3. 清理 FASTQ_TEMP_DIR
    print(f"\n清理 FASTQ_TEMP 目錄: {FASTQ_TEMP_DIR}")
    tmp_files = cleanup_temp_files(FASTQ_TEMP_DIR)
    
    # 顯示清理後的磁碟使用情況
    print("\n" + "=" * 80)
    total, used, free, percent = get_disk_usage(SRA_TEMP_DIR)
    print(f"清理後:")
    print(f"  總容量: {total:.2f} GB")
    print(f"  已使用: {used:.2f} GB ({percent:.1f}%)")
    print(f"  可用: {free:.2f} GB")
    
    print(f"\n清理統計:")
    print(f"  臨時檔案: {temp_files + fastq_temp + tmp_files} 個")
    print(f"  不完整 SRA: {incomplete} 個")
    print(f"  空資料夾: {empty_dirs} 個")
    print(f"\n✅ 清理完成")
