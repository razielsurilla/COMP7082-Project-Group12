import sqlite3 as sql
import os
from enum import Enum

DATABASE_PATH = "data/"
DATABASE_FILE = "followup.db"

class Sql:
	def __init__(self):
		# ensure directory exists
		os.makedirs(DATABASE_PATH, exist_ok=True)
		relPath = os.path.abspath(DATABASE_PATH+DATABASE_FILE)
		self.conn = sql.connect(relPath)
		self.cursor = self.conn.cursor()

	def terminate(self):
		self.conn.close()
		return None
	
	def commit(self):
		self.conn.commit()
	
	def execute(self, query):
		print(query)
		self.cursor.execute(query)
		
	def fetchall(self):
		return self.cursor.fetchall()
		
	def rowCount(self):
		return self.cursor.rowcount
		
	
