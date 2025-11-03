#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
緊急檢查：NAS 上剛剛上傳的檔案
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS, NAS_FASTQ_PATH
from nas_uploader import NASUploader

def check_recent_uploads():
    """檢查最近上傳的 ERR372354 和 ERR372355"""
    
    samples = ['ERR372353', 'ERR372354', 'ERR372355']
    
    print("🔍 檢查最近上傳的檔案...")
    print()
    
    nas = NASUploader(NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS)
    if not nas.connect():
        print("❌ NAS 連接失敗")
        return
    
    try:
        all_files = nas.sftp.listdir(NAS_FASTQ_PATH)
        
        for sample in samples:
            matching_files = [f for f in all_files if f.startswith(sample)]
            
            if matching_files:
                print(f"📁 {sample}:")
                for filename in sorted(matching_files):
                    try:
                        stat = nas.sftp.stat(f"{NAS_FASTQ_PATH}/{filename}")
                        size_mb = stat.st_size / (1024 * 1024)
                        print(f"   - {filename} ({size_mb:.1f} MB)")
                    except:
                        print(f"   - {filename} (無法獲取大小)")
            else:
                print(f"❌ {sample}: 沒有檔案")
            print()
    
    finally:
        nas.disconnect()

if __name__ == "__main__":
    check_recent_uploads()
