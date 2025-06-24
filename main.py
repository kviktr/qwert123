from fastapi import FastAPI, Request
import os
import requests
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

SCRIPT_URL = os.getenv("SCRIPT_URL")
TASKS = {}  # message_id: {task_text, author, performed}

@app.get("/")
async def root():
    return {"ok": True}

@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()

    # Новая задача
    if "message" in data and "text" in data["message"]:
        msg = data["message"]
        if "#задача" in msg["text"]:
            message_id = msg["message_id"]
            text = msg["text"]
            author = msg["from"].get("username", f"id{msg['from']['id']}")

            TASKS[message_id] = {
                "task_id": str(message_id),
                "task_text": text,
                "author": author,
                "performed": []
            }

            print(f"Новая задача: {message_id} от {author}")

    # Реакции
    elif "message_reaction" in data:
        reaction = data["message_reaction"]
        if reaction["reaction"] == "✅":
            message_id = reaction["message_id"]
            user = reaction["user"].get("username", f"id{reaction['user']['id']}")

            task = TASKS.get(message_id)
            if task and user not in task["performed"]:
                task["performed"].append(user)

                print("Отправлено:", task)
                response = requests.post(SCRIPT_URL, json=task)
                print("Ответ от Google:", response.status_code, response.text)

    return {"ok": True}
