# 📦 完整自動化下載系統 - 方案說明

## 🎯 系統概述

為 I7-11 代處理器優化的全自動 SRA 下載、FASTQ 解壓、NAS 上傳系統。

---

## 📂 資料夾結構

```
auto_downloader/
├── START.bat                  ← 【啟動這個】一鍵啟動
├── complete_downloader.py     ← 主程序（Python）
├── check_environment.py       ← 環境檢查工具
├── README.md                  ← 完整使用說明
├── QUICK_START.md             ← 快速參考
└── SOLUTION.md               ← 本檔案（方案說明）
```

**使用方式**: 將整個 `auto_downloader` 資料夾放在任何位置，雙擊 `START.bat` 即可

---

## 🔧 技術架構

### 核心技術

| 技術                   | 用途       | 說明                   |
| ---------------------- | ---------- | ---------------------- |
| **Python 3.7+**        | 主程序語言 | 多線程控制、邏輯處理   |
| **SRA Toolkit**        | 下載與解壓 | prefetch、fasterq-dump |
| **Paramiko**           | SFTP 上傳  | 與群暉 NAS 通訊        |
| **ThreadPoolExecutor** | 並行處理   | 4 個樣本同時處理       |
| **JSON**               | 進度記錄   | download_progress.json |

### 系統配置（I7-11 代優化）

```python
CPU: I7-11代（8核16線程）
├─ MAX_WORKERS = 4         # 4個樣本並行
├─ FASTERQ_THREADS = 12    # 每個樣本12線程解壓
└─ 總線程使用 = 52 (48解壓 + 4系統)
```

**為何這樣配置？**

- 8 核 16 線程 × 3 = 48 線程（充分利用但不過載）
- 預留 4 線程給作業系統和 NAS 上傳
- 避免系統卡頓，保持流暢

---

## 🔄 工作流程詳解

### 第一階段：初始化（1-2 分鐘）

```
1. 環境檢查
   ├─ Python版本 (3.7+)
   ├─ SRA Toolkit (PATH)
   ├─ Paramiko套件
   └─ 磁碟空間 (200GB+)

2. NAS連接
   └─ SFTP連接到 bioailab.synology.me:22

3. 掃描已有檔案
   ├─ 掃描 /fastq_data/ 中的所有FASTQ
   └─ 生成缺少樣本清單

4. 生成下載清單
   └─ 371個SRR樣本 - 114個已有 = 257個需下載
```

### 第二階段：批次下載（2-3 天）

```
4個樣本並行處理，每個樣本5個步驟：

樣本A ─┬─> [步驟1] Prefetch
       │    └─ 下載SRA到 D:\sra_temp\SRR12345678\
       │    └─ 時間: 5-20分鐘（取決於網速和大小）
       │    └─ 大小: 5-15GB
       │
       ├─> [步驟2] Fasterq-dump
       │    └─ 解壓到 D:\tmp\fastq_output\
       │    └─ 使用12線程加速
       │    └─ 時間: 3-8分鐘
       │    └─ 輸出: SRR12345678_1.fastq + _2.fastq
       │    └─ 大小: 15-40GB
       │
       ├─> [步驟3] 上傳FASTQ到NAS
       │    └─ SFTP上傳到 /fastq_data/
       │    └─ 時間: 10-30分鐘
       │    └─ 同時上傳_1和_2
       │
       ├─> [步驟4] 上傳SRA到NAS
       │    └─ SFTP上傳到 /sra_files/SRR12345678/
       │    └─ 時間: 5-15分鐘
       │    └─ 作為備份保存
       │
       └─> [步驟5] 清理本地檔案
            └─ 刪除 D:\tmp\fastq_output\SRR12345678_*.fastq
            └─ 刪除 D:\sra_temp\SRR12345678\
            └─ 更新 download_progress.json

樣本B ─> (同時進行，步驟同上)
樣本C ─> (同時進行，步驟同上)
樣本D ─> (同時進行，步驟同上)

↓ 完成4個後，繼續下一批 ↓

樣本E~H ─> (重複上述流程)
...
樣本253~256 ─> (最後一批)
樣本257 ─> (單獨處理)
```

### 第三階段：完成與驗證

```
1. 更新進度檔案
   └─ 257個全部標記為completed

2. 斷開NAS連接

3. 顯示統計
   ├─ 總耗時
   ├─ 成功數量
   └─ 失敗數量
```

---

## ⏱️ 時間估算

### 單個樣本時間分佈

| 步驟         | 最快        | 平均        | 最慢        | 瓶頸因素       |
| ------------ | ----------- | ----------- | ----------- | -------------- |
| Prefetch     | 5 分鐘      | 10 分鐘     | 20 分鐘     | 網速、檔案大小 |
| Fasterq-dump | 3 分鐘      | 5 分鐘      | 8 分鐘      | CPU、磁碟速度  |
| 上傳 FASTQ   | 10 分鐘     | 20 分鐘     | 30 分鐘     | 上傳速度       |
| 上傳 SRA     | 5 分鐘      | 10 分鐘     | 15 分鐘     | 上傳速度       |
| 清理         | <1 分鐘     | <1 分鐘     | <1 分鐘     | 磁碟速度       |
| **總計**     | **23 分鐘** | **40 分鐘** | **73 分鐘** | -              |

### 257 個樣本總時間

```
4並行計算:
257個樣本 ÷ 4並行 = 64.25批次
64.25批次 × 40分鐘 = 2570分鐘 = 42.8小時

保守估計: 2-3天連續運行
最快情況: 1.5天（網速快、檔案小）
最慢情況: 4天（網速慢、檔案大）
```

---

## 💾 空間需求

### 本地磁碟（D 槽）

```
瞬時峰值需求:
├─ D:\sra_temp\ (4個樣本)
│  └─ 4 × 10GB = 40GB
│
└─ D:\tmp\fastq_output\ (4個樣本)
   └─ 4 × 30GB = 120GB

總需求: 160GB
建議保留: 200GB以上（含緩衝）
```

**空間管理**:

- ✅ 自動清理：上傳完成後立即刪除
- ✅ 最多同時存在 4 個樣本的資料
- ✅ 不會累積，空間使用固定

### NAS 空間

```
FASTQ資料:
257個樣本 × 25GB平均 = 6.4TB

SRA備份:
257個樣本 × 10GB平均 = 2.6TB

總需求: 約9TB
```

---

## 🔐 安全與可靠性

### 斷點續傳

```python
特點:
✅ 每個樣本完成後立即保存進度
✅ 中斷後重啟自動跳過已完成的
✅ 不會重複下載
✅ 支援任意時刻中斷
```

### 錯誤處理

```python
每個步驟都有錯誤捕捉:
├─ Prefetch超時（1小時）→ 記錄失敗，繼續下一個
├─ Fasterq-dump錯誤 → 清理檔案，記錄失敗
├─ 上傳失敗 → 保留本地檔案，記錄失敗
└─ NAS斷線 → 自動重連（Paramiko）
```

### 資料完整性

```python
驗證機制:
✅ Prefetch後檢查SRA檔案是否存在
✅ Fasterq-dump後檢查兩個FASTQ是否都存在
✅ 上傳後NAS會有完整的配對檔案
✅ 保留SRA備份以便重新解壓
```

---

## 🎛️ 可調整參數

### 性能調整

```python
# complete_downloader.py 第16-17行

# 選項1: 高性能（預設）
MAX_WORKERS = 4
FASTERQ_THREADS = 12
# CPU使用: 80-100%
# 速度: 最快
# 適合: 專用下載，無其他任務

# 選項2: 平衡模式
MAX_WORKERS = 3
FASTERQ_THREADS = 12
# CPU使用: 60-80%
# 速度: 快
# 適合: 偶爾使用電腦做輕度工作

# 選項3: 低功耗
MAX_WORKERS = 2
FASTERQ_THREADS = 8
# CPU使用: 40-60%
# 速度: 較慢
# 適合: 長時間後台運行
```

### 超時調整

```python
# complete_downloader.py 第25-27行

# 網速較慢時增加超時:
PREFETCH_TIMEOUT = 7200   # 改為2小時
FASTERQ_TIMEOUT = 7200
UPLOAD_TIMEOUT = 7200
```

### 路徑調整

```python
# complete_downloader.py 第20-22行

# 如果D槽空間不足，改用其他磁碟:
SRA_TEMP_DIR = Path("E:/sra_temp")
TMP_DIR = Path("E:/tmp")
FASTQ_OUTPUT_DIR = Path("E:/tmp/fastq_output")
```

---

## 📊 監控與除錯

### 實時監控

```powershell
# 方式1: 終端機輸出
# 顯示每個樣本的處理過程和時間

# 方式2: 檢查磁碟空間
Get-PSDrive D | Select-Object Used,Free

# 方式3: 檢查CPU使用率
# 工作管理員 → 效能 → CPU
# 正常: 80-100%
```

### 進度檢查

```powershell
# 在data_collector目錄執行
python check_progress.py

# 檢查NAS狀態
python full_status_report.py

# 同步NAS與進度
python sync_progress_with_nas.py
```

### 日誌檢查

```powershell
# 進度檔案
auto_downloader\download_progress.json

# SRA Toolkit日誌
%USERPROFILE%\.ncbi\

# 終端機輸出（即時）
```

---

## 🚨 故障排除

### 問題 1: Prefetch 一直超時

**症狀**: 多個樣本 prefetch 超時

**原因**:

- 網路不穩定
- NCBI 服務器繁忙
- 檔案太大

**解決**:

1. 檢查網路連接（ping test.net）
2. 改用有線網路
3. 增加 `PREFETCH_TIMEOUT` 到 7200
4. 換時段執行（晚上或凌晨）

### 問題 2: Fasterq-dump 錯誤

**症狀**: "Error: Cannot allocate memory"

**原因**:

- RAM 不足
- SRA 檔案損壞
- 磁碟空間不足

**解決**:

1. 關閉其他程序釋放 RAM
2. 減少 `MAX_WORKERS` 到 2
3. 檢查 D 槽空間
4. 重新下載 SRA 檔案

### 問題 3: NAS 上傳超慢

**症狀**: 上傳速度<5MB/s

**原因**:

- 網路壅塞
- NAS 負載高
- Wi-Fi 不穩定

**解決**:

1. 使用有線網路
2. 避開上傳高峰時段
3. 檢查 NAS 系統資源
4. 減少並行數

### 問題 4: 磁碟空間不足

**症狀**: "No space left on device"

**原因**:

- D 槽空間不足
- 清理失敗
- 並行數太多

**解決**:

1. 手動清理:
   ```powershell
   Remove-Item "D:\sra_temp\*" -Recurse -Force
   Remove-Item "D:\tmp\fastq_output\*" -Force
   ```
2. 減少 `MAX_WORKERS` 到 2
3. 改用更大的磁碟

---

## 🎯 使用建議

### 最佳時機

```
✅ 推薦時機:
- 週末或連續假日
- 凌晨啟動（網路較快）
- 不需要使用電腦的時段

❌ 不建議時機:
- 需要用電腦工作時
- 網路不穩定時
- 磁碟空間不足時
```

### 運行前準備

```
1. 清理D槽空間（200GB+）
2. 關閉不必要的程序
3. 設定電腦不休眠
4. 連接有線網路（推薦）
5. 測試NAS連接
```

### 運行中注意

```
1. 定期檢查終端機輸出（每2-4小時）
2. 監控磁碟空間
3. 檢查CPU溫度
4. 避免強制關機
5. 保持網路連接
```

### 完成後處理

```
1. 執行完整性檢查
2. 同步進度檔案
3. 備份 download_progress.json
4. 清理臨時檔案（可選）
5. 驗證NAS資料完整性
```

---

## 📈 效能基準

### 理想環境

```
網速: 100Mbps下載 + 50Mbps上傳
CPU: I7-11代（8核16線程）
RAM: 16GB
磁碟: SSD

單樣本時間: 25-30分鐘
總時間: 約40小時（1.7天）
```

### 一般環境

```
網速: 50Mbps下載 + 20Mbps上傳
CPU: I7-11代
RAM: 8GB
磁碟: HDD

單樣本時間: 40-50分鐘
總時間: 約65小時（2.7天）
```

### 受限環境

```
網速: 20Mbps下載 + 10Mbps上傳
CPU: I5或舊I7
RAM: 8GB
磁碟: HDD

單樣本時間: 60-90分鐘
總時間: 約100小時（4.2天）

建議: 降低MAX_WORKERS到2
```

---

## ✅ 驗證清單

### 啟動前

- [ ] Python 3.7+ 已安裝
- [ ] SRA Toolkit 已加入 PATH
- [ ] Paramiko 套件已安裝
- [ ] D 槽有 200GB 可用
- [ ] NAS 可正常連接
- [ ] 網路穩定

### 運行中

- [ ] CPU 使用率 80-100%
- [ ] 終端機無錯誤訊息
- [ ] D 槽空間充足
- [ ] 進度正常更新

### 完成後

- [ ] 257 個樣本都已完成
- [ ] NAS 有 257×2=514 個 FASTQ
- [ ] NAS 有 257 個 SRA 備份
- [ ] download_progress.json 正確
- [ ] 本地臨時檔案已清理

---

## 📝 總結

這個系統提供了：

✅ **全自動化**: 一鍵啟動，自動完成
✅ **高性能**: 充分利用 I7-11 代性能
✅ **可靠性**: 斷點續傳，錯誤處理
✅ **易用性**: BAT 啟動，詳細說明
✅ **完整性**: FASTQ+SRA 雙重備份

預計在 2-3 天內完成 257 個樣本的下載、解壓、上傳！

---

**祝使用順利！🎉**
