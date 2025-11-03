#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理 NAS 上所有 FASTQ 檔案清單並輸出為 CSV
"""

import sys
import csv
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS, NAS_FASTQ_PATH
from nas_uploader import NASUploader

def export_nas_files_to_csv(output_file='nas_fastq_files.csv'):
    """
    列出 NAS 上所有 FASTQ 檔案並輸出為 CSV
    
    CSV 格式:
    - 編號 (1, 2, 3...)
    - 完整檔名 (例如: ERR2696422_1.fastq)
    - 檔案大小 (MB)
    """
    
    print("=" * 80)
    print("📋 整理 NAS FASTQ 檔案清單")
    print("=" * 80)
    print()
    
    # 連接 NAS
    print("🔗 連接 NAS...")
    nas = NASUploader(NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS)
    if not nas.connect():
        print("❌ NAS 連接失敗")
        return False
    
    try:
        # 列出所有檔案
        print("📂 讀取檔案列表...")
        all_files = nas.sftp.listdir(NAS_FASTQ_PATH)
        fastq_files = [f for f in all_files if f.endswith('.fastq')]
        
        print(f"✅ 找到 {len(fastq_files)} 個 FASTQ 檔案")
        print()
        
        # 收集檔案資訊
        print("📊 收集檔案大小資訊...")
        file_info = []
        
        for i, filename in enumerate(sorted(fastq_files), 1):
            try:
                file_path = f"{NAS_FASTQ_PATH}/{filename}"
                stat = nas.sftp.stat(file_path)
                size_mb = stat.st_size / (1024 * 1024)
                
                file_info.append({
                    'number': i,
                    'filename': filename,
                    'size_mb': round(size_mb, 2)
                })
                
                # 進度顯示
                if i % 100 == 0:
                    print(f"  進度: {i}/{len(fastq_files)}")
                
            except Exception as e:
                print(f"  ⚠️  無法讀取 {filename}: {e}")
                file_info.append({
                    'number': i,
                    'filename': filename,
                    'size_mb': 0.0
                })
        
        print(f"✅ 完成 {len(file_info)} 個檔案")
        print()
        
        # 寫入 CSV
        print(f"💾 寫入 CSV 檔案: {output_file}")
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            
            # 寫入標題
            writer.writerow(['編號', '樣本ID', '完整檔名', '檔案大小(MB)'])
            
            # 寫入資料
            for info in file_info:
                # 提取樣本ID (去掉 _1.fastq, _2.fastq, _3.fastq 等後綴)
                sample_id = info['filename'].rsplit('_', 1)[0]
                
                writer.writerow([
                    info['number'],
                    sample_id,
                    info['filename'],
                    info['size_mb']
                ])
        
        print(f"✅ CSV 檔案已建立: {output_file}")
        print()
        
        # 顯示統計
        print("=" * 80)
        print("📈 統計資訊")
        print("=" * 80)
        
        total_size = sum(info['size_mb'] for info in file_info)
        avg_size = total_size / len(file_info) if file_info else 0
        
        print(f"總檔案數: {len(file_info)} 個")
        print(f"總大小: {total_size:,.2f} MB ({total_size/1024:.2f} GB)")
        print(f"平均大小: {avg_size:.2f} MB")
        print(f"最大檔案: {max(file_info, key=lambda x: x['size_mb'])['filename']} ({max(file_info, key=lambda x: x['size_mb'])['size_mb']:.2f} MB)")
        print(f"最小檔案: {min(file_info, key=lambda x: x['size_mb'])['filename']} ({min(file_info, key=lambda x: x['size_mb'])['size_mb']:.2f} MB)")
        
        return True
        
    finally:
        nas.disconnect()

if __name__ == "__main__":
    success = export_nas_files_to_csv()
    sys.exit(0 if success else 1)
