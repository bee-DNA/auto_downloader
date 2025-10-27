# 🚚 移植指南 - 如何移動到其他電腦

## 📋 移植流程

這個 `auto_downloader` 資料夾是**完全獨立**的系統，可以移動到任何有 Python 和 SRA Toolkit 的電腦使用。

### ✅ 移植步驟（3 步驟）

#### 步驟 1: 複製資料夾

```powershell
# 方法1: 複製到USB隨身碟
xcopy auto_downloader E:\auto_downloader /E /I /H

# 方法2: 壓縮後傳輸
# 使用7-Zip或WinRAR壓縮整個auto_downloader資料夾
# 壓縮後大小約 5-10 MB（包含所有工具和配置）

# 方法3: 網路傳輸
# 使用FileZilla、WinSCP等工具上傳到NAS或伺服器
```

#### 步驟 2: 在新電腦解壓（如果有壓縮）

```powershell
# 解壓到任意位置，例如:
D:\auto_downloader
C:\Projects\auto_downloader
E:\SRA\auto_downloader
```

#### 步驟 3: 初始化環境

```batch
# 進入資料夾
cd auto_downloader

# 執行SETUP.bat（會自動檢查並安裝所有需要的東西）
SETUP.bat
```

---

## 🔧 新電腦環境需求

### 必須安裝的軟體

#### 1. Python 3.7+

```powershell
# 檢查是否已安裝
python --version

# 如果未安裝，請下載:
# https://www.python.org/downloads/
# 安裝時務必勾選 "Add Python to PATH"
```

#### 2. SRA Toolkit 3.0+

```powershell
# 檢查是否已安裝
prefetch --version
fasterq-dump --version

# 如果未安裝，有3種方法:

# 方法1: 使用winget（Windows 11推薦）
winget install NCBI.SRA-Toolkit

# 方法2: 手動下載
# 下載: https://github.com/ncbi/sra-tools/wiki/01.-Downloading-SRA-Toolkit
# 解壓後將bin目錄加入PATH

# 方法3: 複製現有的sratoolkit資料夾
# 如果原電腦有sratoolkit，可以一併複製
```

#### 3. 網路連接

- 需要穩定的網路連接到 NCBI 和 NAS
- 建議 100Mbps 以上
- 如果在防火牆後，確保可以訪問:
  - NCBI: ftp.ncbi.nlm.nih.gov
  - NAS: bioailab.synology.me:22

---

## 📁 資料夾完整性檢查

移動後，確認以下檔案都存在：

```
auto_downloader/
├── SETUP.bat              ✅ 初始化腳本
├── START.bat              ✅ 啟動腳本
├── complete_downloader.py ✅ 主程序
├── config.py              ✅ 配置檔案（含NCBI Key）
├── nas_uploader.py        ✅ NAS上傳器
├── check_environment.py   ✅ 環境檢查
├── requirements.txt       ✅ Python依賴清單
├── runs.txt              ✅ 樣本清單（606個）
├── download_progress.json ✅ 進度記錄
├── README.md             ✅ 說明文件
├── QUICK_START.md        ✅ 快速參考
├── SOLUTION.md           ✅ 技術方案
├── FILES.md              ✅ 檔案說明
└── PORTABLE_GUIDE.md     ✅ 本移植指南
```

**快速檢查**:

```batch
# 在auto_downloader目錄執行
dir *.py *.bat *.txt *.json *.md
```

應該看到至少 13 個檔案。

---

## ⚙️ 配置說明

### config.py - 核心配置檔案

所有重要配置都在 `config.py`，**已預先配置好**：

```python
# NCBI API Key（已配置，無需修改）
NCBI_API_KEY = "cbc34d71d57af75c93952af5d6b51d58d008"

# NAS設定（已配置，無需修改）
NAS_HOST = "bioailab.synology.me"
NAS_PORT = 22
NAS_USER = "bioailab"
NAS_PASS = "Ncueailab403"

# 本地路徑（可根據新電腦調整）
SRA_TEMP_DIR = "D:\\sra_temp"      # SRA臨時目錄（60GB）
FASTQ_TEMP_DIR = "D:\\tmp"         # FASTQ臨時目錄（180GB）
FASTQ_OUTPUT_DIR = "D:\\tmp\\fastq_output"

# 線程配置（已優化，無需修改）
MAX_WORKERS = 6        # 6個樣本並行
FASTERQ_THREADS = 5    # 每個樣本5線程
```

### 如果新電腦硬碟配置不同

如果新電腦沒有 D 槽，或者空間不足，需要修改 `config.py`：

```python
# 例如改用 E 槽
SRA_TEMP_DIR = "E:\\sra_temp"
FASTQ_TEMP_DIR = "E:\\tmp"
FASTQ_OUTPUT_DIR = "E:\\tmp\\fastq_output"

# 或改用 C 槽（確保有至少200GB空間）
SRA_TEMP_DIR = "C:\\SRA\\sra_temp"
FASTQ_TEMP_DIR = "C:\\SRA\\tmp"
FASTQ_OUTPUT_DIR = "C:\\SRA\\tmp\\fastq_output"
```

**注意**: 修改後需要確保：

- SRA 臨時目錄至少 60GB
- FASTQ 臨時目錄至少 180GB
- 建議使用 SSD 以提升速度

---

## 🚀 移植後首次啟動

### 1. 執行環境檢查

```batch
cd auto_downloader
SETUP.bat
```

SETUP.bat 會自動：

- ✅ 檢查 Python 版本
- ✅ 安裝必要的 Python 套件（paramiko、tqdm）
- ✅ 檢查 SRA Toolkit
- ✅ 檢查必要檔案（runs.txt、download_progress.json）
- ✅ 統計樣本數量

### 2. 檢查配置

```batch
python config.py
```

應該會看到：

```
====================================
📋 配置檔案檢查
====================================

1️⃣ 檢查本地目錄:
📁 創建目錄: D:\sra_temp
📁 創建目錄: D:\tmp
📁 創建目錄: D:\tmp\fastq_output

2️⃣ 檢查必要檔案:
✅ 所有必要檔案存在

3️⃣ 配置摘要:
  - NCBI API Key: cbc34d71d5...
  - NAS 主機: bioailab.synology.me:22
  - 並行數: 6
  - 單樣本線程: 5
  - 總線程: 30

✅ 配置檔案正常
```

### 3. 測試 NAS 連接

```batch
python -c "from nas_uploader import test_connection; test_connection()"
```

應該會看到：

```
====================================
🧪 測試 NAS SFTP 連接
====================================
🔗 連接到 NAS: bioailab.synology.me:22
✅ SFTP 連接成功

📂 NAS 家目錄內容:
  - Bee_metagenomics
  - ...

✅ 連接測試成功
```

### 4. 啟動下載器

```batch
START.bat
```

---

## 🔍 常見問題

### Q1: Python 版本不符

```
❌ 錯誤: Python 3.6 不支援
```

**解決**: 安裝 Python 3.7 或更高版本

- 下載: https://www.python.org/downloads/
- 建議安裝 Python 3.11（經過測試）

### Q2: SRA Toolkit 未找到

```
❌ SRA Toolkit未安裝或未加入PATH
```

**解決**:

1. 確認 SRA Toolkit 已安裝
2. 將 `bin` 目錄加入系統 PATH:
   - 控制台 → 系統 → 進階系統設定 → 環境變數
   - 編輯 PATH，加入: `C:\sratoolkit\bin`（根據實際路徑）

### Q3: 無法連接到 NAS

```
❌ NAS連接失敗: [Errno 11001] getaddrinfo failed
```

**解決**:

1. 檢查網路連接
2. 確認可以 ping 通 NAS:
   ```powershell
   ping bioailab.synology.me
   ```
3. 檢查防火牆設定
4. 如果在校外，可能需要 VPN

### Q4: 硬碟空間不足

```
❌ 錯誤: [Errno 28] No space left on device
```

**解決**:

1. 檢查硬碟空間: `dir D:\`
2. 確保至少有 200GB 可用空間
3. 或修改 `config.py` 改用其他硬碟

### Q5: paramiko 安裝失敗

```
❌ 錯誤: Microsoft Visual C++ 14.0 is required
```

**解決**:

1. 安裝 Microsoft C++ Build Tools:
   https://visualstudio.microsoft.com/downloads/
2. 或下載預編譯的 wheel:
   ```powershell
   pip install paramiko --prefer-binary
   ```

---

## 📊 移植檢查清單

使用此清單確保移植成功：

- [ ] 複製完整的 auto_downloader 資料夾
- [ ] 新電腦已安裝 Python 3.7+
- [ ] 新電腦已安裝 SRA Toolkit
- [ ] SRA Toolkit 的 bin 已加入 PATH
- [ ] 執行 `SETUP.bat` 無錯誤
- [ ] 執行 `python config.py` 顯示正常
- [ ] NAS 連接測試成功
- [ ] 確認硬碟空間充足（至少 200GB）
- [ ] 檢查 `runs.txt` 存在（606 個樣本）
- [ ] 檢查 `download_progress.json` 存在

全部打勾後，即可執行 `START.bat` 開始下載！

---

## 💡 進階技巧

### 批量移植（多台電腦）

如果要在多台電腦部署：

```powershell
# 1. 在第一台電腦準備好系統
cd auto_downloader
SETUP.bat

# 2. 壓縮整個資料夾
# 使用7-Zip: auto_downloader.7z

# 3. 複製壓縮檔到其他電腦

# 4. 在每台電腦解壓並執行SETUP.bat
```

### 雲端同步

可以將 auto_downloader 放在雲端硬碟：

```
OneDrive\auto_downloader
Google Drive\auto_downloader
Dropbox\auto_downloader
```

但注意：

- ⚠️ **不要同步臨時檔案**（D:\sra_temp、D:\tmp）
- ⚠️ `download_progress.json` 可能需要手動合併

### 使用 Git 管理

可以用 Git 追蹤配置變更：

```powershell
cd auto_downloader
git init
git add *.py *.bat *.txt *.md
git commit -m "Initial portable setup"

# 移植到新電腦
git clone <repository_url>
cd auto_downloader
SETUP.bat
```

---

## 📞 技術支援

如果移植過程中遇到問題：

1. **檢查日誌**:

   ```powershell
   type downloader.log
   ```

2. **執行環境檢查**:

   ```powershell
   python check_environment.py
   ```

3. **查看詳細錯誤**:

   ```powershell
   python complete_downloader.py
   ```

4. **參考其他文檔**:
   - `README.md`: 完整使用說明
   - `FILES.md`: 檔案清單說明
   - `SOLUTION.md`: 技術方案

---

## ✅ 移植成功標誌

當你看到以下輸出，表示移植成功：

```
================================================================================
🚀 開始自動化下載系統
================================================================================

系統配置:
  - 樣本來源: runs.txt
  - NAS已有: 114 個樣本
  - 需下載: 257 個樣本
  - 並行數: 6 個樣本
  - 單樣本線程: 5 線程
  - 總線程: 30 線程（6×5） + 2系統線程

[1/257] 處理: SRR12345678
[1/5] 📥 下載SRA...
```

恭喜！系統已在新電腦上成功運行！🎉
