from nicegui import app, ui
from app.sharedVars import SharedVars
from app.layout import with_sidebar, with_justSidebar
from app.pages import home, upload_schedule, add_edit, events, chat_assistant
from dbmodule.sql import Sql
from dbmodule.calendardata import CalendarData
from datetime import datetime

sqlInstance = None

@ui.page('/')
def home_page():
	ui.page_title('FollowUp/Calendar')
	# calendar_ui = home.Calendar()
	# with_sidebar(calendar_ui.show)
	home_tabs = home.HomeTabs(calendar_data=calendarData)
	# home_tabs.show()
	with_sidebar(home_tabs.show)

@ui.page('/health')
def health():
    return "OK"

@ui.page('/events')
def events_page():
	ui.page_title('FollowUp/Events')
	with_sidebar(lambda: events.show(calendar_data=calendarData))

@ui.page('/upload')
def upload_page():
	ui.page_title('FollowUp/Upload')
	upload_ui = upload_schedule.UploadSchedule()
	with_sidebar(upload_ui.show)

@ui.page('/add-edit')
def add_edit_page():
	ui.page_title('FollowUp/Add Events')
	data = app.storage.user.get(sharedVariables.ADDEDIT_DATA_KEY, sharedVariables.DATA_DEFAULT_VALUE)
	addEditEvent = add_edit.AddEditEvent(data, calendarData)
	with_justSidebar(addEditEvent.showPage)
	#with_sidebar(None)

@ui.page('/assistant')
def assistant_page():
	ui.page_title('FollowUp/Assistant')
	chat_ui = chat_assistant.ChatPage()
	with_sidebar(chat_ui.show)

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
	
	#dateRangeMin = datetime(year=2025, month=1, day=25, hour=10, minute=30, second=0)
	#dateRangeMax = datetime(year=2026, month=1, day=25, hour=10, minute=30, second=0)
	#calendarData.findEventsInRangeMainCal(dateRangeMin.timestamp(), dateRangeMax.timestamp())
	return None


def terminateModules(sqlInstance):
	print("Gracefully close database connection.")
	try:
		sqlInstance.terminate()
	except Exception:
		pass

if __name__ in {"__main__", "__mp_main__"}:
	#ui.page_title('FollowUp')
	initModules()
	ui.run(storage_secret=sharedVariables.STORAGE_SECRET, port=sharedVariables.PORT)
	#terminateModules(sqlInstance)

