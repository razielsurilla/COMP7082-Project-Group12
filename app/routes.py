# app/routes.py
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

    # Create one Calendar UI instance and reuse it
    calendar_ui = home.Calendar()

    @ui.page('/')
    def home_page():
        """Home page with calendar view."""
        with_sidebar(calendar_ui.show)

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

    @ui.page('/add-edit')
    @ui.page('/add_edit')  # optional alias
    def add_edit_page():
        """Placeholder for future Add/Edit page."""
        with_sidebar(lambda: ui.label('Add/Edit page coming soon.'))

    @ui.page('/upload')
    def upload_page():
        """Upload page placeholder."""
        with_sidebar(lambda: ui.label('Upload page coming soon.'))

    @ui.page('/assistant')
    def assistant_page():
        """Assistant page placeholder."""
        with_sidebar(lambda: ui.label('Assistant page coming soon.'))
