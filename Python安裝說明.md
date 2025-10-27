# ❓ Python 安裝說明 - 常見問題

## 🔍 SETUP.bat 會安裝什麼？

### ❌ **不會**安裝的：

```
❌ Python 3.13（或任何 Python 版本）
   → 這是程式語言本體
   → 需要用戶事先手動安裝
   → 下載：https://www.python.org/downloads/
```

### ✅ **會自動**安裝的：

```
✅ paramiko (Python 套件)
   → SFTP 連接 NAS 的功能模組
   → 透過 pip 安裝

✅ tqdm (Python 套件)
   → 顯示進度條的功能模組
   → 透過 pip 安裝
```

---

## 📦 理解差異

### Python 本身（程式語言）

```
Python 3.10 / 3.11 / 3.12 / 3.13
├── 核心語言解釋器
├── 標準函式庫
└── pip 套件管理器

⚠️ 需要用戶手動下載安裝
🔗 https://www.python.org/downloads/
```

### Python 套件（擴充功能）

```
paramiko、tqdm、numpy、pandas 等
├── 使用 pip 安裝
├── 安裝在 Python 環境中
└── 提供額外功能

✅ SETUP.bat 會自動安裝
📝 pip install paramiko tqdm
```

---

## 🚀 新環境完整流程

### 步驟 0️⃣: 手動安裝 Python（⚠️ 必須先做）

#### Windows 安裝步驟：

1. **下載 Python**

   - 前往：https://www.python.org/downloads/
   - 推薦版本：**Python 3.10、3.11 或 3.12**
   - Python 3.13 也可以，但較新可能有相容性問題

2. **執行安裝程式**

   ```
   ⚠️ 重要！勾選這個選項：
   ☑️ Add Python to PATH

   然後點擊「Install Now」
   ```

3. **驗證安裝**

   ```powershell
   # 開啟 PowerShell 或 CMD
   python --version
   # 應該顯示：Python 3.x.x

   pip --version
   # 應該顯示：pip 24.x from ...
   ```

---

### 步驟 1️⃣: 執行 SETUP.bat（自動安裝套件）

```powershell
cd auto_downloader
.\SETUP.bat
```

**SETUP.bat 會做什麼**：

```
[1/4] 檢查必要檔案
      ✅ 確認 runs.txt 存在
      ✅ 確認 download_progress.json 存在

[2/4] 統計樣本數量
      ✅ 統計 SRR 數量：371 個

[3/4] 檢查 Python 環境與安裝套件 ← 這裡！
      ✅ 檢查 Python 是否已安裝
      ✅ 顯示 Python 版本
      📦 執行：pip install -r requirements.txt --upgrade
      ✅ 安裝 paramiko（SFTP 功能）
      ✅ 安裝 tqdm（進度條）

[4/4] 檢查 SRA Toolkit
      ✅ 驗證 prefetch.exe
      ✅ 驗證 fasterq-dump.exe
```

---

### 步驟 2️⃣: 執行 START.bat（開始下載）

```powershell
.\START.bat
```

**開始自動下載 257 個樣本**

---

## 🔧 Python 版本建議

### ✅ 推薦版本（穩定可靠）

```
Python 3.10.x  ← 最穩定
Python 3.11.x  ← 效能提升
Python 3.12.x  ← 新功能，穩定
```

### ⚠️ 可用但較新

```
Python 3.13.x  ← 最新版，可能有相容性問題
               ← paramiko 和 tqdm 應該都支援
               ← 但建議等幾個月更成熟
```

### ❌ 不建議

```
Python 3.6 或更舊  ← 太舊，不支援
Python 2.x         ← 已停止維護
```

---

## ❓ 常見問題

### Q1: 我需要安裝 Python 3.13 嗎？

**A**: 不需要特定版本。**Python 3.10、3.11 或 3.12 都可以**。3.13 也能用，但建議用穩定版本。

---

### Q2: 我已經有 Python 3.9，需要升級嗎？

**A**: **不需要**。Python 3.7+ 都可以用，3.9 完全沒問題。

---

### Q3: SETUP.bat 說「Python 未安裝」怎麼辦？

**A**: 表示：

1. 您還沒安裝 Python，或
2. Python 沒有加入 PATH 環境變數

**解決方法**：

```powershell
# 檢查 Python 是否真的安裝了
python --version

# 如果顯示錯誤，代表需要：
# 1. 安裝 Python（見上方步驟 0）
# 2. 或重新安裝並勾選「Add Python to PATH」
```

---

### Q4: pip 安裝套件失敗怎麼辦？

**A**: 可能是 pip 版本太舊。

**解決方法**：

```powershell
# 升級 pip
python -m pip install --upgrade pip

# 再次安裝套件
pip install paramiko tqdm
```

---

### Q5: 可以手動安裝套件嗎？

**A**: 可以！如果 SETUP.bat 失敗：

```powershell
# 方法 1: 使用 requirements.txt
pip install -r requirements.txt

# 方法 2: 直接安裝
pip install paramiko tqdm

# 方法 3: 逐個安裝
pip install paramiko
pip install tqdm
```

---

### Q6: 如何確認套件安裝成功？

**A**: 執行以下指令：

```powershell
# 檢查 paramiko
python -c "import paramiko; print(f'✅ paramiko {paramiko.__version__}')"

# 檢查 tqdm
python -c "import tqdm; print(f'✅ tqdm {tqdm.__version__}')"

# 或使用檢查腳本
python check_environment.py
```

---

## 📋 完整安裝檢查清單

### ☐ 步驟 0: 安裝 Python（手動）

```
1. [ ] 下載 Python 3.10/3.11/3.12
2. [ ] 執行安裝程式
3. [ ] ⚠️ 勾選「Add Python to PATH」
4. [ ] 驗證：python --version
5. [ ] 驗證：pip --version
```

### ☐ 步驟 1: 執行 SETUP.bat（自動）

```
1. [ ] cd auto_downloader
2. [ ] .\SETUP.bat
3. [ ] 看到「✅ Python 3.x.x 已安裝」
4. [ ] 看到「✅ Python套件安裝完成」
5. [ ] 看到「✅ 使用本地 sratoolkit」
```

### ☐ 步驟 2: 執行 START.bat（自動）

```
1. [ ] .\START.bat
2. [ ] 看到「檢查 NAS 已完成的檔案」
3. [ ] 看到「跳過 NAS 已有的 114 個」
4. [ ] 看到「將下載 257 個樣本」
5. [ ] 開始處理第一個樣本
```

---

## 🎯 總結

| 項目            | 安裝方式              | 時機                      |
| --------------- | --------------------- | ------------------------- |
| **Python 3.x**  | ⚠️ 手動安裝           | 在執行 SETUP.bat **之前** |
| **paramiko**    | ✅ SETUP.bat 自動安裝 | 執行 SETUP.bat 時         |
| **tqdm**        | ✅ SETUP.bat 自動安裝 | 執行 SETUP.bat 時         |
| **SRA Toolkit** | ✅ 已內建             | 不需安裝（已在資料夾內）  |

---

## 🔗 相關資源

- **Python 官網**: https://www.python.org/downloads/
- **Python 安裝教學**: https://docs.python.org/3/using/windows.html
- **pip 使用說明**: https://pip.pypa.io/en/stable/getting-started/
- **paramiko 文檔**: https://www.paramiko.org/
- **tqdm 文檔**: https://tqdm.github.io/

---

**記住：Python 本身需要手動安裝，Python 套件會由 SETUP.bat 自動安裝！** 🐍✨
