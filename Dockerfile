# 使用官方 Python 映像檔
FROM python:3.9-slim

# 設定環境變數，防止 Python 寫入 .pyc 檔案
ENV PYTHONDONTWRITEBYTECODE 1
# 設定環境變數，確保 Python 輸出不會被緩衝
ENV PYTHONUNBUFFERED 1

# 設定工作目錄
WORKDIR /app

# 安裝必要的系統套件 (wget, tar)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

# 下載並解壓縮 SRA Toolkit for Linux (Ubuntu)
RUN wget https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/3.2.1/sratoolkit.3.2.1-ubuntu64.tar.gz -O sratoolkit.tar.gz && \
    tar -vxzf sratoolkit.tar.gz && \
    rm sratoolkit.tar.gz

# 將 SRA Toolkit 加入到 PATH 環境變數中
ENV PATH="/app/sratoolkit.3.2.1-ubuntu64/bin:${PATH}"

# 複製 requirements.txt 並安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案中的所有其他檔案
COPY . .

# 執行 SRA Toolkit 的 vdb-config 來進行初始設定 (非互動式)
# 這會在家目錄下創建 .ncbi 目錄，避免執行時的首次設定提示
RUN vdb-config --non-interactive

# 執行 check_and_create_paths 函數來創建資料夾
RUN python -c "from config import check_and_create_paths; check_and_create_paths()"

# 設定容器啟動時執行的命令
CMD ["python", "complete_downloader.py"]
