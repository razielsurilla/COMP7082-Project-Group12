from nicegui import ui
import google.generativeai as genai
import asyncio
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from app.components.chat_message import ChatMessage
from app.components.chat_input import ChatInput
from dbmodule.sql import Sql

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


async def call_gemini(user_text: str):
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")

    prompt = f"""
You convert natural-language scheduling requests into strict JSON instructions.

Today's date is: {today}

Actions:
1. create_event
2. update_event
3. delete_event

CREATE:
{{
    "action": "create_event",
    "event_name": "...",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "description": "...",
    "recurring": true,
    "alerting": true
}}

UPDATE:
{{
    "action": "update_event",
    "event_name": "...",
    "fields": {{
        "event_name": "...",
        "start_date": "...",
        "end_date": "...",
        "description": "..."
    }}
}}

DELETE:
{{
    "action": "delete_event",
    "event_name": "..."
}}

Output only JSON.
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt + "\nUser request: " + user_text)
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.strip("`").replace("json", "").strip()

    return json.dumps(json.loads(raw), indent=2)


def sql_create_event(conn, data):
    query = """
    INSERT INTO events (
        name,
        start_date,
        end_date,
        description,
        is_recurring,
        is_alerting
    ) VALUES (?, ?, ?, ?, ?, ?);
    """

    start_ts = datetime.strptime(data["start_date"], "%Y-%m-%d").timestamp()
    end_ts = datetime.strptime(data["end_date"], "%Y-%m-%d").timestamp()

    values = (
        data["event_name"],
        start_ts,
        end_ts,
        data["description"],
        int(bool(data["recurring"])),
        int(bool(data["alerting"])),
    )

    conn.execute(query, values)


def sql_update_event(conn, data):
    fields = data["fields"]
    sets = []
    values = []

    mapping = {
        "event_name": "name",
        "start_date": "start_date",
        "end_date": "end_date",
        "description": "description",
    }

    for k, v in fields.items():
        col = mapping[k]

        if k in ("start_date", "end_date"):
            v = datetime.strptime(v, "%Y-%m-%d").timestamp()

        sets.append(f"{col} = ?")
        values.append(v)

    values.append(data["event_name"])

    query = f"UPDATE events SET {', '.join(sets)} WHERE name = ?;"
    conn.execute(query, values)


def sql_delete_event(conn, data):
    query = "DELETE FROM events WHERE name = ?;"
    conn.execute(query, (data["event_name"],))


class ChatPage:
    def __init__(self):
        self.messages_container = None
        self.instructions = []

    def _add_message(self, author, text):
        with self.messages_container:
            ChatMessage(author, text).render()
            ui.run_javascript("""
                const el = document.getElementById('messages_container');
                if (el) el.scrollTop = el.scrollHeight;
            """)

    def _apply_instruction(self, instruction):
        sql_db = Sql()
        conn = sql_db.conn
        action = instruction["action"]

        if action == "create_event":
            sql_create_event(conn, instruction)
        elif action == "update_event":
            sql_update_event(conn, instruction)
        elif action == "delete_event":
            sql_delete_event(conn, instruction)

        conn.commit()
        sql_db.terminate()

    async def _send_message(self, user_text: str):
        self._add_message("user", user_text)
        await asyncio.sleep(0)
        bot_reply = await call_gemini(user_text)
        instruction = json.loads(bot_reply)
        self._apply_instruction(instruction)
        self._add_message("bot", bot_reply)

    def show(self):
        with ui.column().classes("w-3/4 h-screen mx-auto justify-center"):
            with ui.column().classes("flex flex-col h-7/8 w-full"):
                self.messages_container = ui.column().classes(
                    "flex-1 overflow-y-auto w-full p-4 gap-2 bg-gray-50"
                ).props("id=messages_container")

                ChatInput(
                    on_send=lambda text: asyncio.create_task(
                        self._send_message(text)
                    )
                ).render()
