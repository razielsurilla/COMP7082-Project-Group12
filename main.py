from nicegui import ui
from app.layout import with_sidebar
from app.pages import home

calendar_ui = home.Calendar()

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

ui.run()
