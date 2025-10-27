"""
檢查 auto_downloader 目錄的獨立性
"""

from pathlib import Path
import os

print("=" * 70)
print("🔍 檢查 auto_downloader 獨立性")
print("=" * 70)

current_dir = Path(__file__).parent

# 必需的核心檔案
core_files = {
    "config.py": "配置檔案 (API Key, NAS設定, 路徑)",
    "complete_downloader.py": "主程式",
    "nas_uploader.py": "NAS上傳器",
    "runs.txt": "樣本清單 (606個)",
}

# 輔助工具檔案
helper_files = {
    "quick_check.py": "快速環境檢查",
    "verify_system.py": "完整系統驗證",
    "fix_json.py": "JSON修復工具",
    "analyze_failures.py": "失敗分析工具",
    "check_environment.py": "環境檢查工具",
}

# 啟動腳本
startup_files = {
    "START.ps1": "PowerShell啟動腳本",
    "START_EN.bat": "英文版BAT腳本",
}

# 文檔檔案
doc_files = {
    "執行指南.md": "執行說明",
    "問題修復報告.md": "問題修復記錄",
    "NAS檢查驗證報告.md": "NAS檢查說明",
    "JSON修復報告.md": "JSON安全機制",
}

print("\n[1/4] 核心檔案檢查...")
all_core = True
for file, desc in core_files.items():
    path = current_dir / file
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"  {status} {file:30s} {desc}")
    if not exists:
        all_core = False

print("\n[2/4] 輔助工具檢查...")
for file, desc in helper_files.items():
    path = current_dir / file
    exists = path.exists()
    status = "✅" if exists else "⚠️ "
    print(f"  {status} {file:30s} {desc}")

print("\n[3/4] 啟動腳本檢查...")
for file, desc in startup_files.items():
    path = current_dir / file
    exists = path.exists()
    status = "✅" if exists else "⚠️ "
    print(f"  {status} {file:30s} {desc}")

print("\n[4/4] 文檔檔案檢查...")
for file, desc in doc_files.items():
    path = current_dir / file
    exists = path.exists()
    status = "✅" if exists else "⚠️ "
    print(f"  {status} {file:30s} {desc}")

# 檢查依賴
print("\n" + "=" * 70)
print("📦 Python 套件依賴")
print("=" * 70)

dependencies = {
    "paramiko": "NAS SFTP連接 (必需)",
    "tqdm": "進度條顯示 (選用)",
}

for pkg, desc in dependencies.items():
    try:
        __import__(pkg)
        print(f"  ✅ {pkg:20s} {desc}")
    except ImportError:
        print(f"  ❌ {pkg:20s} {desc}")
        print(f"     安裝: pip install {pkg}")

# 檢查外部工具
print("\n" + "=" * 70)
print("🔧 外部工具依賴")
print("=" * 70)

print("  SRA Toolkit:")
parent_dir = current_dir.parent
sra_dir = parent_dir / "sratoolkit.3.2.1-win64" / "bin"

if sra_dir.exists():
    print(f"  ✅ 找到本地 SRA Toolkit")
    print(f"     路徑: {sra_dir}")

    tools = ["prefetch.exe", "fasterq-dump.exe", "vdb-validate.exe"]
    for tool in tools:
        tool_path = sra_dir / tool
        if tool_path.exists():
            print(f"     ✅ {tool}")
        else:
            print(f"     ❌ {tool}")
else:
    print(f"  ⚠️  本地 SRA Toolkit 不存在")
    print(f"     需要: {sra_dir}")
    print(f"     執行 一鍵安裝_SRA_Toolkit.bat 安裝")

# 總結
print("\n" + "=" * 70)
print("📊 獨立性評估")
print("=" * 70)

if all_core:
    print("\n✅ 核心檔案完整!")
    print("\n📁 auto_downloader 目錄 可以獨立執行!")
    print("\n需要:")
    print("  1. Python 3.7+ (含標準庫)")
    print("  2. pip install paramiko  (NAS連接)")
    print("  3. SRA Toolkit (需單獨安裝)")
    print("  4. runs.txt (樣本清單)")
    print("\n🚀 移植步驟:")
    print("  1. 複製整個 auto_downloader 目錄")
    print("  2. 複製 sratoolkit.3.2.1-win64 目錄到同層")
    print("  3. 安裝 Python 和 paramiko")
    print("  4. 執行 python complete_downloader.py")
else:
    print("\n❌ 缺少核心檔案,無法獨立執行")
    print("   請確保所有核心檔案存在")

print("=" * 70)
