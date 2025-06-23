from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import requests
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SCRIPT_URL = os.getenv("SCRIPT_URL")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

TASKS = {}  # message_id: {task_text, author, performed}

@app.get("/")
async def root():
    return JSONResponse({"ok": True})

@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()

    # Новая задача (с тегом #задача)
    if "message" in data and "text" in data["message"]:
        msg = data["message"]
        text = msg["text"]
        if "#задача" in text:
            message_id = msg["message_id"]
            author = msg["from"].get("username", f"id{msg['from']['id']}")

            TASKS[message_id] = {
                "task_id": str(message_id),
                "task_text": text,
                "author": author,
                "performed": []
            }
            print(f"Новая задача: {message_id} от {author}")

    # Обработка реакции
    elif "message_reaction" in data:
        reaction = data["message_reaction"]
        if reaction["reaction"] == "✅":
            msg_id = reaction["message_id"]
            user = reaction["user"].get("username", f"id{reaction['user']['id']}")

            if msg_id in TASKS:
                if user not in TASKS[msg_id]["performed"]:
                    TASKS[msg_id]["performed"].append(user)

                # Отправляем в Google Таблицу
                requests.post(SCRIPT_URL, json=TASKS[msg_id])
                print(f"Отправлено: {TASKS[msg_id]}")

    return {"ok": True}
