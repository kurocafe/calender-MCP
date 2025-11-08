FROM python:3.12

WORKDIR /workspace

# ファイルをコピー
COPY . /workspace

# 依存関係をインストール（supervisorも含む）
RUN pip install -r requirements.txt

# Pythonパスを設定
ENV PYTHONPATH=/workspace/app

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]