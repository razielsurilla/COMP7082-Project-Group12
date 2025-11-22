#! /usr/bin/env python3
import sqlite3
from datetime import datetime, date, timedelta

# your wrappers
from dbmodule.sql import Sql
from dbmodule.calendardata import CalendarData
from app.sharedVars import AddEditEventData


# ---------- helpers ----------
def make_ts(d: date, h: int, m: int) -> float:
    dt = datetime(d.year, d.month, d.day, h, m)
    return dt.timestamp()


def make_event(
    name: str,
    desc: str,
    start_ts: float,
    end_ts: float,
    recurring_idx: int = 0,        # 0=None,1=Daily,2=Weekly,3=Monthly
    interval: int = 1,
    end_opt: int = 0,              # 0=never,1=on date,2=after count
    end_date_ts: float | None = None,
    end_count: int | None = None,
    alerts: list | None = None,
) -> AddEditEventData:

    frame = AddEditEventData()
    frame.eventName = name
    frame.eventDescription = desc
    frame.eventStartDate = start_ts
    frame.eventEndDate = end_ts
    frame.recurringEventOptionIndex = recurring_idx
    frame.isRecurringEvent = bool(recurring_idx != 0)

    frame.recurringInterval = interval
    frame.recurringEndOptionIndex = end_opt
    frame.recurringEndDate = end_date_ts
    frame.recurringEndCount = end_count

    frame.selectedAlertCheckboxes = alerts or []
    frame.isAlerting = bool(alerts)

    return frame


def seed_demo_events():
    sql_instance = Sql()
    cal = CalendarData(sql_instance)

    # build table if needed
    cal.buildData()

    today = date.today()

    # -- Demo events --

    e1 = make_event(
        "Doctor Appointment",
        "Annual checkup.",
        make_ts(today, 9, 0),
        make_ts(today, 9, 30)
    )

    e2 = make_event(
        "Daily Standup",
        "Team sync",
        make_ts(today + timedelta(days=1), 9, 0),
        make_ts(today + timedelta(days=1), 9, 30),
        recurring_idx=1,
        interval=1,
    )

    e3 = make_event(
        "Weekly Lab Meeting",
        "Weekly data review",
        make_ts(today + timedelta(days=2), 10, 0),
        make_ts(today + timedelta(days=2), 11, 0),
        recurring_idx=2,
        interval=1,
        end_opt=2,          # ends after N occurrences
        end_count=8
    )

    end_date = today + timedelta(weeks=8)
    e4 = make_event(
        "Biweekly Journal Club",
        "Every 2 weeks",
        make_ts(today + timedelta(days=3), 15, 0),
        make_ts(today + timedelta(days=3), 16, 0),
        recurring_idx=2,
        interval=2,
        end_opt=1,          # ends on date
        end_date_ts=make_ts(end_date, 23, 59)
    )

    e5 = make_event(
        "Monthly Billing",
        "Pay bills",
        make_ts((today.replace(day=1) + timedelta(days=32)).replace(day=1), 18, 0),
        make_ts((today.replace(day=1) + timedelta(days=32)).replace(day=1), 18, 15),
        recurring_idx=3,
        interval=1,
        alerts=[10]
    )

    demo_events = [e1, e2, e3, e4, e5]

    for ev in demo_events:
        cal.addData(ev)

    sql_instance.commit()
    sql_instance.terminate()
    print(f"Inserted {len(demo_events)} demo events into followup.db")


if __name__ == "__main__":
    seed_demo_events()
