# 📦 Auto Downloader 檔案清單

## 🎯 完整檔案列表（獨立可移植版本）

```
auto_downloader/ 【完全獨立的資料夾】
│
├── 執行檔案 ==================
├── SETUP.bat                    ← 【首次運行】初始化系統
├── START.bat                    ← 【啟動下載】主程序啟動
│
├── Python程序 ==================
├── complete_downloader.py       ← 主程序（30線程，使用config.py）
├── config.py                    ← ⭐配置檔案（NCBI Key、NAS設定）
├── nas_uploader.py              ← ⭐NAS SFTP上傳器
├── check_environment.py         ← 環境檢查工具
│
├── 依賴管理 ==================
├── requirements.txt             ← ⭐Python套件清單（paramiko等）
│
├── 資料檔案 ==================
├── runs.txt                     ← 樣本清單（606個，自動複製）
├── download_progress.json       ← 進度記錄（自動複製）
│
└── 文檔 ==================
    ├── README.md                ← 完整使用說明
    ├── QUICK_START.md           ← 快速參考
    ├── SOLUTION.md              ← 技術方案說明
    ├── PORTABLE_GUIDE.md        ← ⭐移植指南
    └── FILES.md                 ← 本檔案

💡 標記 ⭐ 的是新增的獨立性檔案
```

## 📋 檔案說明

### 執行檔案

#### 1. `SETUP.bat` ⭐ 首次必須運行

**用途**: 初始化系統，自動準備所有必要檔案

**功能**:

- ✅ 檢查並複製 `download_progress.json`
- ✅ 檢查並複製 `runs.txt`
- ✅ 統計 SRR 樣本數量
- ✅ 檢查 Python 環境
- ✅ 檢查 SRA Toolkit
- ✅ 安裝缺少的 Python 套件

**使用方式**:

```
雙擊 SETUP.bat
```

#### 2. `START.bat` ⭐ 啟動下載

**用途**: 啟動主下載程序

**功能**:

- ✅ 檢查環境
- ✅ 顯示配置
- ✅ 啟動 Python 下載器

**使用方式**:

```
執行SETUP.bat後
雙擊 START.bat
```

### Python 程序

#### 3. `complete_downloader.py` ⭐ 核心程序

**用途**: 自動化下載、解壓、上傳系統（獨立版本）

**新特性**:

- ✅ 從 `config.py` 讀取所有配置
- ✅ 使用 `nas_uploader.py` 模組上傳
- ✅ 完全獨立，無外部依賴

**配置** (從 config.py 讀取):

```python
MAX_WORKERS = 6         # 6個樣本並行
FASTERQ_THREADS = 5     # 每個5線程
總線程 = 30             # 解壓線程
```

**流程**:

1. 導入 config.py 配置和 nas_uploader 模組
2. 從 runs.txt 讀取所有 SRR 樣本
3. 檢查 NAS 已有的樣本
4. 計算需要下載的樣本
5. 6 個樣本並行處理:
   - Prefetch: 下載 SRA
   - Fasterq-dump: 解壓 FASTQ (5 線程)
   - 上傳 FASTQ 到 NAS
   - 上傳 SRA 到 NAS
   - 清理本地檔案
6. 更新進度檔案

#### 4. `config.py` ⭐⭐⭐ 核心配置檔案

**用途**: 所有系統配置的中央管理

**包含配置**:

```python
# NCBI API（已配置）
NCBI_API_KEY = "cbc34d71d57af75c93952af5d6b51d58d008"

# NAS設定（已配置）
NAS_HOST = "bioailab.synology.me"
NAS_PORT = 22
NAS_USER = "bioailab"
NAS_PASS = "Ncueailab403"
NAS_FASTQ_PATH = "/homes/bioailab/Bee_metagenomics/Bee_metagenomics/fastq_data"
NAS_SRA_PATH = "/homes/bioailab/Bee_metagenomics/Bee_metagenomics/sra_files"

# 本地路徑（可自訂）
SRA_TEMP_DIR = "D:\\sra_temp"
FASTQ_TEMP_DIR = "D:\\tmp"
FASTQ_OUTPUT_DIR = "D:\\tmp\\fastq_output"

# 線程配置（已優化）
MAX_WORKERS = 6
FASTERQ_THREADS = 5
```

**修改方式**:
如果要改變配置，只需編輯 `config.py`：

```python
# 例如改用E槽
SRA_TEMP_DIR = "E:\\sra_temp"
FASTQ_TEMP_DIR = "E:\\tmp"
```

**驗證配置**:

```powershell
python config.py
```

#### 5. `nas_uploader.py` ⭐⭐ NAS 上傳模組

**用途**: SFTP 上傳到群暉 NAS

**類別**:

```python
class NASUploader:
    def __init__(host, port, username, password)
    def connect()                    # 建立SFTP連接
    def disconnect()                 # 關閉連接
    def create_remote_dir()          # 創建遠端目錄
    def upload_file()                # 上傳單個檔案
    def upload_fastq_pair()          # 上傳FASTQ對
```

**特點**:

- ✅ 完整的 SFTP 功能
- ✅ 自動創建遠端目錄
- ✅ 支援進度顯示
- ✅ 完整的錯誤處理
- ✅ 可獨立測試

**測試連接**:

```powershell
python -c "from nas_uploader import test_connection; test_connection()"
```

#### 6. `check_environment.py`

**用途**: 環境檢查工具

**檢查項目**:

- Python 版本
- Paramiko 套件
- SRA Toolkit
- 磁碟空間
- NAS 連接

**使用方式**:

```powershell
python check_environment.py
```

#### 7. `requirements.txt` ⭐⭐ Python 依賴清單

**用途**: 列出所有 Python 套件依賴

**內容**:

```
paramiko>=3.0.0    # SFTP上傳到NAS
tqdm>=4.65.0       # 進度條顯示（可選）
```

**安裝方式**:

```powershell
# 方法1: SETUP.bat會自動安裝
SETUP.bat

# 方法2: 手動安裝
pip install -r requirements.txt
```

**檢查已安裝**:

```powershell
pip list
```

### 資料檔案

#### 8. `runs.txt` ⭐ 必要檔案

**用途**: 606 個樣本的完整清單

**來源**: 從 `data_collector/runs.txt` 自動複製

**格式**:

```
SRR10810002
SRR10810003
...
ERR2696421
DRR019499
```

**說明**:

- 包含 SRR、ERR、DRR 樣本
- 下載器只處理 SRR 樣本（371 個）
- ERR 和 DRR 會自動跳過（235 個）

**統計**:

```powershell
# 統計SRR數量
findstr /R "^SRR" runs.txt | find /c /v ""
# 結果: 371
```

#### 9. `download_progress.json` ⭐ 必要檔案

**用途**: 記錄下載進度

**來源**: 從 `data_collector/download_progress.json` 自動複製

**格式**:

```json
{
  "completed": ["SRR12180936", ...],
  "failed": [
    {
      "run_id": "SRR12345678",
      "step": "prefetch",
      "error": "...",
      "time": "2025-10-19T..."
    }
  ],
  "remaining": []
}
```

**更新**:

- 每個樣本完成後自動更新
- 支援斷點續傳

### 說明文件

#### 10. `README.md`

**用途**: 完整使用說明（500+行）

**內容**:

- 系統簡介（包含獨立可移植特性）
- 安裝需求
- 快速開始（含 SETUP.bat 說明）
- 配置說明
- 移植到其他電腦
- 故障排除

#### 11. `QUICK_START.md`

**用途**: 快速參考卡

**內容**:

- 30 秒快速開始
- 配置一覽
- 常見問題

#### 12. `SOLUTION.md`

**用途**: 技術方案說明

**內容**:

- 系統架構
- 工作流程
- 時間估算
- 性能基準

#### 13. `PORTABLE_GUIDE.md` ⭐⭐⭐ 移植指南

**用途**: 如何移動到其他電腦

**內容**:

- 移植流程（3 步驟）
- 新電腦環境需求
- 檔案完整性檢查
- 配置說明（config.py）
- 移植後首次啟動
- 常見問題（Python 版本、SRA Toolkit 等）
- 移植檢查清單
- 進階技巧（批量移植、雲端同步、Git 管理）

**重要章節**:

- 如何修改 config.py 適應新硬碟配置
- 如何檢查移植是否成功
- 如何解決常見環境問題

#### 14. `FILES.md`

**用途**: 本檔案 - 完整檔案清單說明

---

### 額外工具與輔助檔案 (與 SRA Toolkit 相關)

#### 15. `sratoolkit.README` ⭐

**用途**: 指示如何將完整的 SRA Toolkit 放入 `auto_downloader` 以實現完全離線可移植運作。

主要內容：

- 建議複製整個 `sratoolkit.3.2.1-win64` 資料夾（含 `bin`）到本目錄
- 或只複製必要的二進位檔 (`prefetch.exe`, `fasterq-dump.exe`) 及相依 DLL
- 如何設定 NCBI API key（可放在 `config.py` 或作為環境變數）

#### 16. `copy_sratoolkit.ps1` ⭐

**用途**: PowerShell 助手，用來一次性將上層的 `sratoolkit.3.2.1-win64` 複製/同步到本目錄。

使用方式（在 `auto_downloader` 目錄中執行）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\copy_sratoolkit.ps1
```

備註：`SETUP.bat` 會在初始化時檢查是否存在上層的 `sratoolkit.3.2.1-win64`，若發現會詢問使用者是否要自動執行 `copy_sratoolkit.ps1` 來複製到本目錄，以實現真正的獨立移植。

## 🚀 首次使用流程

### 步驟 1: 初始化（首次必須）

```
雙擊 SETUP.bat
```

**SETUP.bat 會自動**:

1. 檢查檔案完整性
2. 從上層目錄複製缺少的檔案:
   - `download_progress.json`
   - `runs.txt`
3. 統計樣本數量
4. 檢查環境
5. 安裝缺少的套件

### 步驟 2: 啟動下載

```
雙擊 START.bat
```

### 步驟 3: 監控進度

```
查看終端機輸出
```

---

## 📊 30 線程配置說明

### 為什麼選擇 30 線程？

**I7-11 代規格**:

- 8 核心
- 16 邏輯線程（超線程）

**30 線程配置**:

```
6個樣本並行 × 5線程/樣本 = 30線程（解壓）
+ 2線程（系統、上傳）
= 32線程總使用
```

**優勢**:

- ✅ 充分利用 CPU（32/16 = 200%）
- ✅ 不會過度負載（保留餘裕）
- ✅ 平衡解壓和上傳速度
- ✅ 系統仍保持流暢

### 與 4 並行 12 線程的比較

| 配置          | 並行數 | 線程/樣本 | 總線程  | CPU 使用 | 速度     |
| ------------- | ------ | --------- | ------- | -------- | -------- |
| **舊版**      | 4      | 12        | 48+4=52 | 100%+    | 較慢     |
| **30 線程版** | 6      | 5         | 30+2=32 | 200%     | **更快** |

**30 線程版優勢**:

- ✅ 更多樣本並行（6 vs 4）
- ✅ 降低單樣本線程（避免競爭）
- ✅ 更快完成時間
- ✅ CPU 超線程充分利用

---

## 📁 檔案來源與移植

### 內建獨立檔案（無需複製）

以下檔案**已內建**在 auto_downloader 資料夾，是完全獨立的：

```
✅ SETUP.bat              - 初始化腳本
✅ START.bat              - 啟動腳本
✅ complete_downloader.py - 主程序
✅ config.py              - 配置檔案（含NCBI Key、NAS設定）
✅ nas_uploader.py        - NAS上傳器
✅ check_environment.py   - 環境檢查
✅ requirements.txt       - Python依賴清單
✅ README.md              - 完整說明
✅ QUICK_START.md         - 快速參考
✅ SOLUTION.md            - 技術方案
✅ PORTABLE_GUIDE.md      - 移植指南
✅ FILES.md               - 本檔案
```

### 自動複製的檔案（首次運行時）

SETUP.bat 會自動從上層目錄複製:

```
data_collector/
├── download_progress.json  → auto_downloader/download_progress.json
├── runs.txt                → auto_downloader/runs.txt
└── auto_downloader/
    ├── SETUP.bat           (執行這個自動複製)
    └── ...
```

### 移植到其他電腦

**完整移植流程**:

1. **複製整個 auto_downloader 資料夾**

   ```powershell
   # 使用USB、網路、壓縮等方式
   xcopy auto_downloader E:\auto_downloader /E /I /H
   ```

2. **新電腦只需要**:

   - Python 3.7+
   - SRA Toolkit 3.0+
   - 網路連接

3. **新電腦執行**:
   ```batch
   cd auto_downloader
   SETUP.bat
   START.bat
   ```

💡 **重要**: 所有配置（NCBI Key、NAS 設定）都在`config.py`中，無需任何修改！

### 手動準備的檔案（特殊情況）

如果 SETUP.bat 無法自動複製，請手動複製:

```powershell
# 在data_collector目錄執行
Copy-Item "download_progress.json" "auto_downloader\"
Copy-Item "runs.txt" "auto_downloader\"
```

---

## 🔄 更新檔案

### 更新 runs.txt

如果樣本清單有變動:

```powershell
Copy-Item "..\runs.txt" "runs.txt" -Force
```

### 更新 download_progress.json

如果需要重置進度:

```powershell
Copy-Item "..\download_progress.json" "download_progress.json" -Force
```

### 更新 config.py 配置

如果需要修改配置（例如改用 E 槽）:

```python
# 編輯 config.py
SRA_TEMP_DIR = "E:\\sra_temp"
FASTQ_TEMP_DIR = "E:\\tmp"
FASTQ_OUTPUT_DIR = "E:\\tmp\\fastq_output"
```

### 備份進度檔案

定期備份:

```powershell
Copy-Item "download_progress.json" "download_progress.json.backup"
```

---

## ✅ 檔案檢查清單

### 執行前確認

- [ ] `SETUP.bat` 存在
- [ ] `START.bat` 存在
- [ ] `complete_downloader.py` 存在
- [ ] `runs.txt` 存在（或執行 SETUP.bat 自動生成）
- [ ] `download_progress.json` 存在（或執行 SETUP.bat 自動生成）

### 執行後檢查

- [ ] `download_progress.json` 正在更新
- [ ] 終端機顯示處理進度
- [ ] D:\sra_temp\ 有檔案（最多 6 個樣本）
- [ ] D:\tmp\fastq_output\ 有檔案（最多 6 個樣本）

---

## 🆘 常見問題

### Q: 找不到 runs.txt？

**A**: 執行 `SETUP.bat`，會自動從上層目錄複製

### Q: 找不到 download_progress.json？

**A**: 執行 `SETUP.bat`，會自動從上層目錄複製

### Q: 可以移動整個 auto_downloader 資料夾嗎？

**A**: 可以！只要確保執行過 `SETUP.bat` 即可

### Q: 需要手動編輯檔案嗎？

**A**: 不需要！`SETUP.bat` 會自動處理一切

---

## 📝 總結

**只需要 3 步驟**:

1. ✅ 雙擊 `SETUP.bat`（首次）
2. ✅ 雙擊 `START.bat`（啟動）
3. ✅ 等待 2-3 天（自動完成）

**所有檔案都會自動準備好！** 🎉
