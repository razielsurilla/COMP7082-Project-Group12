from nicegui import ui

def sidebar():
	with ui.column().classes('group fixed w-20 h-full bg-gray-200 p-4 justify-start gap-6'
							 'transition-all duration-300 hover:w-48 z-100'
							 ):

		# for now, all links are to the homepage "/"
		with ui.link(target='/', new_tab=False).classes('no-underline homepage flex'):
			ui.icon('calendar_month').classes('text-5xl text-gray-700 homepage-hover:text-blue-500')
			ui.label('Calendar').classes('pl-4 place-content-center text-gray-700 opacity-0 group-hover:opacity-100 transition-opacity duration-500 homepage-hover:text-blue-500')

		with ui.link(target='/events', new_tab=False).classes('no-underline events flex'):
			ui.icon('menu').classes('text-5xl text-gray-700 events-hover:text-blue-500')
			ui.label('Events').classes('pl-4 place-content-center text-gray-700 opacity-0 group-hover:opacity-100 transition-opacity duration-500 events-hover:text-blue-500')

		with ui.link(target='/upload', new_tab=False).classes('no-underline upload flex'):
			ui.icon('photo_camera').classes('text-5xl text-gray-700 upload-hover:text-blue-500')
			ui.label('Upload').classes('pl-4 place-content-center text-gray-700 opacity-0 group-hover:opacity-100 transition-opacity duration-500 upload-hover:text-blue-500')
