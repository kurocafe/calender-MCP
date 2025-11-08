# ===============================
# mcp-server.py
# Google Calendar MCPサーバー
# ===============================

# FastMCP: Claude MCP対応の軽量サーバーフレームワーク
# CallToolResult: Claude MCPツール実行の戻り値オブジェクト
from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult
import requests

# サーバー名を定義（Claude側に表示される名前）
mcp = FastMCP("google-calendar")

# FastAPIで動作しているバックエンドAPIのURL
# （別プロセスでGoogle Calendarとやり取りする想定）
FASTAPI_URL = "http://localhost:8000"


# ===============================
# Claudeが呼び出すツール定義
# ===============================
# Claudeに「list-events」というツールとして認識される
@mcp.tool("list-events")
def list_events() -> CallToolResult:
    """List next 10 Google Calendar events."""

    try:
        # FastAPIサーバーからイベント一覧を取得
        response = requests.get(f"{FASTAPI_URL}/list-events")
        data = response.json()

        # FastAPI側がエラーを返した場合
        if "error" in data:
            return CallToolResult(content=[
                {"type": "text", "text": f"❌ Error: {data['error']}"}
            ])

        # 取得結果が空の場合
        events = data.get("result", [])
        if not events:
            return CallToolResult(content=[
                {"type": "text", "text": "📭 No upcoming events found."}
            ])

        # イベントリストを整形（タイトルと開始時刻をまとめて表示）
        formatted = "\n".join(
            f"• {e.get('summary', '(no title)')} — "
            f"{e['start'].get('dateTime', e['start'].get('date', 'N/A'))}"
            for e in events
        )

        # Claudeに返す結果。CallToolResultはcontentにリスト形式のデータを要求する
        return CallToolResult(content=[
            {"type": "text", "text": f"📅 Upcoming events:\n{formatted}"}
        ])

    except Exception as e:
        # ネットワークエラーやJSONエラーをキャッチして返す
        return CallToolResult(content=[
            {"type": "text", "text": f"⚠️ Failed to fetch events: {e}"}
        ])


# ===============================
# ローカルテスト実行
# ===============================
# Claudeに接続する前に手動で動作確認するためのブロック
if __name__ == "__main__":
    print("Testing tool manually...")
    # 上で定義したツール関数を直接呼び出してテスト
    result = list_events()
    # 結果（テキスト形式）を出力
    print(result.content)
