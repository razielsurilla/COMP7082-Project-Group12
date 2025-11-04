# main.py
from nicegui import ui
from dbmodule.sql import Sql
from dbmodule.calendardata import CalendarData
from app.routes import register_pages


# ---------- MODULE SETUP ----------
def initModules():
    """Initialize database and return both sqlInstance and calendarData."""
    sqlInstance = Sql()                       # opens SQLite and applies PRAGMAs
    calendarData = CalendarData(sqlInstance.conn)
    calendarData.buildData()                  # ensure events table exists
    return sqlInstance, calendarData


def terminateModules(sqlInstance):
    """Gracefully close database connection."""
    try:
        sqlInstance.terminate()
    except Exception:
        pass


# ---------- APP ENTRY ----------
if __name__ in {"__main__", "__mp_main__"}:
    sqlInstance, calendarData = initModules()
    register_pages(calendarData)
    ui.run(title="Calendar App", reload=False)
    terminateModules(sqlInstance)
