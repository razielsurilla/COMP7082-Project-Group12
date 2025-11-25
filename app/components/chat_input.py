from nicegui import ui

class ChatInput:
    def __init__(self, on_send):
        self.on_send = on_send
        self.input_box = None

    def render(self):
        with ui.row().classes(
            "w-full p-4 bg-gray-100 gap-3 items-center border-t"
        ):
            with ui.row().classes("w-full items-center"):
                self.input_box = (
                    ui.input(placeholder="Type your message...")
                    .classes("flex-1")
                    .props("clearable")
                )
                self.input_box.on('keydown', self._on_key)

                
                ui.button(on_click=self._submit).props('icon=send').classes("bg-blue-500 text-white px-4 py-2 rounded-lg")

    def _on_key(self, e):
        if e.args.get('key') == 'Enter':
            self._submit(e)

    def _submit(self, _):
        text = self.input_box.value
        if not text:
            return
        self.input_box.set_value("")
        self.on_send(text)
