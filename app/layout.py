from nicegui import ui
from app.components.sidebar import sidebar

def with_sidebar(page_content):
    with ui.row().classes('w-full h-screen'):
        sidebar()

        # main content
        with ui.column().classes('flex-1 p-6 overflow-auto'):
            page_content()
