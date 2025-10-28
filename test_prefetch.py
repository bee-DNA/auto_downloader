#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 prefetch 指令，診斷失敗原因
"""

import subprocess
import os
import sys
from pathlib import Path
from config import PREFETCH_EXE, SRA_TEMP_DIR, SRA_TOOLKIT_DIR

# 確保路徑是 Path 物件
PREFETCH_EXE = Path(PREFETCH_EXE) if isinstance(PREFETCH_EXE, str) else PREFETCH_EXE
SRA_TEMP_DIR = Path(SRA_TEMP_DIR) if isinstance(SRA_TEMP_DIR, str) else SRA_TEMP_DIR

# 測試的樣本
test_samples = ["ERR317302", "ERR323407", "ERR323419"]

print("=" * 80)
print("環境資訊")
print("=" * 80)
print(f"作業系統: {os.name}")
print(f"Python: {sys.version}")
print(f"當前目錄: {Path.cwd()}")
print(f"SRA Toolkit 目錄: {SRA_TOOLKIT_DIR}")
print(f"SRA Toolkit 存在: {Path(SRA_TOOLKIT_DIR).exists() if isinstance(SRA_TOOLKIT_DIR, str) else SRA_TOOLKIT_DIR.exists()}")
print(f"使用的 prefetch: {PREFETCH_EXE}")
print(f"Prefetch 存在: {PREFETCH_EXE.exists() if isinstance(PREFETCH_EXE, Path) else Path(PREFETCH_EXE).exists()}")
print(f"輸出目錄: {SRA_TEMP_DIR}")
print(f"PATH: {os.environ.get('PATH', 'N/A')[:200]}")
print("=" * 80)

# 嘗試直接執行 prefetch 查看版本
print("\n嘗試執行 prefetch --version:")
try:
    result = subprocess.run(
        [str(PREFETCH_EXE), "--version"],
        capture_output=True,
        text=True,
        timeout=10
    )
    print(f"返回碼: {result.returncode}")
    if result.stdout:
        print(f"STDOUT: {result.stdout}")
    if result.stderr:
        print(f"STDERR: {result.stderr}")
except Exception as e:
    print(f"錯誤: {e}")

print("\n" + "=" * 80)

# 確保目錄存在
SRA_TEMP_DIR.mkdir(parents=True, exist_ok=True)

for run_id in test_samples:
    print(f"\n測試樣本: {run_id}")
    print("-" * 80)
    
    cmd = [
        str(PREFETCH_EXE),
        run_id,
        "--output-directory",
        str(SRA_TEMP_DIR),
        "--max-size",
        "100GB",
        "-v",  # verbose 模式
    ]
    
    print(f"執行指令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=60  # 60秒超時
        )
        
        print(f"\n返回碼: {result.returncode}")
        
        if result.stdout:
            print(f"\nSTDOUT:\n{result.stdout}")
        
        if result.stderr:
            print(f"\nSTDERR:\n{result.stderr}")
        
        # 檢查檔案是否存在
        sra_file = SRA_TEMP_DIR / run_id / f"{run_id}.sra"
        if sra_file.exists():
            size_mb = sra_file.stat().st_size / (1024**2)
            print(f"\n✅ 檔案已創建: {sra_file} ({size_mb:.2f} MB)")
        else:
            print(f"\n❌ 檔案不存在: {sra_file}")
            
    except subprocess.TimeoutExpired:
        print(f"\n⏰ 超時！")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")

print("\n" + "=" * 80)
print("測試完成")
