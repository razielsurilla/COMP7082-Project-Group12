from nicegui import app, ui
from datetime import date, timedelta
from app.sharedVars import SharedVars

def buttons():
	sharedVariables = SharedVars()
	dateToday = date.today()
	app.storage.user.update({sharedVariables.ADDEDIT_DATA_KEY: f"{dateToday.strftime("%B")} {dateToday.day}, {dateToday.year}"})
	with ui.button(icon="add", on_click=lambda: ui.navigate.to('/add-edit')).classes('z-50') as new_event_button:
		new_event_button.props('fab color=primary')
		new_event_button.classes('fixed bottom-4 right-4 shadow-lg')

	with ui.button(icon="chat_bubble", on_click=lambda: ui.navigate.to('/assistant')).classes('z-50') as assistant_button:
		assistant_button.props('fab color=primary')
		assistant_button.classes('fixed bottom-20 right-4 shadow-lg')
