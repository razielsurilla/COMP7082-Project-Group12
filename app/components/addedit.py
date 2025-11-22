from nicegui import ui

def datePickerLabel(labelName, clickEvent, value: str = ''):
	with ui.input(labelName, value=value or '', on_change=clickEvent) as date:
		with ui.menu().props('no-parent-event') as menu:
			with ui.date().bind_value(date):
				with ui.row().classes('justify-end'):
					ui.button('Close', on_click=menu.close).props('flat')
	with date.add_slot('append'):
		ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
	return date

def timePickerLabel(labelName, clickEvent, value: str = ''):
	with ui.input(labelName, value=value or '', on_change=clickEvent) as time:
		with ui.menu().props('no-parent-event') as menu:
			with ui.time().bind_value(time):
				with ui.row().classes('justify-end'):
					ui.button('Close', on_click=menu.close).props('flat')
		with time.add_slot('append'):
			ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
	return time