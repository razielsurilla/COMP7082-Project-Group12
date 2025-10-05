from nicegui import ui

def sidebar():
    with ui.column().classes('w-20 h-full bg-gray-200 p-4 items-center justify-start gap-6'):

        # for now, all links are to the homepage "/"
        with ui.link(target='/', new_tab=False).classes('no-underline'):
            ui.icon('calendar_month').classes('text-5xl text-gray-700 hover:text-blue-500')

        with ui.link(target='/', new_tab=False).classes('no-underline'):
            ui.icon('menu').classes('text-5xl text-gray-700 hover:text-blue-500')

        with ui.link(target='/', new_tab=False).classes('no-underline'):
            ui.icon('photo_camera').classes('text-5xl text-gray-700 hover:text-blue-500')
