#!/usr/bin/python

from flask import Flask, request, render_template, jsonify, g
import os
import sqlite3

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'timeline.db'),
    DEBUG=True
))
app.config.from_envvar('TIMELINE_SETTINGS', silent=True)

def connect_db():
	"""Connects to the specific database."""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db():
	"""Opens a new database connection if there is none yet for the
	current application context.
	"""
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db
	
@app.teardown_appcontext
def close_db(error):
	"""Closes the database again at the end of the request."""
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()
		
def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.route("/")
def index():
	db = get_db()
	cur = db.execute('select name from event order by id desc')
	entries = cur.fetchall()
	return jsonify(entries)

@app.route("/add/", methods=['GET', 'POST'])
def add():
	if request.method == 'POST':
		return jsonify(request.form)
	else:
		return render_template('add.html')

if __name__ == "__main__":
	app.debug = True
	app.run()