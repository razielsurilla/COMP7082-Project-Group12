from nicegui import app, ui
from datetime import date
from app.sharedVars import SharedVars

def buttons():
	shared_variables = SharedVars()
	date_today = date.today()
	app.storage.user.update({shared_variables.ADDEDIT_DATA_KEY: date_today})
	with ui.button(icon="add", on_click=lambda: ui.navigate.to('/add-edit')).classes('z-50') as new_event_button:
		new_event_button.props('fab color=primary')
		new_event_button.classes('fixed bottom-4 right-4 shadow-lg')

	with ui.button(icon="chat_bubble", on_click=lambda: ui.navigate.to('/assistant')).classes('z-50') as assistant_button:
		assistant_button.props('fab color=primary')
		assistant_button.classes('fixed bottom-20 right-4 shadow-lg')
