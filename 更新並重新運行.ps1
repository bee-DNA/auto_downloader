# 在 Docker 機器上更新代碼並重新構建

# 1. 拉取最新代碼
cd D:\auto_downloader
git pull origin main

# 2. 重新構建 Docker 映像（包含修正後的代碼）
docker build -t auto_downloader .

# 3. 確認 runs_to_fix.txt 在 data 目錄
Copy-Item runs_to_fix.txt data\ -Force

# 4. 運行修正後的版本
docker run --rm -v "${PWD}\data:/app/data" -e RUNS_FILE=/app/data/runs_to_fix.txt auto_downloader
