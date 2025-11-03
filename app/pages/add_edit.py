from nicegui import ui
from app.components.date_picker_label import datePickerLabel

# TODO: this should be a component, then home.py should create a Calendar object
class AddEditEvent:
	def __init__(self):
		return None

	def showPage(self):
		with ui.column():
			with ui.row():
				with ui.column():
					ui.input(label='Event Name', placeholder='start typing',
					on_change=lambda e: resultDetail.set_text('you typed: ' + e.value),
					validation={'Input too long': lambda value: len(value) < 20})
					
					datePickerLabel("Start Date", None)
					
					datePickerLabel("End Date", None)
					
					resultDetail = ui.label()
					#toggle
					switch = ui.switch('Set Alerts')
					ui.label('Remind me:').bind_visibility_from(switch, 'value')
				with ui.column():
					ui.input(label='Event Description', placeholder='start typing',
					on_change=lambda e: resultDescription.set_text('you typed: ' + e.value),
					validation={'Input too long': lambda value: len(value) < 50})
					
					resultDescription = ui.label()
					#toggle
					switch = ui.switch('Set Recurring Event')
					ui.label('I want this event to happen:').bind_visibility_from(switch, 'value')
			ui.button('Save Event', on_click=lambda: ui.notify('You clicked me!'))
		return None
