# FASTQ 檔案檢查與修復指南

## 🎯 目的

確保 NAS 上的 FASTQ 檔案與 `runs.txt` 完全一致：
- ✅ 所有樣本都有成對的 `_1.fastq` 和 `_2.fastq`
- ✅ 刪除多餘的檔案
- ✅ 補齊缺失的樣本

## 📋 工具說明

### 1. `verify_and_fix_fastq.py` - 檢查工具
檢查 NAS 上的檔案並生成報告：
- 完整樣本（有 _1 和 _2）
- 不完整樣本（只有 _1 或 _2）
- 缺失樣本（runs.txt 有但 NAS 沒有）
- 多餘樣本（NAS 有但 runs.txt 沒有）
- 異常檔名
- 檔案大小異常

**生成文件：**
- `runs_to_fix.txt` - 需要重新下載的樣本列表
- `files_to_delete.txt` - 需要刪除的檔案列表

### 2. `delete_extra_files.py` - 刪除工具
根據 `files_to_delete.txt` 刪除 NAS 上的多餘/異常檔案

### 3. `auto_fix_fastq.py` - 自動修復工具
整合上述兩個工具，自動完成檢查和刪除流程

## 🚀 使用方法

### 方法 1：手動執行（推薦，可控制每一步）

#### 步驟 1：檢查檔案
```powershell
python verify_and_fix_fastq.py
```

**輸出範例：**
```
📊 檢查結果
================================================================================
✅ 完整樣本（有 _1 和 _2）: 450
⚠️  不完整樣本（缺少 _1 或 _2）: 5
❌ 缺失樣本（runs.txt 有但 NAS 沒有）: 2
🗑️  多餘樣本（NAS 有但 runs.txt 沒有）: 3
⚠️  異常檔名: 1

✅ 已生成 runs_to_fix.txt（7 個樣本需要重新下載）
✅ 已生成 files_to_delete.txt（11 個檔案需要刪除）
```

#### 步驟 2：刪除多餘檔案（可選）
```powershell
python delete_extra_files.py
```

程式會顯示要刪除的檔案並要求確認：
```
⚠️  確定要刪除這 11 個檔案嗎？(yes/no):
```

#### 步驟 3：重新下載缺失樣本
使用 `runs_to_fix.txt` 重新下載：

**選項 A：使用環境變數**
```powershell
docker run --rm -v "${pwd}\data:/app/data" -e RUNS_FILE=runs_to_fix.txt -e MAX_WORKERS=8 auto_downloader
```

**選項 B：替換 runs.txt**
```powershell
# 備份原始 runs.txt
Copy-Item runs.txt runs.txt.backup

# 使用待修復列表
Copy-Item runs_to_fix.txt runs.txt

# 執行下載
docker run --rm -v "${pwd}\data:/app/data" -e MAX_WORKERS=8 auto_downloader

# 還原原始 runs.txt
Move-Item runs.txt.backup runs.txt -Force
```

### 方法 2：自動執行（快速但較少控制）

```powershell
python auto_fix_fastq.py
```

這會自動執行檢查和刪除，然後提示您重新下載缺失樣本。

## 📊 檢查項目說明

### 1. 完整樣本
樣本同時有 `{run_id}_1.fastq` 和 `{run_id}_2.fastq`

**狀態：** ✅ 正常

### 2. 不完整樣本
只有 `_1.fastq` 或只有 `_2.fastq`

**原因：**
- 下載過程中斷
- 上傳失敗
- 手動刪除了其中一個

**處理：** 刪除現有檔案，重新下載完整樣本

### 3. 缺失樣本
`runs.txt` 中有但 NAS 上完全沒有

**原因：**
- 尚未下載
- 下載失敗
- 被誤刪

**處理：** 重新下載

### 4. 多餘樣本
NAS 上有但 `runs.txt` 中沒有

**原因：**
- runs.txt 被修改過
- 測試樣本
- 錯誤上傳

**處理：** 刪除（如果確定不需要）

### 5. 異常檔名
不符合 `{run_id}_1.fastq` 或 `{run_id}_2.fastq` 格式

**範例：**
- `ERR123456.fastq`（缺少 _1 或 _2）
- `ERR123456_1.fastq.tmp`（臨時檔案）
- `test.fastq`（測試檔案）

**處理：** 刪除

### 6. 檔案大小異常
成對的 `_1.fastq` 和 `_2.fastq` 大小相差超過 2 倍

**原因：**
- 下載不完整
- 檔案損壞
- 單端測序被誤標為雙端

**處理：** 標記為異常，建議檢查後重新下載

## 🔍 進階用法

### 只檢查特定樣本
修改 `runs.txt` 為只包含要檢查的樣本，然後執行 `verify_and_fix_fastq.py`

### 批量刪除模式
如果確定要刪除所有多餘檔案，可以修改 `delete_extra_files.py` 跳過確認：
```python
# 在 delete_files() 函數中註解掉確認部分
# confirm = input(...)
# if confirm.lower() not in ['yes', 'y']:
#     return
```

### 檢查檔案完整性
`verify_and_fix_fastq.py` 會抽查前 50 個樣本的檔案大小。
要檢查所有樣本，修改：
```python
for run_id in complete_samples[:50]:  # 改為 complete_samples
```

## ⚠️ 注意事項

1. **備份重要！** 
   刪除操作不可逆，建議先在測試環境執行

2. **網路連接**
   確保 NAS 連接穩定，大量刪除可能需要較長時間

3. **磁碟空間**
   重新下載前確保有足夠空間

4. **並行數量**
   重新下載時建議使用 `MAX_WORKERS=8` 或更高以加快速度

5. **進度追蹤**
   `complete_downloader.py` 會自動跳過已完成的樣本

## 📝 常見問題

### Q: 為什麼有不完整樣本？
A: 通常是下載或上傳過程中斷導致。刪除後重新下載即可。

### Q: 可以只下載缺失的部分嗎？
A: 不建議。最好刪除不完整的檔案，重新下載完整樣本以確保配對正確。

### Q: 多餘樣本要不要刪除？
A: 如果確定 `runs.txt` 是正確的最終列表，建議刪除以節省空間。

### Q: 檢查工具會修改 NAS 檔案嗎？
A: `verify_and_fix_fastq.py` 只檢查不修改。只有 `delete_extra_files.py` 會刪除檔案。

### Q: 刪除失敗怎麼辦？
A: 檢查：
- NAS 連接是否正常
- 檔案權限是否足夠
- 檔案是否被其他程序佔用

## 🎉 完成後

執行 `verify_and_fix_fastq.py` 確認：
```
✅ 完整樣本（有 _1 和 _2）: 896
⚠️  不完整樣本（缺少 _1 或 _2）: 0
❌ 缺失樣本（runs.txt 有但 NAS 沒有）: 0
🗑️  多餘樣本（NAS 有但 runs.txt 沒有）: 0
⚠️  異常檔名: 0

✅ 沒有需要修復的問題！所有檔案都正確。
```

恭喜！所有 FASTQ 檔案已完整且正確！🎊
