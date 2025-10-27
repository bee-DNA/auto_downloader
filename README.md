# SRA 自動下載系統# 🚀 獨立自動化下載系統 - 使用說明

## 🚀 快速開始## 🆕 新環境快速啟動

````batch**第一次在新電腦使用？** 查看這些快速指南：

.\SETUP.bat- 🐍 **[Python安裝說明.md](Python安裝說明.md)** - ⚠️ Python 需手動安裝！SETUP.bat 只安裝套件

```- 📖 **[新環境啟動指南.md](新環境啟動指南.md)** - 完整的移植和啟動說明

- 🚀 **[快速啟動卡.md](快速啟動卡.md)** - 一頁精簡版快速參考

當提示時輸入 `Y` 立即開始下載,或輸入 `N` 稍後執行 `START.bat`。

**啟動流程**:

---1. ⚠️ **先確認已安裝 Python 3.7+**（需手動安裝，見 [Python安裝說明.md](Python安裝說明.md)）

2. `.\SETUP.bat` - 自動安裝 Python 套件（paramiko、tqdm）

## 📖 完整說明3. `.\START.bat` - 開始下載 257 個樣本（跳過 NAS 已有的 114 個）



請參閱: **[使用指南.md](./使用指南.md)**---



包含:## �📋 系統簡介

- ✅ 快速開始

- ✅ 新環境設置這是一個**完全獨立可移植**的SRA下載、FASTQ解壓、NAS上傳系統，專為I7-11代處理器優化。

- ✅ 完整故障排除

- ✅ 系統配置說明### 🌟 獨立可移植特性

- ✅ 常見問題解答

- 🎁 **完全獨立**: 包含所有必要的工具和配置，無需依賴外部檔案

---- 📦 **可移植**: 整個資料夾可以移動到任何有Python環境的Windows電腦

- 🔑 **內建配置**: NCBI API Key、NAS設定全部內建在 `config.py`

## 🔧 常用工具- 🛠️ **工具完整**: 包含 SRA Toolkit 3.2.1、NAS 上傳器、環境檢查等所有工具

- 🐍 **自動安裝**: SETUP.bat 自動安裝 Python 套件（paramiko、tqdm）

| 檔案 | 說明 |

|------|------|### 🎯 功能特點

| `SETUP.bat` | **初始化系統** (推薦第一步) |

| `START.bat` | 啟動下載 |- ✅ **完全自動化**: 下載 → 解壓 → 上傳 → 清理，一鍵完成

| `解除封鎖.bat` | 解除 Windows 檔案封鎖 |- ✅ **智能檢測**: 從606個樣本中自動檢查NAS已有檔案，只下載缺少的

| `使用指南.md` | **完整使用文檔** |- ✅ **30線程優化**: 6並行 × 5線程，充分利用I7-11代超線程

- ✅ **斷點續傳**: 支援中斷後繼續，進度自動保存

---- ✅ **雙重備份**: FASTQ和SRA都上傳到NAS

- ✅ **自動清理**: 上傳完成後自動刪除本地檔案，節省空間

## 📊 系統概況- ✅ **自動初始化**: SETUP.bat自動準備所有必要檔案



- **樣本總數:** 606 個### 📦 完整檔案清單

- **已完成:** 349 個 (NAS)

- **待下載:** 257 個```

- **預計時間:** 約 28 小時auto_downloader/ 【獨立可移植資料夾】

- **並行設定:** 6 樣本 × 5 線程 = 30 執行緒├── SETUP.bat              ← 【首次運行】初始化系統

├── START.bat              ← 【啟動下載】雙擊啟動

---├── complete_downloader.py ← 主程序（30線程，從config.py讀取配置）

├── config.py              ← 配置檔案（NCBI Key、NAS設定、路徑等）

## ✅ 獨立運行├── nas_uploader.py        ← NAS SFTP上傳器（獨立模組）

├── check_environment.py   ← 環境檢查工具

此資料夾包含所有必要檔案,可獨立運行:├── requirements.txt       ← Python依賴清單（paramiko等）

- ✅ Python 腳本├── runs.txt              ← 樣本清單（606個，自動複製）

- ✅ SRA Toolkit (或自動下載)├── download_progress.json ← 進度檔案（自動複製）

- ✅ 配置檔案├── README.md             ← 本說明檔

- ✅ 樣本清單├── QUICK_START.md        ← 快速參考

- ✅ 進度記錄├── SOLUTION.md           ← 技術方案

└── FILES.md              ← 檔案說明

複製到任何有 Python 的電腦都能使用!

💡 核心特性:

---  ✅ 所有工具都在這個資料夾

  ✅ 所有配置都在 config.py

**完整說明請看:** [使用指南.md](./使用指南.md)  ✅ 可以整個資料夾複製到其他電腦使用

  ✅ 只需要Python和SRA Toolkit環境
````

---

## 🔧 系統需求

### 必要條件

1. **作業系統**: Windows 10/11
2. **CPU**: I7-11 代（或更高）
3. **RAM**: 建議 16GB 以上
4. **硬碟空間**:
   - D 槽至少 200GB 可用空間（SRA 臨時：80GB + FASTQ 臨時：120GB）
   - 建議 SSD 以提升速度
5. **網路**: 穩定的寬頻連接（建議 100Mbps 以上）

### 軟體需求

1. **Python 3.7+**

   - 下載: https://www.python.org/downloads/
   - 安裝時勾選「Add Python to PATH」

2. **SRA Toolkit 3.2.1**

   - 已包含在專案中：`data_collector/sratoolkit.3.2.1-win64/`
   - 需將 `bin` 目錄加入系統 PATH

3. **Python 套件**
   - `paramiko` (自動安裝)

---

## 🚀 快速開始

### 【重要】首次使用必讀

如果這是**首次使用**或**移動到新電腦**，請先執行：

```batch
SETUP.bat
```

SETUP.bat 會自動：

- ✅ 複製必要檔案（runs.txt、download_progress.json）
- ✅ 安裝 Python 套件（paramiko 等）
- ✅ 檢查環境（Python、SRA Toolkit）
- ✅ 統計樣本數量

### 方法 1: 一鍵啟動（推薦）

1. 進入 `auto_downloader` 資料夾
2. **首次使用**: 雙擊 `SETUP.bat`（只需執行一次）
3. **啟動下載**: 雙擊 `START.bat`
4. 按任意鍵開始

### 方法 2: 手動啟動

1. 開啟 PowerShell 或 CMD
2. 切換到 `auto_downloader` 目錄:
   ```powershell
   cd auto_downloader
   ```
3. 首次使用，安裝依賴:
   ```powershell
   pip install -r requirements.txt
   ```
4. 執行程序:
   ```powershell
   python complete_downloader.py
   ```

### 移動到其他電腦

1. **複製整個 `auto_downloader` 資料夾**
2. 確保新電腦有 Python 和 SRA Toolkit
3. 執行 `SETUP.bat` 檢查環境
4. 執行 `START.bat` 開始下載

💡 提示: 所有配置（NCBI Key、NAS 設定）都在 `config.py` 中，無需修改！

---

## ⚙️ 系統配置

### CPU 線程配置（I7-11 代優化）

```python
MAX_WORKERS = 4         # 4個樣本並行
FASTERQ_THREADS = 12    # 每個樣本12線程
總線程使用 = 48 (解壓) + 4 (上傳/系統) = 52線程
```

**為什麼這樣配置？**

- I7-11 代: 8 核 16 線程
- 4 個樣本並行 × 12 線程 = 48 線程解壓
- 預留 4 線程給系統和 NAS 上傳
- 最大化 CPU 使用率同時避免系統卡頓

### 路徑配置

**本地路徑:**

```python
SRA_TEMP_DIR = "D:/sra_temp"           # SRA下載臨時目錄
TMP_DIR = "D:/tmp"                     # 解壓臨時目錄
FASTQ_OUTPUT_DIR = "D:/tmp/fastq_output"  # FASTQ輸出目錄
```

**NAS 路徑:**

```python
FASTQ路徑: /Bee_metagenomics/Bee_metagenomics/fastq_data
SRA路徑: /Bee_metagenomics/Bee_metagenomics/sra_files
```

### 超時設置

```python
PREFETCH_TIMEOUT = 3600   # 下載超時: 1小時
FASTERQ_TIMEOUT = 5400    # 解壓超時: 1.5小時
UPLOAD_TIMEOUT = 3600     # 上傳超時: 1小時
```

---

## 📊 工作流程

```
1. 🔍 檢查NAS上已有的樣本
   └─ 自動掃描 /Bee_metagenomics/Bee_metagenomics/fastq_data

2. 📋 生成缺少樣本清單
   └─ 從download_progress.json中排除NAS已有的

3. 🚀 開始4個樣本並行處理:

   樣本A ─┬─> [1] Prefetch: 下載SRA到D:\sra_temp\
          ├─> [2] Fasterq-dump: 解壓到D:\tmp\fastq_output\ (12線程)
          ├─> [3] 上傳FASTQ到NAS: /fastq_data/
          ├─> [4] 上傳SRA到NAS: /sra_files/
          └─> [5] 清理本地檔案

   樣本B ─> (同上)
   樣本C ─> (同上)
   樣本D ─> (同上)

4. ✅ 更新進度檔案
   └─ download_progress.json

5. 🔄 繼續下一批樣本...
```

---

## 📈 預估時間

### 單個樣本處理時間

| 步驟         | 大小    | 時間           | 說明              |
| ------------ | ------- | -------------- | ----------------- |
| Prefetch     | 5-15GB  | 5-20 分鐘      | 取決於網速        |
| Fasterq-dump | 15-40GB | 3-8 分鐘       | 12 線程加速       |
| 上傳 FASTQ   | 15-40GB | 10-30 分鐘     | 取決於上傳速度    |
| 上傳 SRA     | 5-15GB  | 5-15 分鐘      | 取決於上傳速度    |
| **總計**     | -       | **23-73 分鐘** | 平均 40 分鐘/樣本 |

### 257 個樣本總時間

- **4 並行**: 257 ÷ 4 × 40 分鐘 = **42.8 小時**
- **保守估計**: **2-3 天連續運行**

💡 **建議**: 週末或假日啟動，讓系統連續運行

---

## 🔍 監控與檢查

### 檢查運行狀態

1. **查看終端機輸出**

   - 即時顯示當前處理的樣本
   - 顯示成功/失敗統計

2. **檢查進度檔案**

   ```powershell
   # 在data_collector目錄執行
   python check_progress.py
   ```

3. **檢查 NAS 檔案**
   ```powershell
   python full_status_report.py
   ```

### 檢查磁碟空間

```powershell
# 檢查D槽空間
Get-PSDrive D | Select-Object Used,Free

# 檢查臨時目錄大小
Get-ChildItem "D:\sra_temp" -Recurse | Measure-Object -Property Length -Sum
Get-ChildItem "D:\tmp" -Recurse | Measure-Object -Property Length -Sum
```

### 檢查 CPU 使用率

- 按 `Ctrl + Shift + Esc` 開啟工作管理員
- 查看「效能」標籤
- 正常情況: CPU 使用率 80-100%

---

## ⚠️ 常見問題

### 1. Prefetch 超時

**原因**: 網路不穩定或檔案太大

**解決方案**:

- 檢查網路連接
- 增加 `PREFETCH_TIMEOUT`
- 使用有線網路而非 Wi-Fi

### 2. Fasterq-dump 錯誤

**原因**: SRA 檔案損壞或磁碟空間不足

**解決方案**:

- 檢查 D 槽可用空間（需要 120GB+）
- 刪除損壞的 SRA 檔案，程序會自動重試
- 檢查 SRA 檔案完整性:
  ```powershell
  vdb-validate D:\sra_temp\SRR12345678\SRR12345678.sra
  ```

### 3. NAS 上傳失敗

**原因**: NAS 連接中斷或權限問題

**解決方案**:

- 測試 NAS 連接:
  ```powershell
  python -c "import paramiko; t = paramiko.Transport(('bioailab.synology.me', 22)); t.connect(username='bioailab', password='Ncueailab403'); print('✅ 連接成功'); t.close()"
  ```
- 檢查 NAS 空間是否充足
- 確認帳號密碼正確

### 4. 磁碟空間不足

**解決方案**:

- 減少 `MAX_WORKERS` (改為 2 或 3)
- 清理臨時檔案:
  ```powershell
  Remove-Item "D:\sra_temp\*" -Recurse -Force
  Remove-Item "D:\tmp\fastq_output\*" -Force
  ```

### 5. 程序中斷後如何繼續

**好消息**: 程序支援斷點續傳！

1. 直接重新運行 `START.bat`
2. 程序會自動:
   - 檢查 NAS 已上傳的檔案
   - 跳過已完成的樣本
   - 從未完成的樣本繼續

---

## 🛠️ 進階配置

### 修改並行數

編輯 `complete_downloader.py`:

```python
MAX_WORKERS = 4  # 改為2或3以節省資源
```

**建議配置:**

- **性能優先**: MAX_WORKERS=4
- **穩定優先**: MAX_WORKERS=2
- **平衡模式**: MAX_WORKERS=3

### 修改解壓線程

```python
FASTERQ_THREADS = 12  # 改為8或16
```

**計算公式:**

```
總線程 = MAX_WORKERS × FASTERQ_THREADS
建議範圍: 32-64線程（I7-11代）
```

### 修改路徑

如果 C 槽或 D 槽空間不足，可修改:

```python
SRA_TEMP_DIR = Path("E:/sra_temp")  # 改為其他磁碟
TMP_DIR = Path("E:/tmp")
FASTQ_OUTPUT_DIR = Path("E:/tmp/fastq_output")
```

---

## 📝 進度檔案說明

`download_progress.json` 格式:

```json
{
  "completed": ["SRR12180936", "SRR12180945", ...],
  "failed": [
    {
      "run_id": "SRR12180999",
      "step": "fasterq-dump",
      "error": "錯誤訊息",
      "time": "2025-10-19T22:30:00"
    }
  ],
  "remaining": []
}
```

**手動編輯** (不建議):

- 如需重新下載某個樣本，從 `completed` 移除該 ID
- 如需跳過某個樣本，加入 `completed`

---

## 🔄 中斷與恢復

### 正常停止

1. 在終端機按 `Ctrl + C`
2. 程序會安全停止當前任務
3. 已完成的樣本會保存在進度檔案

### 強制中斷

1. 如果程序無回應，關閉終端機視窗
2. 重新運行時可能需要清理臨時檔案

### 恢復下載

```powershell
# 重新運行START.bat即可
START.bat
```

程序會自動:

1. 檢查 NAS 已有的檔案
2. 更新進度檔案
3. 從中斷處繼續

---

## 📊 完成後檢查

### 驗證上傳完整性

```powershell
cd data_collector
python full_status_report.py
```

查看:

- ✅ NAS 完整配對數量
- ⚠️ 不完整配對（缺少\_1 或\_2）
- ❌ 失敗樣本數量

### 同步進度檔案

```powershell
python sync_progress_with_nas.py
```

自動將 NAS 上的檔案標記為 completed

---

## 💡 最佳實踐

### 運行前

1. ✅ 確認 D 槽至少有 200GB 可用空間
2. ✅ 確認網路連接穩定
3. ✅ 確認 NAS 可正常訪問
4. ✅ 關閉不必要的程序

### 運行中

1. ✅ 定期檢查終端機輸出
2. ✅ 監控磁碟空間
3. ✅ 避免使用電腦進行高負載任務
4. ✅ 保持系統不休眠

### 運行後

1. ✅ 執行完整性檢查
2. ✅ 清理臨時檔案
3. ✅ 備份進度檔案
4. ✅ 驗證 NAS 上的資料

---

## 📞 疑難排解

### 聯絡資訊

如遇到無法解決的問題:

1. 記錄錯誤訊息
2. 截圖終端機輸出
3. 檢查進度檔案
4. 提供系統資訊（CPU、RAM、磁碟空間）

### 日誌位置

- 終端機輸出（實時）
- `download_progress.json`（進度記錄）
- SRA Toolkit 日誌: `%USERPROFILE%\.ncbi\`

---

## 📄 授權與版權

本工具僅供學術研究使用。

---

**版本**: 1.0
**更新日期**: 2025-10-19
**適用於**: I7-11 代處理器
