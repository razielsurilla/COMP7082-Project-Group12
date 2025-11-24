from nicegui import ui

class ChatMessage:
    def __init__(self, author, text):
        self.author = author
        self.text = text

    def render(self):
        alignment = "self-end" if self.author == "user" else "self-start"
        bubble_color = "bg-blue-200" if self.author == "user" else "bg-gray-200"

        with ui.column().classes(f"{alignment} max-w-[70%] my-1 px-3 py-2 rounded-xl {bubble_color}"):
            ui.label(self.text).classes("text-sm whitespace-pre-wrap")
