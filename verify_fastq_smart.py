#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能 FASTQ 驗證腳本 - 支援 SINGLE-END 和 PAIRED-END
"""

import sys
from pathlib import Path
from collections import defaultdict
import requests
import xml.etree.ElementTree as ET
import time

sys.path.insert(0, str(Path(__file__).parent))

from config import NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS, NAS_FASTQ_PATH, RUNS_FILE
from nas_uploader import NASUploader

def check_sample_layout_batch(run_ids):
    """
    批量查詢樣本的 layout
    
    Returns:
        dict: {run_id: 'SINGLE' or 'PAIRED'}
    """
    print("🔍 查詢樣本 layout (SINGLE/PAIRED)...")
    
    layouts = {}
    for i, run_id in enumerate(run_ids, 1):
        try:
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            params = {
                'db': 'sra',
                'id': run_id,
                'rettype': 'xml'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            
            # 查找 LIBRARY_LAYOUT
            layout = 'UNKNOWN'
            for layout_elem in root.iter('LIBRARY_LAYOUT'):
                if layout_elem.find('SINGLE') is not None:
                    layout = 'SINGLE'
                elif layout_elem.find('PAIRED') is not None:
                    layout = 'PAIRED'
                break
            
            layouts[run_id] = layout
            
            if i % 10 == 0:
                print(f"  進度: {i}/{len(run_ids)}")
            
            # 避免 API 限制
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  ⚠️  {run_id}: 查詢失敗 - {e}")
            layouts[run_id] = 'UNKNOWN'
    
    print(f"✅ 完成 {len(layouts)} 個樣本的 layout 查詢")
    return layouts

def verify_fastq_smart():
    """智能驗證 FASTQ 檔案"""
    
    # 1. 讀取期待的樣本列表
    print("=" * 80)
    print("📋 讀取 runs.txt")
    print("=" * 80)
    
    runs_file = Path(RUNS_FILE)
    if not runs_file.exists():
        print(f"❌ 找不到 {RUNS_FILE}")
        return False
    
    expected_runs = set()
    with open(runs_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                expected_runs.add(line)
    
    print(f"✅ 期待 {len(expected_runs)} 個樣本")
    print()
    
    # 2. 連接 NAS 並列出現有檔案
    print("=" * 80)
    print("🔗 連接 NAS 並檢查檔案")
    print("=" * 80)
    
    nas = NASUploader(NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS)
    if not nas.connect():
        print("❌ NAS 連接失敗")
        return False
    
    try:
        all_files = nas.sftp.listdir(NAS_FASTQ_PATH)
        fastq_files = [f for f in all_files if f.endswith('.fastq')]
        
        print(f"✅ NAS 上有 {len(fastq_files)} 個 FASTQ 檔案")
        print()
        
        # 3. 分析現有檔案
        samples_on_nas = defaultdict(list)
        for filename in fastq_files:
            # 解析檔名 (例如: ERR2696422_1.fastq)
            if '_1.fastq' in filename:
                sample_id = filename.replace('_1.fastq', '')
                samples_on_nas[sample_id].append('_1')
            elif '_2.fastq' in filename:
                sample_id = filename.replace('_2.fastq', '')
                samples_on_nas[sample_id].append('_2')
        
        # 4. 找出需要檢查 layout 的樣本
        incomplete_samples = []
        for sample_id in expected_runs:
            files = samples_on_nas.get(sample_id, [])
            if len(files) == 1:  # 只有一個檔案，需要確認是 SINGLE 還是缺檔
                incomplete_samples.append(sample_id)
            elif len(files) == 0:  # 完全缺失
                incomplete_samples.append(sample_id)
        
        # 5. 查詢 layout
        print("=" * 80)
        print("🔍 檢查不完整樣本的 layout")
        print("=" * 80)
        
        if incomplete_samples:
            layouts = check_sample_layout_batch(incomplete_samples)
        else:
            layouts = {}
        
        print()
        
        # 6. 分類結果
        complete = []
        incomplete_paired = []
        missing = []
        
        for sample_id in expected_runs:
            files = samples_on_nas.get(sample_id, [])
            layout = layouts.get(sample_id, 'UNKNOWN')
            
            if len(files) == 2:  # 有 _1 和 _2
                complete.append(sample_id)
            elif len(files) == 1:  # 只有一個
                if layout == 'SINGLE' and '_1' in files:
                    complete.append(sample_id)  # SINGLE-END 只需要 _1
                else:
                    incomplete_paired.append(sample_id)  # PAIRED-END 缺少另一個
            else:  # 沒有檔案
                missing.append(sample_id)
        
        # 7. 列印報告
        print("=" * 80)
        print("📊 驗證結果")
        print("=" * 80)
        print(f"✅ 完整樣本: {len(complete)}/{len(expected_runs)} 個")
        print(f"⚠️  不完整樣本: {len(incomplete_paired)} 個")
        print(f"❌ 缺失樣本: {len(missing)} 個")
        print()
        
        if incomplete_paired:
            print("⚠️  不完整的 PAIRED-END 樣本:")
            for sample in sorted(incomplete_paired)[:10]:
                files = samples_on_nas.get(sample, [])
                print(f"   - {sample}: 只有 {', '.join(files)}")
            if len(incomplete_paired) > 10:
                print(f"   ... 還有 {len(incomplete_paired) - 10} 個")
            print()
        
        if missing:
            print("❌ 缺失的樣本:")
            for sample in sorted(missing)[:10]:
                print(f"   - {sample}")
            if len(missing) > 10:
                print(f"   ... 還有 {len(missing) - 10} 個")
            print()
        
        # 8. 生成修復清單
        if incomplete_paired or missing:
            runs_to_fix = sorted(incomplete_paired + missing)
            
            with open('runs_to_fix.txt', 'w') as f:
                for run in runs_to_fix:
                    f.write(f"{run}\n")
            
            print(f"📝 已生成 runs_to_fix.txt ({len(runs_to_fix)} 個樣本)")
            
            # 生成刪除清單（只刪除不完整的 PAIRED-END 檔案）
            files_to_delete = []
            for sample in incomplete_paired:
                files = samples_on_nas.get(sample, [])
                for suffix in files:
                    files_to_delete.append(f"{sample}{suffix}.fastq")
            
            if files_to_delete:
                with open('files_to_delete.txt', 'w') as f:
                    for filename in sorted(files_to_delete):
                        f.write(f"{filename}\n")
                
                print(f"🗑️  已生成 files_to_delete.txt ({len(files_to_delete)} 個檔案)")
        else:
            print("🎉 所有樣本都完整！")
        
        return len(incomplete_paired) == 0 and len(missing) == 0
    
    finally:
        nas.disconnect()

if __name__ == "__main__":
    success = verify_fastq_smart()
    sys.exit(0 if success else 1)
