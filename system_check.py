#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整系統檢查 - 在執行前驗證所有配置
"""

import sys
import os
from pathlib import Path

def check_config():
    """檢查配置檔案"""
    print("=" * 80)
    print("🔍 檢查配置檔案")
    print("=" * 80)
    
    try:
        from config import (
            MAX_WORKERS, FASTERQ_THREADS, 
            USE_ARIA2, ARIA2_CONNECTIONS,
            PREFETCH_EXE, FASTERQ_DUMP_EXE, VDB_VALIDATE_EXE,
            SRA_TEMP_DIR, FASTQ_OUTPUT_DIR,
            NAS_HOST, NAS_PORT
        )
        
        print(f"✅ config.py 導入成功")
        print(f"   - MAX_WORKERS: {MAX_WORKERS}")
        print(f"   - FASTERQ_THREADS: {FASTERQ_THREADS}")
        print(f"   - USE_ARIA2: {USE_ARIA2}")
        print(f"   - ARIA2_CONNECTIONS: {ARIA2_CONNECTIONS}")
        print(f"   - SRA_TEMP_DIR: {SRA_TEMP_DIR}")
        print(f"   - FASTQ_OUTPUT_DIR: {FASTQ_OUTPUT_DIR}")
        print(f"   - NAS: {NAS_HOST}:{NAS_PORT}")
        return True
    except Exception as e:
        print(f"❌ config.py 導入失敗: {e}")
        return False


def check_dependencies():
    """檢查 Python 依賴"""
    print("\n" + "=" * 80)
    print("🔍 檢查 Python 依賴")
    print("=" * 80)
    
    dependencies = {
        'paramiko': '用於 NAS SFTP 連接',
        'tqdm': '用於進度條顯示',
    }
    
    all_ok = True
    for module, desc in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module:15} - {desc}")
        except ImportError:
            print(f"❌ {module:15} - {desc} (未安裝)")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  缺少依賴，請執行: pip install -r requirements.txt")
    
    return all_ok


def check_tools():
    """檢查系統工具"""
    print("\n" + "=" * 80)
    print("🔍 檢查系統工具")
    print("=" * 80)
    
    tools = {
        'aria2c': 'aria2 多連接下載器',
        'axel': 'axel 多連接下載器（備用）',
        'curl': 'curl 下載工具',
    }
    
    import shutil
    for tool, desc in tools.items():
        if shutil.which(tool):
            print(f"✅ {tool:15} - {desc}")
        else:
            print(f"⚠️  {tool:15} - {desc} (未安裝，但不是必需)")
    
    return True


def check_sra_toolkit():
    """檢查 SRA Toolkit"""
    print("\n" + "=" * 80)
    print("🔍 檢查 SRA Toolkit")
    print("=" * 80)
    
    try:
        from config import PREFETCH_EXE, FASTERQ_DUMP_EXE, VDB_VALIDATE_EXE
        
        tools = {
            'prefetch': PREFETCH_EXE,
            'fasterq-dump': FASTERQ_DUMP_EXE,
            'vdb-validate': VDB_VALIDATE_EXE,
        }
        
        import shutil
        all_ok = True
        for name, exe in tools.items():
            if shutil.which(exe) or Path(exe).exists():
                print(f"✅ {name:15} - {exe}")
            else:
                print(f"❌ {name:15} - {exe} (未找到)")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        return False


def check_files():
    """檢查必要檔案"""
    print("\n" + "=" * 80)
    print("🔍 檢查必要檔案")
    print("=" * 80)
    
    files = [
        'config.py',
        'complete_downloader.py',
        'nas_uploader.py',
        'requirements.txt',
        'Dockerfile',
        'runs.txt',
    ]
    
    all_ok = True
    for fname in files:
        fpath = Path(fname)
        if fpath.exists():
            print(f"✅ {fname}")
        else:
            print(f"❌ {fname} (不存在)")
            all_ok = False
    
    return all_ok


def check_directories():
    """檢查目錄"""
    print("\n" + "=" * 80)
    print("🔍 檢查目錄結構")
    print("=" * 80)
    
    try:
        from config import SRA_TEMP_DIR, FASTQ_OUTPUT_DIR, FASTQ_TEMP_DIR
        
        dirs = {
            'data': 'data',
            'SRA 臨時': SRA_TEMP_DIR,
            'FASTQ 輸出': FASTQ_OUTPUT_DIR,
            'FASTQ 臨時': FASTQ_TEMP_DIR,
        }
        
        for name, dpath in dirs.items():
            p = Path(dpath)
            if p.exists():
                print(f"✅ {name:15} - {dpath}")
            else:
                print(f"⚠️  {name:15} - {dpath} (不存在，會自動創建)")
        
        return True
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        return False


def check_docker():
    """檢查 Docker 環境"""
    print("\n" + "=" * 80)
    print("🔍 檢查 Docker 環境")
    print("=" * 80)
    
    import subprocess
    
    # 檢查 Docker 是否安裝
    try:
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Docker 已安裝: {result.stdout.strip()}")
        else:
            print(f"❌ Docker 未正確安裝")
            return False
    except Exception as e:
        print(f"❌ Docker 未安裝: {e}")
        return False
    
    # 檢查 Docker 映像
    try:
        result = subprocess.run(
            ['docker', 'images', 'auto_downloader', '--format', '{{.Repository}}:{{.Tag}}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if 'auto_downloader' in result.stdout:
            print(f"✅ Docker 映像已建構: {result.stdout.strip()}")
        else:
            print(f"⚠️  Docker 映像未建構")
            print(f"   執行: docker build -t auto_downloader .")
    except Exception as e:
        print(f"⚠️  無法檢查 Docker 映像: {e}")
    
    return True


def check_runs_file():
    """檢查樣本清單"""
    print("\n" + "=" * 80)
    print("🔍 檢查樣本清單")
    print("=" * 80)
    
    files_to_check = ['runs.txt', 'runs_to_fix.txt']
    
    for fname in files_to_check:
        fpath = Path(fname)
        if fpath.exists():
            with open(fpath, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                print(f"✅ {fname:20} - {len(lines)} 個樣本")
        else:
            if fname == 'runs.txt':
                print(f"❌ {fname:20} - 不存在（必需）")
            else:
                print(f"⚠️  {fname:20} - 不存在（可選）")
    
    return True


def main():
    """主檢查流程"""
    print("=" * 80)
    print("🚀 完整系統檢查")
    print("=" * 80)
    print()
    
    checks = [
        ("配置檔案", check_config),
        ("Python 依賴", check_dependencies),
        ("系統工具", check_tools),
        ("SRA Toolkit", check_sra_toolkit),
        ("必要檔案", check_files),
        ("目錄結構", check_directories),
        ("Docker 環境", check_docker),
        ("樣本清單", check_runs_file),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 檢查 {name} 時發生錯誤: {e}")
            results.append((name, False))
    
    # 總結
    print("\n" + "=" * 80)
    print("📊 檢查總結")
    print("=" * 80)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{status:10} - {name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ 所有檢查通過！系統已就緒")
        print()
        print("接下來可以執行:")
        print("1. 建構 Docker: docker build -t auto_downloader .")
        print("2. 測試下載: docker run --rm -v \"${pwd}\\data:/app/data\" auto_downloader")
    else:
        print("⚠️  某些檢查未通過，請先修復問題")
        print()
        print("常見問題:")
        print("- Python 依賴: pip install -r requirements.txt")
        print("- SRA Toolkit: 需要在 Docker 容器內使用")
        print("- Docker 映像: docker build -t auto_downloader .")
    print("=" * 80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
