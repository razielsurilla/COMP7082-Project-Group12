from nicegui import ui
from app.layout import with_sidebar
from app.pages import home
from dbmodule.sql import Sql

calendar_ui = home.Calendar()
sqlInstance = None

@ui.page('/')
def home_page():
	with_sidebar(calendar_ui.show)

@ui.page('/events')
def events_page():
	with_sidebar(None)

@ui.page('/upload')
def upload_page():
	with_sidebar(None)

@ui.page('/add-edit')
def add_edit_page():
	with_sidebar(None)

@ui.page('/assistant')
def assistant_page():
	with_sidebar(None)

def initModules():
	sqlInstance = Sql()
	return None

def terminateModules():
	#sqlInstance.terminate()
	return None

if __name__ in {"__main__", "__mp_main__"}:
	initModules()
	ui.run()
	#terminateModules()
