from nicegui import ui
from app.pages import home

def register_pages():
	@ui.page('/') # the route the page will render on
	def home_page():
		home.show()





