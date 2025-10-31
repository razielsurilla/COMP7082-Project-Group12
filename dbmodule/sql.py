import sqlite3 as sql
import os

DATABASE_PATH = "../data/"
DATABASE_FILE = "followup.db"

class Sql:
	def __init__(self):
		absPath = os.path.realpath(__file__)
		#relPath = os.path.
		print(absPath)
		#self.conn = sql.connect(absPath)
		#self.cursor = self.conn.cursor()

	def terminate(self):
		#self.conn.close()
		return None
