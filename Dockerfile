FROM python:3.12

WORKDIR /workspace

COPY . /workspace

RUN pip install -r requirements.txt

# アプリケーションのディレクトリをPythonパスに追加
ENV PYTHONPATH=/workspace/app

# bashは後でpython3 server.pyとかに変えて自動でMCPサーバーが立ち上げるようにする
# CMD ["python3", "app/server.py"]
# CMD [ "bash" ]
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
