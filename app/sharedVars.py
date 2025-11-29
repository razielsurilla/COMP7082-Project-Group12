import os
from dataclasses import dataclass, field
from typing import ClassVar, List
from datetime import datetime, date, timedelta

class SharedVars:
	def __init__(self):
		self.PORT = int(os.getenv('PORT', 9090))
		self.STORAGE_SECRET = 'followupPortal'
		self.ADDEDIT_DATA_KEY = 'addEditData'
		self.DATA_DEFAULT_VALUE = 'No data'
		return None

@dataclass
class AddEditEventData:
	eventName: str = "dummy"
	eventDescription: str = "dummy"
	eventStartDate: float = 0
	eventEndDate: float = 0
	isRecurringEvent: bool = False
	isAlerting: bool = False
	recurringEventOptionIndex: int = 0
	selectedAlertCheckboxes: List[int] = field(default_factory=list)
	recurringInterval: int = 0
	recurringEndOptionIndex: int = 0
	recurringEndDate: float | None = None
	recurringEndCount: int | None = None

@dataclass
class EventDateTime:
	DATE_FORMAT: ClassVar[str] = "%Y-%m-%d/%H:%M"
	dateStr: str = ""
	timeStr: str = ""
	
	def getDateTimestamp(self):
		dateObj = datetime.now()
		try:
			dateObj = datetime.strptime(f"{self.dateStr}/{self.timeStr}", self.DATE_FORMAT)
			return dateObj.timestamp()
		except ValueError as e:
			print("event date incorrect format!")
		return 0
	
