from nicegui import ui
from app.layout import with_sidebar
from app.pages import home

calendar_ui = home.Calendar()

@ui.page('/')
def home_page():
    with_sidebar(calendar_ui.show)

ui.run()
