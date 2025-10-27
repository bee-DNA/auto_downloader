#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAS SFTP 上傳模組
上傳 FASTQ 檔案到群暉 NAS
"""

import paramiko
import os
from pathlib import Path
from datetime import datetime
import time
from tqdm import tqdm

class NASUploader:
    """群暉 NAS SFTP 上傳器"""
    
    def __init__(self, host, port, username, password):
        """初始化 SFTP 連接"""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sftp = None
        self.transport = None
        
    def connect(self):
        """建立 SFTP 連接"""
        try:
            print(f"🔗 連接到 NAS: {self.host}:{self.port}")
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.connect(username=self.username, password=self.password)
            
            # 設置心跳機制,每60秒發送一次信號以保持連接
            self.transport.set_keepalive(60)

            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            print(f"✅ NAS SFTP 已連接: {self.host}")
            return True
        except Exception as e:
            print(f"❌ SFTP 連接失敗: {e}")
            return False
    
    def disconnect(self):
        """關閉 SFTP 連接"""
        try:
            if self.sftp:
                self.sftp.close()
            if self.transport:
                self.transport.close()
            print(f"✅ SFTP 連接已關閉")
        except Exception as e:
            print(f"⚠️  關閉連接時發生錯誤: {e}")
    
    def create_remote_dir(self, remote_path):
        """在 NAS 上創建目錄"""
        try:
            self.sftp.stat(remote_path)
            # 目錄已存在
        except FileNotFoundError:
            # 目錄不存在，創建
            try:
                self.sftp.mkdir(remote_path)
                print(f"✅ 創建遠端目錄: {remote_path}")
            except Exception as e:
                # 可能是父目錄不存在，遞迴創建
                parent = str(Path(remote_path).parent)
                if parent != remote_path:
                    self.create_remote_dir(parent)
                    self.sftp.mkdir(remote_path)
    
    def upload_file(self, local_file, remote_path, show_progress=True):
        """
        上傳單個檔案到 NAS
        
        Args:
            local_file: 本地檔案路徑
            remote_path: 遠端目錄路徑
            show_progress: 是否顯示進度
        
        Returns:
            bool: 上傳是否成功
        """
        local_file = Path(local_file)
        if not local_file.exists():
            print(f"❌ 本地檔案不存在: {local_file}")
            return False
        
        # 確保遠端目錄存在
        self.create_remote_dir(remote_path)
        
        # 遠端完整路徑
        remote_file = f"{remote_path}/{local_file.name}"
        
        # 獲取檔案大小
        file_size = local_file.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"📤 上傳: {local_file.name} ({file_size_mb:.1f} MB)")
        
        try:
            start_time = time.time()
            
            if show_progress:
                # 帶進度條的上傳
                uploaded = [0]  # 使用列表避免閉包問題
                
                # 使用 tqdm 建立進度條
                with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"上傳 {local_file.name}") as pbar:
                    self.sftp.put(str(local_file), remote_file, callback=lambda sent, total: pbar.update(sent - pbar.n))
            
            else:
                # 無進度條上傳
                self.sftp.put(str(local_file), remote_file)
            
            # 驗證檔案大小
            remote_size = self.sftp.stat(remote_file).st_size
            if remote_size != file_size:
                print(f"   - ❌ 上傳失敗: 檔案大小不匹配 (本地: {file_size}, 遠端: {remote_size})")
                return False
            
            elapsed = time.time() - start_time
            speed = file_size_mb / elapsed if elapsed > 0 else 0
            
            print(f"  ✅ 上傳完成 ({elapsed:.1f}秒, {speed:.2f} MB/s)")
            return True
            
        except Exception as e:
            print(f"  ❌ 上傳失敗: {e}")
            return False
    
    def upload_fastq_pair(self, run_id, local_dir, remote_base="/homes/bioailab/fastq_data"):
        """
        上傳一對 FASTQ 檔案（_1 和 _2）
        
        Args:
            run_id: 樣本 ID (例如 SRR12345678)
            local_dir: 本地 FASTQ 目錄
            remote_base: NAS 遠端基礎路徑
        
        Returns:
            tuple: (成功, 上傳的檔案數量, 總大小 MB)
        """
        local_dir = Path(local_dir)
        
        # 查找 FASTQ 檔案
        fastq_files = list(local_dir.glob(f"{run_id}_*.fastq"))
        
        if not fastq_files:
            print(f"⚠️  找不到 {run_id} 的 FASTQ 檔案")
            return False, 0, 0
        
        print(f"\n{'='*60}")
        print(f"📤 上傳 {run_id} 到 NAS")
        print(f"{'='*60}")
        
        # 創建樣本子目錄（可選）
        # remote_dir = f"{remote_base}/{run_id}"
        remote_dir = remote_base  # 或直接放在基礎目錄
        
        success_count = 0
        total_size = 0
        
        for fastq_file in fastq_files:
            file_size_mb = fastq_file.stat().st_size / (1024 * 1024)
            total_size += file_size_mb
            
            if self.upload_file(fastq_file, remote_dir, show_progress=True):
                success_count += 1
        
        success = (success_count == len(fastq_files))
        
        if success:
            print(f"✅ {run_id} 上傳完成: {success_count} 個檔案, {total_size:.1f} MB")
        else:
            print(f"⚠️  {run_id} 部分上傳: {success_count}/{len(fastq_files)} 個檔案")
        
        return success, success_count, total_size


def test_connection():
    """測試 NAS 連接"""
    print("="*60)
    print("🧪 測試 NAS SFTP 連接")
    print("="*60)
    
    # NAS 設定
    NAS_HOST = "bioailab.synology.me"
    NAS_PORT = 22
    NAS_USER = "bioailab"
    NAS_PASS = "Ncueailab403"
    
    uploader = NASUploader(NAS_HOST, NAS_PORT, NAS_USER, NAS_PASS)
    
    if uploader.connect():
        print("✅ 連接測試成功")
        
        # 測試列出目錄
        try:
            print("\n📂 NAS 家目錄內容:")
            files = uploader.sftp.listdir(".")
            for f in files[:10]:  # 只顯示前 10 個
                print(f"  - {f}")
        except Exception as e:
            print(f"⚠️  列出目錄失敗: {e}")
        
        uploader.disconnect()
        return True
    else:
        print("❌ 連接測試失敗")
        return False


if __name__ == "__main__":
    # 執行連接測試
    test_connection()
