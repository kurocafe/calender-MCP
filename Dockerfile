FROM python:3.12

WORKDIR /workspace

COPY . /workspace/

RUN pip install google-api-python-client google-auth-httplib2 google-aoth-oauthlib

RUN pip install -r requirements.txt

# bashは後でpython3 server.pyとかに変えて自動でMCPサーバーが立ち上げるようにする
CMD ["bash"]  