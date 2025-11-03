# 🚀 aria2 多連接加速方案

## 問題分析

當前速度慢的根本原因：
- ❌ **單連接下載**: prefetch 每次只用 1 個連接 = 5 Mbps
- ❌ **Docker 限制**: 容器內難以安裝 Aspera
- ✅ **解決方案**: 使用 aria2 多連接下載（16 連接）

## 預期效果

| 方案 | 連接數 | 單檔速度 | 並行數 | 總吞吐量 |
|------|-------|----------|--------|----------|
| **原始 prefetch** | 1 | 5 Mbps | 8 | 40 Mbps |
| **aria2 加速** | 16 | 20-50 Mbps | 8 | 160-400 Mbps |

**預計提升: 4-10 倍！**

---

## 快速測試（1 分鐘）

### 測試單個檔案下載速度

```powershell
# 重建 Docker 映像（包含 aria2）
docker build -t auto_downloader .

# 測試下載一個樣本（ERR372354）
docker run --rm -v "${pwd}\data:/app/data" auto_downloader python aria2_wrapper.py ERR372354
```

觀察輸出的下載速度是否提升到 20-50 Mbps！

---

## 完整部署步驟

### 步驟 1: 重建 Docker 映像（5 分鐘）
```powershell
cd d:\OneDrive\學校上課\課程\四上\auto_downloader
docker build -t auto_downloader .
```

### 步驟 2: 清理異常檔案
```powershell
python delete_extra_files.py
```

### 步驟 3: 使用 aria2 加速下載
```powershell
docker run --rm -v "${pwd}\data:/app/data" `
    -e RUNS_FILE=runs_to_fix.txt `
    -e MAX_WORKERS=8 `
    -e USE_ARIA2=yes `
    -e ARIA2_CONNECTIONS=16 `
    auto_downloader
```

**預計時間: 1-2 小時**（比原本的 5 小時快 3-5 倍！）

---

## 技術原理

### 為什麼 aria2 更快？

1. **多連接下載**: 同時使用 16 個 TCP 連接
   - prefetch: 1 連接 × 5 Mbps = 5 Mbps
   - aria2: 16 連接 × 5 Mbps = 80 Mbps（理論值）
   - 實際: 20-50 Mbps（受伺服器限制）

2. **更好的連接管理**:
   - 自動重試失敗的連接
   - 動態調整連接數
   - 智能分塊下載

3. **斷點續傳**:
   - 網路中斷後可以續傳
   - 不會浪費已下載的部分

### 為什麼不用 Aspera？

| 方案 | 速度 | Docker 支援 | 複雜度 | 推薦 |
|------|------|------------|--------|------|
| **Aspera** | 🚀🚀🚀 極快 (200+ Mbps) | ❌ 困難 | 😓 高 | ⚠️ 本機使用 |
| **aria2** | 🚀🚀 很快 (20-50 Mbps) | ✅ 簡單 | 😊 低 | ✅ **推薦** |
| **prefetch** | 🐌 慢 (5 Mbps) | ✅ 預設 | 😊 低 | ❌ 太慢 |

---

## 進階優化

### 如果 aria2 仍然慢

#### 選項 1: 增加連接數（測試伺服器限制）
```powershell
docker run --rm -v "${pwd}\data:/app/data" `
    -e ARIA2_CONNECTIONS=32 `
    auto_downloader
```

#### 選項 2: 減少並行數（避免競爭）
```powershell
docker run --rm -v "${pwd}\data:/app/data" `
    -e MAX_WORKERS=4 `
    -e ARIA2_CONNECTIONS=32 `
    auto_downloader
```

#### 選項 3: 使用 NCBI 備用鏡像
修改 `aria2_wrapper.py` 中的 mirrors 列表，添加更多鏡像。

---

## 監控下載速度

### 方法 1: Docker 日誌
```powershell
docker ps  # 找到容器 ID
docker logs -f <container_id>
```

### 方法 2: aria2 內建進度
aria2 會顯示：
```
[#1 SIZE:123.4MiB/456.7MiB(27%) CN:16 DL:45.2MiB ETA:2m15s]
```
- `CN:16` = 16 個連接
- `DL:45.2MiB` = 45.2 MiB/s（約 361 Mbps！）
- `ETA:2m15s` = 預計 2 分 15 秒完成

---

## 對比測試

### 測試腳本
```powershell
# 測試 prefetch（慢）
docker run --rm -v "${pwd}\data:/app/data" auto_downloader `
    bash -c "time prefetch ERR372354 --max-size 100GB"

# 測試 aria2（快）
docker run --rm -v "${pwd}\data:/app/data" auto_downloader `
    python aria2_wrapper.py ERR372354
```

比較兩者的下載時間！

---

## 常見問題

### Q1: aria2 顯示 "not found"
```powershell
# 確認 Docker 映像已更新
docker build --no-cache -t auto_downloader .
```

### Q2: 連接數過多導致錯誤
減少連接數:
```powershell
-e ARIA2_CONNECTIONS=8
```

### Q3: 某些檔案下載失敗
aria2_wrapper.py 會自動嘗試 3 個不同的鏡像，如果都失敗，會回退到 prefetch。

---

## 立即行動 ⚡

1. **重建映像**（現在就做！）:
   ```powershell
   docker build -t auto_downloader .
   ```

2. **測試單個檔案**（驗證速度）:
   ```powershell
   docker run --rm -v "${pwd}\data:/app/data" auto_downloader python aria2_wrapper.py ERR372354
   ```

3. **如果速度提升，開始批次下載**:
   ```powershell
   docker run --rm -v "${pwd}\data:/app/data" -e RUNS_FILE=runs_to_fix.txt -e USE_ARIA2=yes auto_downloader
   ```

**預計總時間: 1-2 小時完成全部 42 個樣本！** 🎉
