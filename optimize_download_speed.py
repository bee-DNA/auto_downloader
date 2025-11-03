#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
網路下載速度優化指南和測試工具
"""

import subprocess
import sys
import time
from pathlib import Path

def test_network_speed():
    """測試網路連接速度"""
    print("=" * 80)
    print("🌐 網路速度測試")
    print("=" * 80)
    
    # 測試 DNS 解析
    print("\n1️⃣ 測試 DNS 解析...")
    try:
        import socket
        start = time.time()
        socket.gethostbyname("sra-download.ncbi.nlm.nih.gov")
        dns_time = (time.time() - start) * 1000
        print(f"   ✅ DNS 解析時間: {dns_time:.2f} ms")
    except Exception as e:
        print(f"   ❌ DNS 解析失敗: {e}")
    
    # 測試 NCBI 連接
    print("\n2️⃣ 測試 NCBI 連接...")
    try:
        import urllib.request
        start = time.time()
        urllib.request.urlopen("https://www.ncbi.nlm.nih.gov", timeout=10)
        connect_time = (time.time() - start) * 1000
        print(f"   ✅ 連接時間: {connect_time:.2f} ms")
    except Exception as e:
        print(f"   ❌ 連接失敗: {e}")
    
    # 測試下載速度（小檔案）
    print("\n3️⃣ 測試下載速度...")
    try:
        test_url = "https://ftp.ncbi.nlm.nih.gov/README.ftp"
        start = time.time()
        response = urllib.request.urlopen(test_url, timeout=30)
        data = response.read()
        elapsed = time.time() - start
        size_mb = len(data) / (1024 * 1024)
        speed_mbps = (size_mb * 8) / elapsed
        print(f"   ✅ 下載速度: {speed_mbps:.2f} Mbps")
    except Exception as e:
        print(f"   ❌ 下載測試失敗: {e}")


def show_optimization_tips():
    """顯示優化建議"""
    print("\n" + "=" * 80)
    print("⚡ 下載速度優化建議")
    print("=" * 80)
    
    print("\n💡 方案 1: 增加並行數（最簡單，已預設）")
    print("   當前設定: 8 個並行")
    print("   單個下載: 5 Mbps")
    print("   總吞吐量: 5 × 8 = 40 Mbps")
    print("   ")
    print("   進一步提升（如果資源充足）:")
    print("   docker run --rm -v \"${pwd}\\data:/app/data\" -e MAX_WORKERS=12 auto_downloader")
    print("   總吞吐量: 5 × 12 = 60 Mbps")
    
    print("\n💡 方案 2: 使用 Aspera 加速（需要安裝）")
    print("   Aspera 是 IBM 開發的高速傳輸協議，可提供 10-100 倍速度")
    print("   ")
    print("   安裝步驟:")
    print("   1. 下載 Aspera Connect:")
    print("      https://www.ibm.com/products/aspera/downloads")
    print("   ")
    print("   2. 配置 SRA Toolkit 使用 Aspera:")
    print("      vdb-config --interactive")
    print("      在 Main 選單選擇 ASPERA，設定路徑")
    print("   ")
    print("   3. 啟用 Aspera（預設已啟用）:")
    print("      docker run --rm -v \"${pwd}\\data:/app/data\" -e USE_ASPERA=yes auto_downloader")
    print("   ")
    print("   預期速度: 50-200 Mbps（取決於網路和伺服器）")
    
    print("\n💡 方案 3: 使用更快的鏡像站（中國用戶）")
    print("   NCBI 在中國有鏡像，速度可能更快:")
    print("   - 設定環境變數: NCBI_VDB_CONFIG")
    print("   - 或使用第三方鏡像（如阿里雲）")
    
    print("\n💡 方案 4: 檢查網路瓶頸")
    print("   ✓ 確認不在尖峰時段")
    print("   ✓ 檢查防火牆/防毒軟體是否影響")
    print("   ✓ 使用有線網路而非 WiFi")
    print("   ✓ 關閉其他下載/串流程式")
    
    print("\n💡 方案 5: 夜間/離峰時段下載")
    print("   NCBI 伺服器在美國，離峰時段（亞洲時間上午）可能更快")
    
    print("\n💡 方案 6: 批次下載較小的檔案")
    print("   將 runs.txt 按檔案大小排序，先下載小檔案")


def check_aspera_installation():
    """檢查 Aspera 是否已安裝"""
    print("\n" + "=" * 80)
    print("🔍 檢查 Aspera 安裝狀態")
    print("=" * 80)
    
    # 檢查常見的 Aspera 安裝路徑
    aspera_paths = [
        Path.home() / ".aspera" / "connect" / "bin" / "ascp",
        Path.home() / ".aspera" / "connect" / "bin" / "ascp.exe",
        Path("C:/Program Files/Aspera/Aspera Connect/bin/ascp.exe"),
        Path("C:/Users") / Path.home().name / "AppData/Local/Programs/Aspera/Aspera Connect/bin/ascp.exe",
    ]
    
    found = False
    for path in aspera_paths:
        if path.exists():
            print(f"   ✅ 找到 Aspera: {path}")
            found = True
            break
    
    if not found:
        print("   ❌ 未找到 Aspera")
        print("   ")
        print("   安裝 Aspera 可以提升 10-100 倍下載速度")
        print("   下載: https://www.ibm.com/products/aspera/downloads")
    
    # 檢查 SRA Toolkit 配置
    vdb_config = Path.home() / ".ncbi" / "user-settings.mkfg"
    if vdb_config.exists():
        print(f"\n   ℹ️  SRA Toolkit 配置: {vdb_config}")
        with open(vdb_config, 'r') as f:
            content = f.read()
            if 'ascp' in content.lower():
                print("   ✅ Aspera 已配置在 SRA Toolkit")
            else:
                print("   ⚠️  Aspera 未配置在 SRA Toolkit")
                print("   執行: vdb-config --interactive 進行配置")
    else:
        print("\n   ℹ️  未找到 SRA Toolkit 配置檔")


def main():
    print("=" * 80)
    print("🚀 SRA 下載速度優化工具")
    print("=" * 80)
    
    # 測試網路速度
    test_network_speed()
    
    # 檢查 Aspera
    check_aspera_installation()
    
    # 顯示優化建議
    show_optimization_tips()
    
    print("\n" + "=" * 80)
    print("✅ 檢查完成")
    print("=" * 80)
    print("\n建議:")
    print("1. 當前配置已優化為 8 個並行（40 Mbps 總吞吐量）")
    print("2. 如果需要更快，考慮安裝 Aspera 或增加並行數到 12-16")
    print("3. 重新建構 Docker 映像以套用最新配置:")
    print("   docker build -t auto_downloader .")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用戶中斷程序")
    except Exception as e:
        print(f"\n❌ 程序錯誤: {e}")
        import traceback
        traceback.print_exc()
