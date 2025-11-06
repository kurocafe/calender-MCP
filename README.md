# calender-MCP
日曜迄

## 仮想環境作ったよ
```bash
# 作成用コマンド(実行しなくてよい)
python3 -m venv .venv

# 仮想環境有効化
## mac/linux:
source .venv/bin/activate

## win
.venv\Scripts\activate
```

環境は"requirements.txt"にあるよ。

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
├── credentials.json        # Google CloudからダウンロードしたOAuth認証情報
├── token.json              # 認証済みトークン（初回認証後に自動生成）
│
├── requirements.txt        # pip依存ライブラリ
├── Dockerfile
├── .env                    # 環境変数（Docker Compose用など）
└── README.md
```