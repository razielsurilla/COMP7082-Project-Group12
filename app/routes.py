from nicegui import ui
from app.layout import with_sidebar
from app.pages import home, events

def register_pages(calendarData):
    """
    Register all NiceGUI pages.
    - Home uses the Calendar component's .show()
    - Events is called without DB arg (fallback compatible)
    - Add/Edit remains a placeholder
    """
    @ui.page('/') # the route the page will render on
    def home_page():
        home.show()
    @ui.page('/events')
    def events_page():
        """List of events page."""
        def content():
            # Call events.show() if it doesn't accept a parameter.
            try:
                # If your events.show supports a DB arg, this will succeed:
                return events.show(calendarData)  # type: ignore[arg-type]
            except TypeError:
                # Otherwise, fall back to the no-arg version:
                return events.show()
            except AttributeError:
                ui.label('Events page is not implemented yet.')
        with_sidebar(content)




