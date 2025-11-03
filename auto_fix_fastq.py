#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動修復 NAS FASTQ 檔案
整合檢查、刪除多餘檔案、生成待下載列表
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 80)
    print("🔧 FASTQ 檔案自動修復工具")
    print("=" * 80)
    
    # 步驟 1: 檢查並生成報告
    print("\n[1/3] 🔍 檢查 NAS 上的檔案...")
    try:
        result = subprocess.run(
            [sys.executable, "verify_and_fix_fastq.py"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ 檢查失敗: {e}")
        return
    
    # 步驟 2: 刪除多餘檔案（如果有）
    delete_list = Path("files_to_delete.txt")
    if delete_list.exists():
        print(f"\n[2/3] 🗑️  刪除多餘/異常檔案...")
        try:
            result = subprocess.run(
                [sys.executable, "delete_extra_files.py"],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ 刪除失敗: {e}")
            print("⚠️  請手動執行: python delete_extra_files.py")
    else:
        print(f"\n[2/3] ✅ 沒有需要刪除的檔案")
    
    # 步驟 3: 提示重新下載
    runs_to_fix = Path("runs_to_fix.txt")
    if runs_to_fix.exists():
        with open(runs_to_fix, 'r') as f:
            count = len([line for line in f if line.strip()])
        
        print(f"\n[3/3] 📥 需要重新下載 {count} 個樣本")
        print(f"\n執行以下命令重新下載:")
        print(f"   docker run --rm -v \"${{pwd}}\\data:/app/data\" -e RUNS_FILE=runs_to_fix.txt -e MAX_WORKERS=8 auto_downloader")
        print(f"\n或修改 runs.txt 為 runs_to_fix.txt 的內容後執行:")
        print(f"   docker run --rm -v \"${{pwd}}\\data:/app/data\" -e MAX_WORKERS=8 auto_downloader")
    else:
        print(f"\n[3/3] ✅ 所有樣本都完整，無需重新下載")
    
    print(f"\n{'='*80}")
    print("✅ 修復流程完成")
    print(f"{'='*80}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用戶中斷程序")
    except Exception as e:
        print(f"\n❌ 程序錯誤: {e}")
        import traceback
        traceback.print_exc()
