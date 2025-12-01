from nicegui import ui
from app.components.sidebar import sidebar
from app.components.addchat import buttons

def with_sidebar(page_content):
	with ui.row().classes('w-full h-screen'):
		sidebar()
		buttons()

		# main content
		with ui.column().classes('flex-1 overflow-hidden'):
			page_content()


def with_just_sidebar(page_content):
	with ui.row().classes('w-full h-screen'):
		sidebar()
		# main content
		with ui.column().classes('flex-1 overflow-hidden'):
			page_content()
	return None
