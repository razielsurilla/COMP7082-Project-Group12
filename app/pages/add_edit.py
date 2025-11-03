from nicegui import ui
from app.components.date_picker_label import datePickerLabel, timePickerLabel

# TODO: this should be a component, then home.py should create a Calendar object
class AddEditEvent:
	def __init__(self):
		return None

	def showPage(self):
		with ui.column():
			with ui.row():
				with ui.column():
					self.eventEntryPanel()
					self.alertsPanel()
				with ui.column():
					ui.textarea(label='Event Description', value='some text').props('clearable')
					resultDescription = ui.label()
					self.recurringEventPanel()
			ui.button('Save Event', on_click=lambda: ui.notify('You clicked me!'))
		return None
	
	def alertsPanel(self):
		#toggle
		switch = ui.switch('Set Alerts')
		ui.label('Remind me:').bind_visibility_from(switch, 'value')
		checkbox = ui.checkbox('When it happens').bind_visibility_from(switch, 'value')
		#ui.label('Check!').bind_visibility_from(checkbox, 'value')
		checkbox = ui.checkbox('15 minutes before').bind_visibility_from(switch, 'value')
		#ui.label('Check!').bind_visibility_from(checkbox, 'value')
		checkbox = ui.checkbox('1 hour before').bind_visibility_from(switch, 'value')
		#ui.label('Check!').bind_visibility_from(checkbox, 'value')
		checkbox = ui.checkbox('1 day before').bind_visibility_from(switch, 'value')
		#ui.label('Check!').bind_visibility_from(checkbox, 'value')
		return None

	def recurringEventPanel(self):
		#toggle
		switch = ui.switch('Set Recurring Event')
		ui.label('I want this event to happen:').bind_visibility_from(switch, 'value')
		radio1 = ui.radio(['Every label days', 'Every Week', 'Every Month', 'Every Year'], value='Every Week').bind_visibility_from(switch, 'value')
		return None

	def eventEntryPanel(self):
		ui.input(label='Event Name', placeholder='start typing',
		on_change=lambda e: resultDetail.set_text('you typed: ' + e.value),
		validation={'Input too long': lambda value: len(value) < 20})
		with ui.row():
			datePickerLabel("Start Date", None)
			timePickerLabel("Time", None)
		
		with ui.row():
			datePickerLabel("End Date", None)
			timePickerLabel("Time", None)
		
		resultDetail = ui.label()
		return None
