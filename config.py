#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
獨立下載器配置檔案
包含所有必要的 NCBI 和 NAS 設定
"""

import os
from pathlib import Path

# ============================================
# NCBI API 配置
# ============================================
NCBI_API_KEY = os.environ.get("NCBI_API_KEY", "cbc34d71d57af75c93952af5d6b51d58d008")
NCBI_EMAIL = os.environ.get("NCBI_EMAIL", "123321123axx@gmail.com")

# ============================================
# NAS SFTP 配置
# 優先從環境變數讀取，若無則使用預設值
# ============================================
NAS_HOST = os.environ.get("NAS_HOST", "bioailab.synology.me")
NAS_PORT = int(os.environ.get("NAS_PORT", 22))
NAS_USER = os.environ.get("NAS_USER", "bioailab")
NAS_PASS = "Ncueailab403"

# NAS 遠端路徑 (相對路徑)
NAS_FASTQ_PATH = "Bee_metagenomics/Bee_metagenomics/fastq_data"
NAS_SRA_PATH = "Bee_metagenomics/Bee_metagenomics/sra_files"

# ============================================
# 本地路徑配置 (改為相對路徑)
# ============================================
# 專案根目錄
BASE_DIR = Path(__file__).parent

# 資料目錄
DATA_DIR = BASE_DIR / "data"

# SRA Toolkit 路徑 (自動檢測)
# 假設 sratoolkit 目錄與此 config.py 在同一層級
SRA_TOOLKIT_DIR_WIN = BASE_DIR / "sratoolkit.3.2.1-win64" / "bin"
SRA_TOOLKIT_DIR_LINUX = BASE_DIR / "sratoolkit.3.2.1-ubuntu64" / "bin"


# 平台無關的執行檔名稱
prefetch_exec = "prefetch.exe" if os.name == 'nt' else "prefetch"
fasterq_dump_exec = "fasterq-dump.exe" if os.name == 'nt' else "fasterq-dump"
vdb_validate_exec = "vdb-validate.exe" if os.name == 'nt' else "vdb-validate"

SRA_TOOLKIT_DIR = SRA_TOOLKIT_DIR_WIN if os.name == 'nt' else SRA_TOOLKIT_DIR_LINUX

if SRA_TOOLKIT_DIR.exists():
    # 使用本地 SRA Toolkit
    PREFETCH_EXE = str(SRA_TOOLKIT_DIR / prefetch_exec)
    FASTERQ_DUMP_EXE = str(SRA_TOOLKIT_DIR / fasterq_dump_exec)
    VDB_VALIDATE_EXE = str(SRA_TOOLKIT_DIR / vdb_validate_exec)
else:
    # 使用系統 PATH 中的工具
    PREFETCH_EXE = prefetch_exec
    FASTERQ_DUMP_EXE = fasterq_dump_exec
    VDB_VALIDATE_EXE = vdb_validate_exec

# SRA 下載臨時目錄
SRA_TEMP_DIR = str(DATA_DIR / "sra_temp")

# FASTQ 解壓臨時目錄
FASTQ_TEMP_DIR = str(DATA_DIR / "tmp")

# FASTQ 輸出目錄
FASTQ_OUTPUT_DIR = str(DATA_DIR / "fastq_output")

# ============================================
# 下載器配置
# ============================================
# 並行下載數量（同時處理幾個樣本）
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", 6))

# fasterq-dump 線程數（每個樣本用幾個線程解壓）
FASTERQ_THREADS = int(os.environ.get("FASTERQ_THREADS", 5))

# ============================================
# 進度檔案配置
# ============================================
# 樣本清單檔案
RUNS_FILE = "runs.txt"

# 進度記錄檔案
PROGRESS_FILE = "download_progress.json"

# 日誌檔案
LOG_FILE = "downloader.log"

# ============================================
# 重試配置
# ============================================
# 下載失敗重試次數
MAX_RETRIES = 3

# 重試等待時間（秒）
RETRY_DELAY = 5

# ============================================
# 環境檢查函數 (用於直接執行此檔案時)
# ============================================
def check_and_create_paths():
    """檢查並創建必要的本地目錄"""
    paths = [SRA_TEMP_DIR, FASTQ_TEMP_DIR, FASTQ_OUTPUT_DIR]
    print("1️⃣  檢查本地目錄:")
    for path in paths:
        path_obj = Path(path)
        if not path_obj.exists():
            print(f"   - 創建目錄: {path_obj.relative_to(BASE_DIR)}")
            path_obj.mkdir(parents=True, exist_ok=True)
        else:
            print(f"   - 目錄已存在: {path_obj.relative_to(BASE_DIR)}")

if __name__ == "__main__":
    print("=" * 60)
    print("📋 配置檔案檢查 (Docker-Ready Version)")
    print("=" * 60)

    check_and_create_paths()

    print("\n2️⃣  配置摘要:")
    print(f"  - SRA Toolkit Path: {SRA_TOOLKIT_DIR}")
    print(f"  - Prefetch command: {PREFETCH_EXE}")
    print(f"  - NAS Host: {NAS_HOST}")
    print(f"  - NAS User: {NAS_USER}")
    print(f"  - NAS Pass: {'*' * len(NAS_PASS) if NAS_PASS else '(Not Set)'}")
    print(f"  - Concurrency: {MAX_WORKERS} workers, {FASTERQ_THREADS} threads/worker")

    print("\n✅ 配置檔案正常")
    print("   現在路徑為相對路徑，並可透過環境變數覆寫。")
