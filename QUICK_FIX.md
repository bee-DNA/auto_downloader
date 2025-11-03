# 🚀 快速修復 FASTQ 檔案

## 一鍵檢查（30秒）

```powershell
python verify_and_fix_fastq.py
```

## 三步驟完整修復

### 1️⃣ 檢查檔案（1-2分鐘）
```powershell
python verify_and_fix_fastq.py
```

### 2️⃣ 刪除多餘檔案（如果有，1-5分鐘）
```powershell
python delete_extra_files.py
```
輸入 `yes` 確認刪除

### 3️⃣ 重新下載缺失樣本（如果有）
```powershell
docker run --rm -v "${pwd}\data:/app/data" -e RUNS_FILE=runs_to_fix.txt -e MAX_WORKERS=8 auto_downloader
```

## 🎯 完成確認

再次執行檢查，應該看到：
```
✅ 完整樣本（有 _1 和 _2）: 896
⚠️  不完整樣本: 0
❌ 缺失樣本: 0
🗑️  多餘樣本: 0
⚠️  異常檔名: 0
```

## 📖 詳細說明

查看 `FASTQ_CHECK_GUIDE.md` 了解更多選項和進階用法。

## ⚡ 自動模式（一鍵執行）

```powershell
python auto_fix_fastq.py
```

會自動完成檢查和刪除，然後提示您重新下載。
