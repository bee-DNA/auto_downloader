#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 aria2 加速下載 SRA 檔案的包裝器
aria2 支援多連接下載，可以將 5 Mbps 提升到 20-50 Mbps
"""

import subprocess
import sys
from pathlib import Path

def download_with_aria2(url, output_path, connections=16):
    """
    使用 aria2 多連接下載
    
    Args:
        url: 下載 URL
        output_path: 輸出路徑
        connections: 連接數（預設 16）
    """
    cmd = [
        "aria2c",
        "--max-connection-per-server=16",  # 每個伺服器最多 16 個連接
        "--split=16",  # 分割為 16 個部分同時下載
        "--min-split-size=1M",  # 最小分割大小 1MB
        "--max-concurrent-downloads=1",
        "--continue=true",  # 支援斷點續傳
        "--max-tries=5",
        "--retry-wait=3",
        "--timeout=60",
        "--connect-timeout=30",
        f"--dir={output_path.parent}",
        f"--out={output_path.name}",
        url
    ]
    
    print(f"🚀 使用 aria2 加速下載（16 連接）...")
    print(f"   指令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ aria2 下載失敗: {e}")
        print(f"   stderr: {e.stderr}")
        return False


def get_sra_download_url(run_id):
    """
    構建 SRA 檔案的直接下載 URL
    
    NCBI SRA 檔案 URL 格式:
    https://sra-downloadb.be-md.ncbi.nlm.nih.gov/sos4/sra-pub-run-28/{run_id}/{run_id}.sra
    
    其中 run-28 是批次號，前 6 個字元相同的 ID 在同一批次
    """
    # SRA ID 格式: ERR123456 或 SRR123456
    prefix = run_id[:6]  # 前 6 個字元
    
    # NCBI 有多個下載鏡像
    mirrors = [
        f"https://sra-downloadb.be-md.ncbi.nlm.nih.gov/sos4/sra-pub-run-28/{prefix}/{run_id}/{run_id}.sra",
        f"https://sra-download.ncbi.nlm.nih.gov/traces/sra68/SRZ/{prefix}/{run_id}/{run_id}.sra",
        f"https://sra-pub-run-odp.s3.amazonaws.com/sra/{run_id}/{run_id}",
    ]
    
    return mirrors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python aria2_wrapper.py <RUN_ID>")
        sys.exit(1)
    
    run_id = sys.argv[1]
    output_dir = Path("data/sra_temp") / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{run_id}.sra"
    
    urls = get_sra_download_url(run_id)
    
    success = False
    for i, url in enumerate(urls, 1):
        print(f"\n嘗試鏡像 {i}/{len(urls)}: {url}")
        if download_with_aria2(url, output_file):
            print(f"✅ 下載成功!")
            success = True
            break
        else:
            print(f"⚠️ 鏡像 {i} 失敗，嘗試下一個...")
    
    if not success:
        print(f"\n❌ 所有鏡像都失敗")
        sys.exit(1)
