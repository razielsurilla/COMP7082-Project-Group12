from app.components.schedule_event import UploadedEventDataFrame
from datetime import datetime, timedelta

def test_uploaded_event_dataframe_dates_align_with_weekday():
    obj = UploadedEventDataFrame("Test", "Wednesday", "Stuff")

    today = datetime.today()
    target_wd = 2  # Wednesday
    days_ahead = (target_wd - today.weekday()) % 7
    expected_date = today + timedelta(days=days_ahead)

    assert abs(obj.eventStartDate - expected_date.timestamp()) < 3
    assert abs(obj.eventEndDate - (expected_date + timedelta(hours=1)).timestamp()) < 3
    assert obj.isRecurringEvent is True
    assert obj.isAlerting is True
