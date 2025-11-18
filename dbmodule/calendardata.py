from enum import Enum
import json
from datetime import datetime, date, timedelta

# data tables
class Event(Enum):
    TABLE_NAME = "events"
    EVENT_NAME = "name"
    START_DATE = "start_date"
    END_DATE = "end_date"
    DESC = "description"
    RECURRING = "is_recurring"
    ALERTING = "is_alerting"
    R_OPTION = "recurring_option"
    A_OPTIONS = "alerting_options"

class CalendarData:
	def __init__(self, sqlInstance):
		self.sql = sqlInstance
		return None
	
	def buildData(self):
		query = (f"create table if not exists {Event.TABLE_NAME.value}"
		f"({Event.EVENT_NAME.value} TEXT,"
		f"{Event.START_DATE.value} REAL NOT NULL,"
		f"{Event.END_DATE.value} REAL NOT NULL,"
		f"{Event.DESC.value} TEXT,"
		f"{Event.RECURRING.value} BOOLEAN,"
		f"{Event.ALERTING.value} BOOLEAN,"
		f"{Event.R_OPTION.value} INT,"
		f"{Event.A_OPTIONS.value} TEXT,"
		f"PRIMARY kEY ({Event.START_DATE.value}, {Event.END_DATE.value})"
		f");")
		
		self.sql.execute(query)
		return None
	
	# don't execute this unless needed
	def deleteData(self):
		query = (f"drop table if exists {Event.TABLE_NAME.value};")
		
		self.sql.execute(query)
		return None
	
	def verifyData(self):
		query = (f"PRAGMA table_info({Event.TABLE_NAME.value});")
		
		self.sql.execute(query)
		self.printQueryData()
		return None
	
	def printQueryData(self):
		rows = self.sql.fetchall()
		print("number of rows fetched: ", len(rows))
		for row in rows:
			print(row)
	
	def fillQueryData(self):
		rows = self.sql.fetchall()
		rowCount = len(rows)
		if rowCount > 0:
			for i in range(rowCount):
				dataFrame = rows[i][0]
				#dataList.append(dataFrame)
	
	def addData(self, dataFrame):
		query = (f"insert into {Event.TABLE_NAME.value} "
		f"({Event.EVENT_NAME.value}, {Event.START_DATE.value}, {Event.END_DATE.value}, {Event.DESC.value},"
		f"{Event.RECURRING.value}, {Event.ALERTING.value}, {Event.R_OPTION.value}, {Event.A_OPTIONS.value})"
		f"values ('{dataFrame.eventName}', {dataFrame.eventStartDate}, {dataFrame.eventEndDate}, "
		f"'{dataFrame.eventDescription}', {dataFrame.isRecurringEvent}, {dataFrame.isAlerting}, "
		f"{dataFrame.recurringEventOptionIndex}, '{json.dumps(dataFrame.selectedAlertCheckboxes)}'"
		f");")
		
		self.sql.execute(query)
		self.sql.commit()
		self.printAllData()
		return None

	def printAllData(self):
		query = (f"select * from {Event.TABLE_NAME.value};")
		
		self.sql.execute(query)
		self.printQueryData()
		return None

	def findEventsInRangeMainCal(self, oldDate, newDate):
		oldDate = ""
		newDate = ""
		query = f"select * from {Event.TABLE_NAME.value} where {Event.START_DATE.value} between {oldDate} and {newDate};)"
		#self.sql.execute(query).fetchall()
		#TODO: SORT VALUES INTO DICTIONARY FORM, key: day, value: list[events]
		d = {"a": [1, 2, 3]}
		return d

	def findEventsInRangeImpDate(self, oldDate, newDate):
		query = f"select * from {Event.TABLE_NAME.value} where {Event.START_DATE.value} between {oldDate} and {newDate};)"
		#self.sql.execute(query).fetchall()
		#TODO: SORT VALUES INTO DICTIONARY FORM, key: day, value: list[events]
		d = {"a": [1, 2, 3]}
		return d

