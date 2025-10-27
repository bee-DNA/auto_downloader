# 🚀 快速啟動指南

## ⚡ 30 秒開始使用

1. 📂 進入資料夾：`auto_downloader`
2. 🖱️ 雙擊：`START.bat`
3. ⌨️ 按 Enter 開始
4. ☕ 休息 2-3 天，系統自動完成

---

## 📊 系統配置一覽

| 項目         | 配置                    |
| ------------ | ----------------------- |
| **CPU**      | I7-11 代 (8 核 16 線程) |
| **並行數**   | 4 個樣本同時處理        |
| **解壓線程** | 每個樣本 12 線程        |
| **總線程**   | 52 (48 解壓 + 4 系統)   |
| **預估時間** | 2-3 天 (257 個樣本)     |
| **磁碟需求** | D 槽 200GB 可用         |

---

## 📁 檔案說明

```
auto_downloader/
├── START.bat              ← 【雙擊這個】啟動程序
├── complete_downloader.py ← 主程序
├── README.md             ← 完整說明
└── QUICK_START.md        ← 本檔案
```

---

## 🔧 工作流程

```
NAS檢查 → 生成清單 → 4個樣本並行：
    ├─ 下載SRA (5-20分鐘)
    ├─ 解壓FASTQ (3-8分鐘，12線程)
    ├─ 上傳FASTQ到NAS (10-30分鐘)
    ├─ 上傳SRA到NAS (5-15分鐘)
    └─ 清理本地檔案
```

**單個樣本**: 平均 40 分鐘  
**257 個樣本**: 約 42.8 小時（2-3 天）

---

## ⚠️ 啟動前檢查

- [ ] D 槽至少有 200GB 可用空間
- [ ] 網路連接穩定
- [ ] Python 已安裝（3.7+）
- [ ] SRA Toolkit 已加入 PATH
- [ ] NAS 可正常訪問

---

## 🖥️ 啟動方式

### 方式 1: 一鍵啟動（推薦）

```
雙擊 START.bat → 按Enter
```

### 方式 2: PowerShell

```powershell
cd "auto_downloader"
python complete_downloader.py
```

---

## 📊 監控進度

### 實時監控

- 查看終端機輸出
- 顯示當前樣本和成功/失敗數

### 檢查 NAS

```powershell
cd ..
python full_status_report.py
```

### 檢查進度檔案

```powershell
cd ..
python check_progress.py
```

---

## ⏸️ 中斷與恢復

### 安全停止

```
按 Ctrl + C
```

### 繼續運行

```
重新運行 START.bat
程序會自動從中斷處繼續
```

---

## 🔍 路徑說明

### 本地臨時目錄

```
D:\sra_temp\           ← SRA下載（自動清理）
D:\tmp\                ← 解壓臨時（自動清理）
D:\tmp\fastq_output\   ← FASTQ輸出（自動清理）
```

### NAS 目錄

```
/Bee_metagenomics/Bee_metagenomics/fastq_data/  ← FASTQ最終位置
/Bee_metagenomics/Bee_metagenomics/sra_files/   ← SRA備份位置
```

---

## ❓ 常見問題

### Q: 可以中斷後繼續嗎？

**A**: 可以！重新運行即可，會自動跳過已完成的。

### Q: 需要手動清理檔案嗎？

**A**: 不需要，上傳成功後會自動清理。

### Q: CPU 使用率應該是多少？

**A**: 80-100%為正常，表示充分利用 CPU。

### Q: 預估時間準確嗎？

**A**: 取決於網速，40 分鐘/樣本是保守估計。

### Q: 磁碟空間不夠怎麼辦？

**A**: 修改 `MAX_WORKERS` 為 2 或 3，減少並行數。

---

## 🎯 完成後

1. 執行完整性檢查：

   ```powershell
   python full_status_report.py
   ```

2. 同步進度檔案：

   ```powershell
   python sync_progress_with_nas.py
   ```

3. 清理臨時檔案（可選）：
   ```powershell
   Remove-Item "D:\sra_temp\*" -Recurse -Force
   Remove-Item "D:\tmp\*" -Recurse -Force
   ```

---

## 📈 性能優化建議

| 瓶頸     | 解決方案               |
| -------- | ---------------------- |
| 網速慢   | 使用有線網路、晚上下載 |
| 磁碟慢   | 使用 SSD、減少並行數   |
| CPU 滿載 | 降低 FASTERQ_THREADS   |
| RAM 不足 | 減少 MAX_WORKERS       |

---

## 📞 需要幫助？

1. 查看完整說明：`README.md`
2. 檢查終端機錯誤訊息
3. 查看進度檔案：`download_progress.json`

---

**祝下載順利！🎉**
