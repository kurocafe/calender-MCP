# calender-MCP
日曜迄


## ディレクトリ構成(適宜変更して)
```bash
mcp-calendar/
├── app/
│   ├── __init__.py
│   ├── server.py           # FastAPIベースのMCPサーバー本体
│   ├── calendar_service.py # Google Calendar操作用モジュール
│   ├── config.py           # 設定や環境変数の読み込み
│   └── utils.py            # 共通関数など（任意）
│
├── credentials.json        # Google CloudからダウンロードしたOAuth認証情報 <= gitからは削除しました（セキュリティー上）、このファイルは必要です
├── token.json              # 認証済みトークン（初回認証後に自動生成）<=　gitからは削除しました（セキュリティ上）、これは自動生成されます（参照：google calendar api のチュートリアル）
│
├── requirements.txt        # pip依存ライブラリ
├── Dockerfile
├── .env                    # 環境変数（Docker Compose用など）
└── README.md
```