import os
import time
import json
import urllib.request
import urllib.parse

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENROUTER_KEY = os.environ["OPENROUTER_API_KEY"]

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def telegram(method, data=None):
    url = f"{TELEGRAM_API}/{method}"

    if data:
        data = urllib.parse.urlencode(data).encode()

    request = urllib.request.Request(url, data=data)

    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode())


def ask_ai(message):
    body = json.dumps({
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "你叫沈言，是白风的私人聊天伙伴。"
                    "你说话自然、温柔、偶尔调皮，不要像客服。"
                    "用户叫白风。"
                )
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }).encode()

    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode())

    return data["choices"][0]["message"]["content"]


print("沈言启动了。")

offset = 0

while True:
    try:
        result = telegram("getUpdates", {
            "timeout": 30,
            "offset": offset
        })

        for update in result.get("result", []):
            offset = update["update_id"] + 1

            message = update.get("message")

            if not message or "text" not in message:
                continue

            chat_id = message["chat"]["id"]
            text = message["text"]

            reply = ask_ai(text)

            telegram("sendMessage", {
                "chat_id": chat_id,
                "text": reply
            })

    except Exception as e:
        print("发生错误：", e)
        time.sleep(5)
