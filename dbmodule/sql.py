import sqlite3 as sql
import os
from enum import Enum

DATABASE_PATH = "data/"
DATABASE_FILE = "followup.db"

class Sql:
	def __init__(self):
		relPath = os.path.abspath(DATABASE_PATH+DATABASE_FILE)
		self.conn = sql.connect(relPath)
		self.cursor = self.conn.cursor()
		return None

	def terminate(self):
		self.conn.close()
		return None
