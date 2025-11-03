#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查樣本的 Layout (SINGLE 或 PAIRED)
使用 NCBI Entrez API 查詢
"""

import requests
import time
import xml.etree.ElementTree as ET

def check_sample_layout(run_id):
    """
    查詢 SRA 樣本的 layout (SINGLE 或 PAIRED)
    
    Args:
        run_id: SRA run ID (例如 ERR2696422)
    
    Returns:
        'SINGLE', 'PAIRED', 或 'UNKNOWN'
    """
    try:
        # 使用 NCBI E-utilities API
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            'db': 'sra',
            'id': run_id,
            'rettype': 'xml'
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        # 解析 XML
        root = ET.fromstring(response.text)
        
        # 查找 LIBRARY_LAYOUT
        for layout in root.iter('LIBRARY_LAYOUT'):
            if layout.find('SINGLE') is not None:
                return 'SINGLE'
            elif layout.find('PAIRED') is not None:
                return 'PAIRED'
        
        return 'UNKNOWN'
    
    except Exception as e:
        print(f"  ❌ 查詢失敗: {e}")
        return 'ERROR'

def main():
    """檢查不完整樣本的 layout"""
    
    # 檢查所有缺失和不完整的樣本
    samples_with_files = [
        # 有部分檔案的 8 個
        'ERR2696421',  # 只有 _2
        'ERR2696422',  # 只有 _1
        'ERR2696423',  # 只有 _1
        'ERR2696424',  # 只有 _2
        'ERR2696425',  # 只有 _2
        'ERR2696426',  # 只有 _1
        'ERR2696427',  # 只有 _1
        'ERR2696428',  # 只有 _2
        # 完全缺失的樣本（取幾個檢查）
        'ERR372353', 'ERR372354', 'ERR372355',
        'ERR2696417', 'ERR2696418', 'ERR2696429', 'ERR2696430'
    ]
    
    print("🔍 檢查樣本的 Layout (SINGLE/PAIRED)...")
    print("=" * 60)
    
    results = {}
    for run_id in samples_with_files:
        print(f"📊 {run_id}...", end=" ", flush=True)
        layout = check_sample_layout(run_id)
        results[run_id] = layout
        
        if layout == 'SINGLE':
            print("✅ SINGLE-END")
        elif layout == 'PAIRED':
            print("⚠️  PAIRED-END (缺少另一個檔案)")
        else:
            print(f"❓ {layout}")
        
        # 避免 API 限制
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print("📊 統計")
    print("=" * 60)
    
    single_count = sum(1 for v in results.values() if v == 'SINGLE')
    paired_count = sum(1 for v in results.values() if v == 'PAIRED')
    
    print(f"✅ SINGLE-END: {single_count} 個")
    print(f"⚠️  PAIRED-END: {paired_count} 個")
    
    if single_count > 0:
        print()
        print("💡 結論: 這些樣本是 SINGLE-END，只會產生一個 _1.fastq 檔案")
        print("   驗證腳本需要修改，不應該期待 _2.fastq 檔案")
    
    if paired_count > 0:
        print()
        print("⚠️  警告: 這些是 PAIRED-END 樣本，但只有一個檔案")
        print("   需要重新下載以獲取完整的配對檔案")
        paired_samples = [k for k, v in results.items() if v == 'PAIRED']
        print(f"   受影響樣本: {', '.join(paired_samples)}")

if __name__ == "__main__":
    main()
