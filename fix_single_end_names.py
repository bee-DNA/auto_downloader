#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 SINGLE-END 樣本 - 將錯誤的 _2.fastq 重命名為 _1.fastq
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS, NAS_FASTQ_PATH
from nas_uploader import NASUploader

def fix_single_end_files():
    """修復 SINGLE-END 樣本的檔名"""
    
    # 需要重命名的樣本（有 _2 但應該是 _1）
    samples_to_fix = [
        'ERR2696421',
        'ERR2696424',
        'ERR2696425',
        'ERR2696428',
    ]
    
    print("🔧 修復 SINGLE-END 樣本檔名...")
    print(f"   將 _2.fastq 重命名為 _1.fastq")
    print()
    
    # 連接 NAS
    nas = NASUploader(NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS)
    if not nas.connect():
        print("❌ NAS 連接失敗")
        return False
    
    try:
        success_count = 0
        
        for sample in samples_to_fix:
            old_name = f"{sample}_2.fastq"
            new_name = f"{sample}_1.fastq"
            
            old_path = f"{NAS_FASTQ_PATH}/{old_name}"
            new_path = f"{NAS_FASTQ_PATH}/{new_name}"
            
            try:
                # 檢查舊檔案是否存在
                nas.sftp.stat(old_path)
                
                # 重命名
                nas.sftp.rename(old_path, new_path)
                print(f"✅ {sample}: {old_name} → {new_name}")
                success_count += 1
                
            except FileNotFoundError:
                print(f"⚠️  {sample}: {old_name} 不存在")
            except Exception as e:
                print(f"❌ {sample}: 重命名失敗 - {e}")
        
        print()
        print("=" * 60)
        print(f"✅ 成功修復: {success_count}/{len(samples_to_fix)} 個檔案")
        
        return success_count == len(samples_to_fix)
    
    finally:
        nas.disconnect()

if __name__ == "__main__":
    success = fix_single_end_files()
    sys.exit(0 if success else 1)
