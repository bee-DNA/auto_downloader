#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查 ERR372353-355 的預期大小
"""

import requests

def check_sample_size(run_id):
    """查詢樣本的預期大小"""
    try:
        url = f"https://www.ebi.ac.uk/ena/portal/api/filereport"
        params = {
            'accession': run_id,
            'result': 'read_run',
            'fields': 'run_accession,fastq_bytes,read_count,base_count'
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        lines = response.text.strip().split('\n')
        if len(lines) > 1:
            header = lines[0].split('\t')
            data = lines[1].split('\t')
            
            result = dict(zip(header, data))
            
            fastq_bytes = int(result.get('fastq_bytes', 0))
            read_count = int(result.get('read_count', 0))
            base_count = int(result.get('base_count', 0))
            
            return {
                'fastq_mb': fastq_bytes / (1024 * 1024),
                'reads': read_count,
                'bases': base_count
            }
    except Exception as e:
        print(f"  ❌ 查詢失敗: {e}")
        return None

def main():
    samples = ['ERR372353', 'ERR372354', 'ERR372355']
    
    print("🔍 檢查樣本預期大小...")
    print("=" * 70)
    
    for run_id in samples:
        print(f"\n📊 {run_id}:")
        info = check_sample_size(run_id)
        
        if info:
            print(f"   預期 FASTQ 大小: {info['fastq_mb']:.1f} MB")
            print(f"   Reads 數量: {info['reads']:,}")
            print(f"   Bases 數量: {info['bases']:,}")
        else:
            print(f"   ❌ 無法獲取資訊")

if __name__ == "__main__":
    main()
