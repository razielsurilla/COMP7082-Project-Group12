from nicegui import app, ui
from app.sharedVars import SharedVars
from app.layout import with_sidebar, with_just_sidebar
from app.pages import home, upload_schedule, add_edit, events, chat_assistant
from dbmodule.sql import Sql
from dbmodule.calendardata import CalendarData
sqlInstance = None

@ui.page('/')
def home_page():
	ui.page_title('FollowUp/Calendar')
	home_tabs = home.HomeTabs(calendar_data=calendarData)
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
	add_edit_event = add_edit.AddEditEvent(data, calendarData)
	with_just_sidebar(add_edit_event.showPage)

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
	
	calendarData.build_data()
	calendarData.verify_data()
	calendarData.print_all_data()

	return None


def terminateModules(sql_instance):
	print("Gracefully close database connection.")
	try:
		sql_instance.terminate()
	except Exception:
		pass

if __name__ in {"__main__", "__mp_main__"}:
	initModules()
	ui.run(host="0.0.0.0", storage_secret=sharedVariables.STORAGE_SECRET, port=sharedVariables.PORT)
