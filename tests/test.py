import requests
import os
test_message = "これはテスト用のメッセージです。"

def send_line_api(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('LINE_CHANNEL_ACCESS_TOKEN')}"
    }
    data = {
        "to": "USER_ID",
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

if __name__ == "__main__":
    status_code = send_line_api(test_message)
    if status_code == 200:
        print("メッセージが正常に送信されました。")
    else:
        print(f"メッセージの送信に失敗しました。ステータスコード: {status_code}")