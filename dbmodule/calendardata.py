from enum import Enum
import json
from datetime import datetime, date, timedelta
from app.sharedVars import AddEditEventData

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
    R_DAYS = "recurring_days"
    R_END_DATE = "recurring_end_date"

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
		f"{Event.R_DAYS.value} INT,"
		f"{Event.R_END_DATE.value} REAL NOT NULL,"
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
	
	def getAllData(self):
		query = (f"select * from {Event.TABLE_NAME.value};")
		self.sql.execute(query)
		
		rows = self.sql.fetchall()
		rowCount = len(rows)
		dataList = []
		if rowCount > 0:
			for i in range(rowCount):
				dataFrame = AddEditEventData()
				dataFrame.eventName = rows[i][0]
				dataFrame.eventStartDate = rows[i][1]
				dataFrame.eventEndDate = rows[i][2]
				dataFrame.eventDescription = rows[i][3]
				dataFrame.isRecurringEvent = rows[i][4]
				dataFrame.isAlerting = rows[i][5]
				dataFrame.recurringEventOptionIndex = rows[i][6]
				dataFrame.selectedAlertCheckboxes = rows[i][7]
				dataFrame.recurringDays = rows[i][8]
				dataFrame.recurringEndDate = rows[i][9]
				dataList.append(dataFrame)
		#print(dataList)
		return dataList
	
	def addData(self, dataFrame):
		query = (f"insert into {Event.TABLE_NAME.value} "
		f"({Event.EVENT_NAME.value}, {Event.START_DATE.value}, {Event.END_DATE.value}, {Event.DESC.value},"
		f"{Event.RECURRING.value}, {Event.ALERTING.value}, {Event.R_OPTION.value}, {Event.A_OPTIONS.value},"
		f"{Event.R_DAYS.value}, {Event.R_END_DATE.value})"
		f"values ('{dataFrame.eventName}', {dataFrame.eventStartDate}, {dataFrame.eventEndDate}, "
		f"'{dataFrame.eventDescription}', {dataFrame.isRecurringEvent}, {dataFrame.isAlerting}, "
		f"{dataFrame.recurringEventOptionIndex}, '{json.dumps(dataFrame.selectedAlertCheckboxes)} ', "
		f"{dataFrame.recurringDays}, {dataFrame.recurringEndDate} "
		f");")
		
		self.sql.execute(query)
		self.sql.commit()
		#self.printAllData()
		return None

	def printAllData(self):
		query = (f"select * from {Event.TABLE_NAME.value};")
		
		self.sql.execute(query)
		self.printQueryData()
		return None
	
	def getDateFromTimestamp(self, timestamp):
		dateObj = datetime.fromtimestamp(timestamp)
		return dateObj

	def findEventsInRangeMainCal(self, rangeMin, rangeMax):
		query = (f"select * from {Event.TABLE_NAME.value} where {Event.START_DATE.value} between {rangeMin} and {rangeMax};")
		self.sql.execute(query)
		#self.printAllData()
		fetchedData = self.sql.fetchall()
		numFetchedDataRows = len(fetchedData)
		#TODO: SORT VALUES INTO DICTIONARY FORM, key: day, value: list[events]
		d = {"a": [1, 2, 3]}
		return d

	def findEventsInRangeImpDate(self, oldDate, newDate):
		query = (f"select * from {Event.TABLE_NAME.value} where {Event.START_DATE.value} between {oldDate} and {newDate};")
		#self.sql.execute(query)
		#TODO: SORT VALUES INTO DICTIONARY FORM, key: day, value: list[events]
		d = {"a": [1, 2, 3]}
		return d

	def updateEvent(self, old_start_ts, old_end_ts, dataFrame):
		"""Update a single event identified by its original start/end timestamps."""
		query = (
			f"update {Event.TABLE_NAME.value} set "
			f"{Event.EVENT_NAME.value} = '{dataFrame.eventName}', "
			f"{Event.START_DATE.value} = {dataFrame.eventStartDate}, "
			f"{Event.END_DATE.value} = {dataFrame.eventEndDate}, "
			f"{Event.DESC.value} = '{dataFrame.eventDescription}', "
			f"{Event.RECURRING.value} = {int(bool(dataFrame.isRecurringEvent))}, "
			f"{Event.ALERTING.value} = {int(bool(dataFrame.isAlerting))}, "
			f"{Event.R_OPTION.value} = {int(dataFrame.recurringEventOptionIndex)}, "
			f"{Event.A_OPTIONS.value} = '{json.dumps(dataFrame.selectedAlertCheckboxes)}, ' "
			f"{Event.R_DAYS.value} = {dataFrame.recurringDays}, "
			f"{Event.R_END_DATE.value} = {dataFrame.recurringEndDate} "
			f"where {Event.START_DATE.value} = {old_start_ts} "
			f"and {Event.END_DATE.value} = {old_end_ts};"
		)
		self.sql.execute(query)
		self.sql.commit()


	def deleteEvent(self, start_ts, end_ts):
		"""Delete a single event identified by its start/end timestamps."""
		query = (
			f"delete from {Event.TABLE_NAME.value} "
			f"where {Event.START_DATE.value} = {start_ts} "
			f"and {Event.END_DATE.value} = {end_ts};"
		)
		self.sql.execute(query)
		self.sql.commit()


