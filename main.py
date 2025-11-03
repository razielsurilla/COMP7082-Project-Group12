from nicegui import ui
from app.layout import with_sidebar
from app.pages import home, upload_schedule, add_edit
from dbmodule.sql import Sql
from dbmodule.calendardata import CalendarData


sqlInstance = None

@ui.page('/')
def home_page():
    # calendar_ui = home.Calendar()
    # with_sidebar(calendar_ui.show)
    home_tabs = home.HomeTabs()
    # home_tabs.show()
    with_sidebar(home_tabs.show)

@ui.page('/events')
def events_page():
	with_sidebar(None)

@ui.page('/upload')
def upload_page():
	upload_ui = upload_schedule.UploadSchedule()
	with_sidebar(upload_ui.show)

@ui.page('/add-edit')
def add_edit_page():
	addEditEvent = add_edit.AddEditEvent()
	addEditEvent.showPage()
	#with_sidebar(None)

@ui.page('/assistant')
def assistant_page():
	with_sidebar(None)

def initModules():
	global sqlInstance
	sqlInstance = Sql()
	calendarData = CalendarData(sqlInstance)
	calendarData.buildData()
	calendarData.addData(None, None, None)
	calendarData.updateDescription(None, None)
	calendarData.updateDetail(None, None);
	calendarData.updateDate(None, None);
	return None

def terminateModules():
	global sqlInstance
	sqlInstance.terminate()
	return None

if __name__ in {"__main__", "__mp_main__"}:
    initModules()
    ui.run()
    terminateModules()

