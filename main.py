from nicegui import app, ui
from app.sharedVars import SharedVars
from app.layout import with_sidebar, with_justSidebar
from app.pages import home, upload_schedule, add_edit, events
from dbmodule.sql import Sql
from dbmodule.calendardata import CalendarData
from datetime import datetime

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
	with_sidebar(events.show)

@ui.page('/upload')
def upload_page():
	upload_ui = upload_schedule.UploadSchedule()
	with_sidebar(upload_ui.show)

@ui.page('/add-edit')
def add_edit_page():
	data = app.storage.user.get(sharedVariables.ADDEDIT_DATA_KEY, sharedVariables.DATA_DEFAULT_VALUE)
	addEditEvent = add_edit.AddEditEvent(data, calendarData)
	with_justSidebar(addEditEvent.showPage)
	#with_sidebar(None)

@ui.page('/assistant')
def assistant_page():
#	with_sidebar(None)
    ui.label("TBD")

# ---------- MODULE SETUP ----------
def initModules():
	global sharedVariables
	global sqlInstance
	global calendarData

	sharedVariables = SharedVars()
	sqlInstance = Sql()
	calendarData = CalendarData(sqlInstance)
	
	calendarData.buildData()
	calendarData.verifyData()
	calendarData.printAllData()
	dataFrames = calendarData.getAllData()
	
	dateRangeMin = datetime(year=2025, month=1, day=25, hour=10, minute=30, second=0)
	dateRangeMax = datetime(year=2026, month=1, day=25, hour=10, minute=30, second=0)
	calendarData.findEventsInRangeMainCal(dateRangeMin.timestamp(), dateRangeMax.timestamp())
	return None


def terminateModules(sqlInstance):
    print("Gracefully close database connection.")
    try:
        sqlInstance.terminate()
    except Exception:
        pass

if __name__ in {"__main__", "__mp_main__"}:
	initModules()
	ui.run(storage_secret=sharedVariables.STORAGE_SECRET, port=sharedVariables.PORT)
	#terminateModules(sqlInstance)

