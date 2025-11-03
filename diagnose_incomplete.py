#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷不完整樣本 - 檢查是單端還是下載失敗
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS, NAS_FASTQ_PATH
from nas_uploader import NASUploader

def diagnose_incomplete_samples():
    """診斷不完整的樣本"""
    
    # 從之前的報告中已知的不完整樣本
    samples_to_check = [
        'ERR372353', 'ERR372354', 'ERR372355',  # 缺失
        'ERR2696417', 'ERR2696418', 'ERR2696419', 'ERR2696420', 'ERR2696421',
        'ERR2696422', 'ERR2696423', 'ERR2696424', 'ERR2696425', 'ERR2696426',
        'ERR2696427', 'ERR2696428', 'ERR2696429', 'ERR2696430', 'ERR2696431',
        'ERR2696432', 'ERR2696433', 'ERR2696434', 'ERR2696435', 'ERR2696436',
        'ERR2696437', 'ERR2696438', 'ERR2696439', 'ERR2696440'
    ]
    
    print(f"🔍 檢查 {len(samples_to_check)} 個樣本...")
    print()
    
    # 連接 NAS
    nas = NASUploader(NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS)
    if not nas.connect():
        print("❌ NAS 連接失敗")
        return
    
    try:
        # 列出 NAS 上的所有檔案
        all_files = nas.sftp.listdir(NAS_FASTQ_PATH)
        
        results = {
            'both_exist': [],  # 兩個檔案都存在
            'only_1': [],      # 只有 _1
            'only_2': [],      # 只有 _2
            'neither': [],     # 都不存在
        }
        
        for sample in samples_to_check:
            file_1 = f"{sample}_1.fastq"
            file_2 = f"{sample}_2.fastq"
            
            has_1 = file_1 in all_files
            has_2 = file_2 in all_files
            
            if has_1 and has_2:
                results['both_exist'].append(sample)
                print(f"✅ {sample}: 兩個檔案都存在")
            elif has_1 and not has_2:
                results['only_1'].append(sample)
                # 獲取檔案大小
                try:
                    stat = nas.sftp.stat(f"{NAS_FASTQ_PATH}/{file_1}")
                    size_mb = stat.st_size / (1024 * 1024)
                    print(f"⚠️  {sample}: 只有 _1 ({size_mb:.1f} MB)")
                except:
                    print(f"⚠️  {sample}: 只有 _1 (無法獲取大小)")
            elif has_2 and not has_1:
                results['only_2'].append(sample)
                try:
                    stat = nas.sftp.stat(f"{NAS_FASTQ_PATH}/{file_2}")
                    size_mb = stat.st_size / (1024 * 1024)
                    print(f"⚠️  {sample}: 只有 _2 ({size_mb:.1f} MB)")
                except:
                    print(f"⚠️  {sample}: 只有 _2 (無法獲取大小)")
            else:
                results['neither'].append(sample)
                print(f"❌ {sample}: 兩個檔案都不存在")
        
        print()
        print("=" * 80)
        print("📊 統計")
        print("=" * 80)
        print(f"✅ 兩個檔案都存在: {len(results['both_exist'])} 個")
        print(f"⚠️  只有 _1: {len(results['only_1'])} 個")
        print(f"⚠️  只有 _2: {len(results['only_2'])} 個")
        print(f"❌ 都不存在: {len(results['neither'])} 個")
        
        if results['both_exist']:
            print(f"\n✅ 實際上已完整的樣本: {', '.join(results['both_exist'][:5])}" + 
                  (f" ... 等 {len(results['both_exist'])} 個" if len(results['both_exist']) > 5 else ""))
        
    finally:
        nas.disconnect()

if __name__ == "__main__":
    diagnose_incomplete_samples()
