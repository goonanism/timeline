#!/usr/bin/python

import sqlite3, os
class database:
	def connect_db(self):
		"""Connects to the specific database."""
		rv = sqlite3.connect(os.path.join(app.root_path, 'timeline.db'))
		rv.row_factory = sqlite3.Row
		return rv