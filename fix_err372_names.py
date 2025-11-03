#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 ERR372353-355 的檔名：_3.fastq → _1.fastq
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS, NAS_FASTQ_PATH
from nas_uploader import NASUploader

def fix_err372_files():
    """修復 ERR372353-355 的檔名"""
    
    samples = ['ERR372353', 'ERR372354', 'ERR372355']
    
    print("🔧 修復 ERR372353-355 檔名...")
    print("   將 _3.fastq 重命名為 _1.fastq")
    print()
    
    nas = NASUploader(NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS)
    if not nas.connect():
        print("❌ NAS 連接失敗")
        return False
    
    try:
        success_count = 0
        
        for sample in samples:
            old_name = f"{sample}_3.fastq"
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
        print(f"✅ 成功修復: {success_count}/{len(samples)} 個檔案")
        
        return success_count == len(samples)
    
    finally:
        nas.disconnect()

if __name__ == "__main__":
    success = fix_err372_files()
    
    if success:
        print()
        print("🎉 檔名修復完成！")
        print("現在運行 verify_fastq_smart.py 確認全部完整")
    
    sys.exit(0 if success else 1)
