from enum import Enum

# data tables
class Event(Enum):
	TNAME = "event"
	DATE = "date"
	DESC = "description"
	DETAIL = "detail"
	
class CalendarData:
	def __init__(self, sqlCursor):
		self.cursor = sqlCursor
		return None
	
	def buildData(self):
		query = (f"create table if not exists {Event.TNAME.value}"
		f"({Event.DATE.value} Real primary key,"
		f"{Event.DESC.value} text,"
		f"{Event.DETAIL.value} text)")
		
		print(query)
		#self.cursor.execute(query)
		return None
	
	def addData(self, date, description, detail):
		query = (f"insert into {Event.TNAME.value} "
		f"({Event.DATE.value}, {Event.DESC.value}, {Event.DETAIL.value}) "
		f"values ({date}, {description}, {detail})")
		
		print(query)
		#self.cursor.execute(query)
		return None

	def updateDescription(self, desc, date):
		query = (f"update {Event.TNAME.value} "
		f"set ({Event.DESC.value} = {desc} "
		f"where {Event.DATE.value} = {date})")
		
		print(query)
		#self.cursor.execute(query)
		return None

	def updateDetail(self, desc, date):
		query = (f"update {Event.TNAME.value} "
		f"set ({Event.DESC.value} = {desc} "
		f"where {Event.DATE.value} = {date})")
		
		print(query)
		#self.cursor.execute(query)
		return None
	
	def updateDate(self, oldDate, newDate):
		query = (f"select {Event.DESC.value}, {Event.DETAIL.value} from {Event.TNAME.value} "
		f"where {Event.DATE.value} = {oldDate})")
		print(query)
		#result = self.cursor.execute(query)
		desc = None
		detail = None
		#desc, detail = result.fetchone()
		
		query = (f"delete from {Event.TNAME.value} "
		f"where {Event.DATE.value} = {oldDate})")
		print(query)
		#self.cursor.execute(query)
		
		self.addData(newDate, desc, detail)
		return None
