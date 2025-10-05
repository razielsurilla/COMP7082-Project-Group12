from nicegui import ui
from app.layout import with_sidebar
from app.pages import home

@ui.page('/') # route the page will display on
def home_page():
    with_sidebar(home.show)

ui.run()
