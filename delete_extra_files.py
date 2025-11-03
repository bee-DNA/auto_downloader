#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
刪除 NAS 上多餘的 FASTQ 檔案
根據 files_to_delete.txt 刪除指定檔案
"""

import sys
from pathlib import Path
import posixpath

# 導入配置
try:
    from config import *
    from nas_uploader import NASUploader
except ImportError as e:
    print(f"❌ 導入失敗: {e}")
    print("請確保 config.py 和 nas_uploader.py 在同一目錄")
    sys.exit(1)

# NAS 設置
NAS_CONFIG = {
    "host": NAS_HOST,
    "port": NAS_PORT,
    "username": NAS_USER,
    "password": NAS_PASS,
    "fastq_path": NAS_FASTQ_PATH,
    "sra_path": NAS_SRA_PATH,
}


def delete_files():
    """從 files_to_delete.txt 讀取並刪除檔案"""
    delete_list_file = Path("files_to_delete.txt")
    
    if not delete_list_file.exists():
        print(f"❌ 找不到 {delete_list_file}")
        print("請先執行 verify_and_fix_fastq.py 生成刪除列表")
        sys.exit(1)
    
    # 讀取要刪除的檔案列表
    with open(delete_list_file, 'r') as f:
        files_to_delete = [line.strip() for line in f if line.strip()]
    
    if not files_to_delete:
        print("✅ 沒有需要刪除的檔案")
        return
    
    print(f"📋 準備刪除 {len(files_to_delete)} 個檔案")
    print(f"\n前 10 個檔案:")
    for filename in files_to_delete[:10]:
        print(f"   - {filename}")
    if len(files_to_delete) > 10:
        print(f"   ... 還有 {len(files_to_delete) - 10} 個")
    
    # 確認
    confirm = input(f"\n⚠️  確定要刪除這 {len(files_to_delete)} 個檔案嗎？(yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("❌ 已取消")
        return
    
    # 連接 NAS
    print(f"\n🔌 連接 NAS...")
    nas_uploader = NASUploader(
        host=NAS_CONFIG['host'],
        port=NAS_CONFIG['port'],
        username=NAS_CONFIG['username'],
        password=NAS_CONFIG['password']
    )
    
    if not nas_uploader.connect():
        print("❌ NAS 連接失敗")
        sys.exit(1)
    
    print("✅ NAS 連接成功")
    
    try:
        remote_base = NAS_CONFIG['fastq_path']
        success_count = 0
        fail_count = 0
        
        for i, filename in enumerate(files_to_delete, 1):
            remote_path = posixpath.join(remote_base, filename)
            
            try:
                nas_uploader.sftp.remove(remote_path)
                print(f"[{i}/{len(files_to_delete)}] ✅ 已刪除: {filename}")
                success_count += 1
            except FileNotFoundError:
                print(f"[{i}/{len(files_to_delete)}] ⚠️  檔案不存在: {filename}")
                success_count += 1  # 視為成功（檔案已經不存在）
            except Exception as e:
                print(f"[{i}/{len(files_to_delete)}] ❌ 刪除失敗: {filename} - {e}")
                fail_count += 1
        
        print(f"\n{'='*80}")
        print(f"📊 刪除結果")
        print(f"{'='*80}")
        print(f"✅ 成功: {success_count}")
        print(f"❌ 失敗: {fail_count}")
        
        if fail_count == 0:
            # 刪除列表檔案
            delete_list_file.unlink()
            print(f"\n✅ 已刪除 {delete_list_file}")
    
    finally:
        nas_uploader.disconnect()
        print(f"\n✅ NAS 連接已關閉")


if __name__ == "__main__":
    try:
        delete_files()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用戶中斷程序")
    except Exception as e:
        print(f"\n❌ 程序錯誤: {e}")
        import traceback
        traceback.print_exc()
