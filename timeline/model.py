from flask import Flask, jsonify, json, g
from timeline import app
import sqlite3

class Model:
	def __init__(self, name = None, table = None, habtm = None, join_table = None):
		self.name = name
		self.table = table
		self.habtm = habtm
		self.join_table = join_table
		
	def connect_db(self):
		"""Connects to the specific database."""
		rv = sqlite3.connect(app.config['DATABASE'])
		rv.row_factory = sqlite3.Row
		return rv
	def get_db(self):
		"""Opens a new database connection if there is none yet for the
		current application context.
		"""
		if not hasattr(g, 'sqlite_db'):
			g.sqlite_db = self.connect_db()
		return g.sqlite_db
	@app.teardown_appcontext
	def close_db(self, error = None):
		"""Closes the database again at the end of the request."""
		if hasattr(g, 'sqlite_db'):
			g.sqlite_db.close()
	def init_db(self):
		with app.app_context():
			db = get_db()
			with app.open_resource('schema.sql', mode='r') as f:
				db.cursor().executescript(f.read())
			db.commit()

	def dict_row(self, row):
		return dict(zip(row.keys(), row))
	def save(self, data):
		db = self.get_db()
		if data[self.name].has_key('id'):
			values = self.query_values(data[self.name])
			keys = ', '.join(values['key_list'])
			values = ', '.join(values['question_marks'])
			db.execute('UPDATE ' + self.table + '(' + keys + ') values(' + values + ') WHERE id = ' + str(data[self.name]['id']), values['value_list'])
			# update
			pass
		else:
			#create new entry
			values = self.query_values(data[self.name])
			db.execute('INSERT INTO ' + self.table + '(' + ', '.join(values['key_list']) + ') values(' + ', '.join(values['question_marks']) + ')', values['value_list'])
			pass
	def query_values(self, data):
		key_list = []
		value_list = []
		question_marks = []
		for key, value in data.iteritems():
			key_list.append(key)
			value_list.append(value)
			question_marks.append('?')
		return { 'key_list' : key_list, 'value_list' : value_list, 'question_marks' : question_marks }
	

	def delete(self):
		pass
	def query(self, query):
		db = self.get_db()
		cur = db.execute(query)
		return cur.fetchall()
		