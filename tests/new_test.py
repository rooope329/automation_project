from playwright.sync_api import sync_playwright
import requests

def test_connection():
    with sync_playwright() as p:
        # Windows側のChrome(9222番ポート)に接続
        # host.docker.internal は「Dockerから見た自分のPC」のアドレスです
        try:
            #ブラウザから接続指定情報を取得
            response = requests.get(
                "http://host.docker.internal:9222/json/version",
                headers={"Host": "localhost"}
            )
            data = response.json()
            ws_url = data.get('webSocketDebuggerUrl')

            #dockerからブラウザに接続するためのURLを構築
            ws_url = ws_url.replace("localhost", "host.docker.internal:9222")

            browser = p.chromium.connect_over_cdp(
                ws_url,
                headers = {"Host": "localhost"}
            )
            print("接続に成功しました！")
            
            # すでに開いているページ（日経の画面）を取得
            context = browser.contexts[0]
            page = context.pages[0]
            
            # 今のURLを表示して、ログインできているか確認
            print(f"現在のページ: {page.url}")
            page.screenshot(path="connected_check.png")
            print("スクリーンショットを撮りました。")
            
        except Exception as e:
            print(f"接続エラー: {e}")
            print("Windows側でChromeが `--remote-debugging-port=9222` で開いているか確認してください。")

if __name__ == "__main__":
    test_connection()