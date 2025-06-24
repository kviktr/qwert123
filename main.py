from fastapi import FastAPI, Request
import requests

app = FastAPI()

# URL веб-приложения Google Apps Script (замени на свой, если нужно)
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbx24V8m_grKsc96BDwZ1z0lRKVHWTUu2NTmkgXsbY_4U_K0meXyPYfGe1pMxlFFr7MT/exec"

# Хранилище задач в памяти
TASKS = {}

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("DEBUG full payload:", data)

    # Новое сообщение с задачей
    if "message" in data:
        message = data["message"]
        text = message.get("text", "")
        if "#задача" in text.lower():
            task_id = message["message_id"]
            task_text = text
            author = message["from"].get("username", f"id{message['from']['id']}")

            TASKS[task_id] = {
                "task_id": task_id,
                "task_text": task_text,
                "author": author,
                "performed": [],
            }

            print(f"Новая задача: {task_id} от {author}")

    # Обработка реакции ✅
    elif "message_reaction" in data:
        reaction = data["message_reaction"]
        print("DEBUG reaction payload:", reaction)

        if (
            "new_reaction" in reaction and
            reaction["new_reaction"] and
            reaction["new_reaction"][0].get("emoji") == "✅"
        ):
            message_id = reaction["message_id"]
            user = reaction["user"].get("username", f"id{reaction['user']['id']}")

            task = TASKS.get(message_id)
            if task and user not in task["performed"]:
                task["performed"].append(user)

                print("Отправлено:", task)
                response = requests.post(SCRIPT_URL, json=task)
                print("Ответ от Google:", response.status_code, response.text)

    return {"ok": True}
