FROM mcr.microsoft.com/playwright/python:v1.58.0-noble

WORKDIR /app

#依存パッケージインストール
COPY docker/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm -rf /tmp/requirements.txt 

#ブラウザインストール
RUN playwright install chromium --with-deps

COPY . .


CMD ["python", "src/main.py"]
