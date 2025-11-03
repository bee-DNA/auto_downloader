# 🔍 診斷 Docker 為何看不到 runs_to_fix.txt

## 問題分析

從輸出可以看到：
```
📄 runs.txt中的SRR樣本: 38 個
```

這說明 Docker 容器讀取的是 `runs.txt`（38 個樣本），而不是 `runs_to_fix.txt`（3 個樣本）。

## 可能的原因

### 1. runs_to_fix.txt 不在 Docker 容器內

Docker 命令：
```powershell
docker run --rm -v "${PWD}\data:/app/data" -e RUNS_FILE=runs_to_fix.txt auto_downloader
```

**問題**：`-v "${PWD}\data:/app/data"` 只掛載了 `data` 目錄，但 `runs_to_fix.txt` 在外面！

容器內檔案結構：
```
/app/
├── data/              ← 掛載點 (D:\auto_downloader\data)
│   ├── fastq_output/
│   ├── sra_temp/
│   └── tmp/
├── runs.txt           ← 容器內原有的檔案
├── complete_downloader.py
└── config.py
```

`runs_to_fix.txt` 應該在 `D:\auto_downloader\`，但**沒有被掛載進容器**！

## 解決方案

### 方案 1：將 runs_to_fix.txt 放入 data 目錄（推薦）

```powershell
# 在 Docker 機器上
cd D:\auto_downloader

# 複製 runs_to_fix.txt 到 data 目錄
Copy-Item runs_to_fix.txt data\

# 修改環境變數指向 data 目錄內的檔案
docker run --rm -v "${PWD}\data:/app/data" -e RUNS_FILE=/app/data/runs_to_fix.txt auto_downloader
```

### 方案 2：掛載整個工作目錄

```powershell
docker run --rm `
  -v "${PWD}:/app" `
  -e RUNS_FILE=runs_to_fix.txt `
  auto_downloader
```

**注意**：這會覆蓋容器內的 `/app` 目錄，包括 Python 腳本！只在確認 Docker 機器上有完整代碼時使用。

### 方案 3：額外掛載 runs_to_fix.txt

```powershell
docker run --rm `
  -v "${PWD}\data:/app/data" `
  -v "${PWD}\runs_to_fix.txt:/app/runs_to_fix.txt" `
  -e RUNS_FILE=runs_to_fix.txt `
  auto_downloader
```

## 檢查步驟

### 1. 確認 runs_to_fix.txt 存在且內容正確

```powershell
# 在 Docker 機器上
cd D:\auto_downloader
cat runs_to_fix.txt
```

應該顯示：
```
ERR372353
ERR372354
ERR372355
```

### 2. 使用推薦方案

```powershell
# 複製檔案到 data 目錄
Copy-Item runs_to_fix.txt data\

# 運行 Docker（注意路徑）
docker run --rm -v "${PWD}\data:/app/data" -e RUNS_FILE=/app/data/runs_to_fix.txt auto_downloader
```

### 3. 驗證容器能看到檔案

```powershell
# 測試容器能否讀取檔案
docker run --rm -v "${PWD}\data:/app/data" auto_downloader cat /app/data/runs_to_fix.txt
```

應該顯示 3 個樣本 ID。

## 預期輸出

正確配置後，應該看到：
```
📄 runs.txt中的SRR樣本: 3 個   ← 注意這裡是 3 個！
📋 進度檔案記錄已完成: 0 個
🔍 正在檢查NAS已有樣本...
✅ NAS已有: 896 個
📊 總共已完成: 896 個
📊 需要下載: 3 個               ← 開始下載

🔽 開始下載 3 個樣本...
```
