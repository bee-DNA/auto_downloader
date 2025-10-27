# 🚀 立即開始使用

## ✅ 系統已準備就緒

**auto_downloader** 是一個完全獨立的 SRA 下載系統，包含所有必要工具。

---

## ⚡ 快速開始（3 步驟）

### 步驟 1️⃣: 初始化（首次必須）

```powershell
cd auto_downloader
.\SETUP.bat
```

**SETUP.bat 會自動**:

- ✅ 檢查必要檔案
- ✅ 安裝 Python 套件
- ✅ 驗證 SRA Toolkit（已內建）
- ✅ 顯示配置摘要

⏱️ **需要時間**: 約 1-2 分鐘

---

### 步驟 2️⃣: 啟動下載

```powershell
.\START.bat
```

**系統會自動**:

- ✅ 從 606 個樣本中篩選 371 個 SRR
- ✅ 檢查 NAS 已有的 114 個樣本
- ✅ 下載缺少的 257 個樣本
- ✅ 6 個樣本並行處理（每個 5 線程）
- ✅ 自動上傳到 NAS
- ✅ 自動清理本地檔案

⏱️ **預計時間**: 約 28 小時

---

### 步驟 3️⃣: 監控進度

**查看終端機輸出**:

```
🔄 [1/257] 處理 SRR12345678...
  ⏬ Prefetch: 2.5 GB (20 分鐘)
  🧬 Fasterq-dump: 解壓中 (5 線程, 40 分鐘)
  ☁️ 上傳 FASTQ: 完成 (15 分鐘)
  ☁️ 上傳 SRA: 完成 (10 分鐘)
  🗑️ 清理: 完成
✅ 完成！
```

**檢查進度檔案**:

```powershell
notepad download_progress.json
```

---

## 📊 系統配置摘要

### 線程配置（30 線程版本）

```
6 個樣本並行
× 5 線程/樣本解壓
= 30 線程（解壓）+ 2 線程（系統）
```

### 樣本統計

```
總樣本: 606 個
處理中: 371 個 SRR（NCBI）
跳過:   235 個 ERR/DRR
已完成: 114 個
需下載: 257 個
```

### 磁碟使用

```
D:\sra_temp:          60 GB（SRA 暫存）
D:\tmp:              180 GB（FASTQ 暫存）
auto_downloader:     104 MB（系統本身）
```

---

## 🔧 環境需求

### 必須項目

✅ **Windows** 作業系統  
✅ **Python 3.7+** 已安裝  
✅ **網路連線** (下載 SRA + 連接 NAS)  
✅ **磁碟空間** (D:\sra_temp: 60GB, D:\tmp: 180GB)

### 已內建項目（無需安裝）

✅ **SRA Toolkit 3.2.1** (103.45 MB, 已包含)  
✅ **NCBI API Key** (已配置在 config.py)  
✅ **NAS 設定** (已配置在 config.py)

---

## 📦 移植到其他電腦

### 方法 1: 直接複製（推薦）

```powershell
# 複製整個 auto_downloader 資料夾到目標機器
# 包含 sratoolkit.3.2.1-win64 子資料夾

# 在目標機器執行
cd auto_downloader
.\SETUP.bat
.\START.bat
```

### 方法 2: 壓縮打包

```powershell
# 壓縮
Compress-Archive -Path auto_downloader -DestinationPath auto_downloader.zip

# 在目標機器解壓後執行
Expand-Archive auto_downloader.zip
cd auto_downloader
.\SETUP.bat
.\START.bat
```

### 配置修改（如果需要）

編輯 `config.py`:

```python
# 例如改用 E 槽
SRA_TEMP_DIR = "E:\\sra_temp"
FASTQ_TEMP_DIR = "E:\\tmp"
```

---

## 🛑 停止或暫停

### 暫停下載

```
按 Ctrl+C 中斷
```

系統會保存進度到 `download_progress.json`，下次啟動會自動從中斷處繼續。

### 重新啟動

```powershell
.\START.bat
```

系統會自動跳過已完成的樣本。

---

## ❓ 常見問題

### Q1: 如何檢查環境？

```powershell
python check_environment.py
```

### Q2: 如何修改配置？

```powershell
notepad config.py
# 修改後儲存即可，無需重新執行 SETUP.bat
```

### Q3: 如何查看已完成的樣本？

```powershell
python -c "import json; print(json.load(open('download_progress.json'))['completed'])"
```

### Q4: SETUP.bat 找不到 SRA Toolkit？

- 確認 `sratoolkit.3.2.1-win64` 資料夾存在
- 確認 `sratoolkit.3.2.1-win64\bin\prefetch.exe` 存在
- 如果缺少，執行 `copy_sratoolkit.ps1` 從上層複製

### Q5: 如何驗證 NCBI API Key？

```powershell
python -c "from config import NCBI_API_KEY; print(NCBI_API_KEY)"
# 應該顯示: cbc34d71d57af75c93952af5d6b51d58d008
```

---

## 📖 完整文檔

需要更多資訊？請參考：

- 📘 **README.md** - 完整使用說明（500+行）
- 📕 **PORTABLE_GUIDE.md** - 移植指南
- 📗 **SOLUTION.md** - 技術方案說明
- 📙 **FILES.md** - 檔案清單說明
- 📔 **MANIFEST.md** - 系統檔案清單
- 📓 **COMPLETION_REPORT.md** - 建置完成報告

---

## ✅ 檢查清單

在啟動前確認：

- [ ] Python 3.7+ 已安裝 (`python --version`)
- [ ] D 槽有足夠空間（至少 240 GB）
- [ ] 網路可連接 NCBI 和 NAS
- [ ] `sratoolkit.3.2.1-win64` 資料夾存在
- [ ] 已執行過 `SETUP.bat`

---

## 🎯 預期結果

**完成後您將獲得**:

- ✅ 257 個 SRR 樣本的 FASTQ 檔案（已上傳到 NAS）
- ✅ 257 個 SRA 備份檔案（已上傳到 NAS）
- ✅ 完整的下載記錄（download_progress.json）
- ✅ 自動清理的本地磁碟空間

**NAS 位置**:

- FASTQ: `/Bee_metagenomics/Bee_metagenomics/fastq_data/`
- SRA: `/Bee_metagenomics/Bee_metagenomics/sra_files/`

---

## 💡 提示

### 提高下載速度

系統已使用 NCBI API Key 和 30 線程優化，無需額外配置。

### 監控系統資源

```powershell
# 打開工作管理員查看 CPU/磁碟使用
taskmgr
```

### 檢查 NAS 連線

```powershell
python -c "from nas_uploader import test_connection; test_connection()"
```

---

## 🎉 就這麼簡單！

**只需 2 個命令**:

```powershell
.\SETUP.bat    # 首次必須
.\START.bat    # 開始下載
```

**等待 28 小時**，系統會自動完成 257 個樣本的下載、解壓、上傳！

---

**建立時間**: 2025 年 10 月 19 日  
**狀態**: ✅ 可立即使用  
**支援**: 查看 README.md 或 PORTABLE_GUIDE.md
