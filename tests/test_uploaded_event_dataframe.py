import unittest
from datetime import datetime, timedelta
from app.components.schedule_event import UploadedEventDataFrame

class TestUploadedEventDataFrame(unittest.TestCase):

    def test_uploaded_event_dataframe_dates_align_with_weekday(self):
        obj = UploadedEventDataFrame("Test", "Wednesday", "Stuff")

        today = datetime.today()
        target_wd = 2
        days_ahead = (target_wd - today.weekday()) % 7
        expected_date = today + timedelta(days=days_ahead)

        self.assertLess(abs(obj.eventStartDate - expected_date.timestamp()), 3)
        self.assertLess(
            abs(obj.eventEndDate - (expected_date + timedelta(hours=1)).timestamp()),
            3,
        )
        self.assertTrue(obj.isRecurringEvent)
        self.assertTrue(obj.isAlerting)
