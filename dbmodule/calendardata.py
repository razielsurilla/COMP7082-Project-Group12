from enum import Enum
import json

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
	def __init__(self, sqlCursor):
		self.cursor = sqlCursor
		return None
	
	def buildData(self):
		query = (f"create table if not exists {Event.TABLE_NAME.value}"
		f"({Event.START_DATE.value} DATE,"
		f"{Event.END_DATE.value} DATE,"
		f"{Event.DESC.value} TEXT,"
		f"{Event.RECURRING.value} BOOLEAN,"
		f"{Event.ALERTING.value} BOOLEAN,"
		f"{Event.R_OPTION.value} INT,"
		f"{Event.A_OPTIONS.value} TEXT,"
		f"PRIMARY kEY ({Event.START_DATE.value}, {Event.END_DATE.value})"
		f");")
		
		print(query)
		self.cursor.execute(query)
		return None
	
	def verifyData(self):
		#query = (f".schema {Event.TABLE_NAME.value}")
		query = (f"PRAGMA table_info({Event.TABLE_NAME.value});")
		print(query)
		self.cursor.execute(query)
		self.printQueryData()
		return None
	
	def printQueryData(self):
		rows = self.cursor.fetchall()
		for row in rows:
			print(row)
	
	def addData(self, date, description, detail):
		query = (f"insert into {Event.TABLE_NAME.value} "
		f"({Event.DATE.value}, {Event.DESC.value}, {Event.DETAIL.value}) "
		f"values ({date}, {description}, {detail})")
		
		print(query)
		#self.cursor.execute(query)
		return None

	def updateDescription(self, desc, date):
		query = (f"update {Event.TABLE_NAME.value} "
		f"set ({Event.DESC.value} = {desc} "
		f"where {Event.DATE.value} = {date})")
		
		print(query)
		#self.cursor.execute(query)
		return None

	def updateDetail(self, desc, date):
		query = (f"update {Event.TABLE_NAME.value} "
		f"set ({Event.DESC.value} = {desc} "
		f"where {Event.DATE.value} = {date})")
		
		print(query)
		#self.cursor.execute(query)
		return None
	
	def updateDate(self, oldDate, newDate):
		query = (f"select {Event.DESC.value}, {Event.DETAIL.value} from {Event.TABLE_NAME.value} "
		f"where {Event.DATE.value} = {oldDate})")
		print(query)
		#result = self.cursor.execute(query)
		desc = None
		detail = None
		#desc, detail = result.fetchone()
		
		query = (f"delete from {Event.TABLE_NAME.value} "
		f"where {Event.DATE.value} = {oldDate})")
		print(query)
		#self.cursor.execute(query)
		
		self.addData(newDate, desc, detail)
		return None
