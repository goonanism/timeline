#!/usr/bin/python

from flask import Flask, request, render_template, jsonify, json, g
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

def dict_row(row):
	return dict(zip(row.keys(), row)) 

@app.route("/")
def index():
	return 'timeline!'

@app.route("/events/")
def events():
	db = get_db()
	cur = db.execute('SELECT * FROM event')
	json_list = {'events' : []}
	events = cur.fetchall()
	for event in events:
		json_list['events'].append(dict_row(event))
	return jsonify(json_list)
	
@app.route("/events/view/<int:event_id>")
def event_view(event_id):
	return 'Event %d' % event_id
	
@app.route("/events/edit/<int:event_id>")
def event_edit(event_id):
	db = get_db()
	cur = db.execute('SELECT * FROM event WHERE id = ' + str(event_id))
	event = cur.fetchone()
	event_dic = dict_row(event)
	date_from = event_dic['date_from'].split('-')
	date_to = event_dic['date_to'].split('-')
	event_dic['date_from'] = {'year' : int(date_from[0]), 'month' : int(date_from[1]), 'day' : int(date_from[2])}
	event_dic['date_to'] = {'year' : int(date_to[0]), 'month' : int(date_to[1]), 'day' : int(date_to[2])}
	return render_template('edit.html', event=event_dic)

@app.route("/events/add/", methods=['GET', 'POST'])
def add_event():
	if request.method == 'POST':
		date_from = request.form['date_from[year]'] + '-' + request.form['date_from[month]'] + '-' + request.form['date_from[day]']
		date_to = request.form['date_to[year]'] + '-' + request.form['date_to[month]'] + '-' + request.form['date_to[day]']
		db = get_db()
		db.execute('insert into event (name, note, link, date_from, date_to) values(?, ?, ?, ?, ?)', [request.form['name'], request.form['note'], request.form['link'], date_from, date_to])
		db.commit()
		return jsonify(request.form)
	else:
		return render_template('add.html')

@app.route("/tags/")
def get_tags():
	db = get_db()
	cur = db.execute('SELECT * FROM tag')
	json_list = {'tags' : []}
	events = cur.fetchall()
	for event in events:
		json_list['tags'].append(dict_row(event))
	return jsonify(json_list)

@app.route("/tags/add/", methods=['GET', 'POST'])
def add_tags():
	if request.method == 'POST':
		reference = request.json['tag'].replace(' ', '-').lower()
		db = get_db()

		# check if tag exists. If it does, return all details
		
		cur = db.execute("SELECT * FROM tag WHERE reference = '" + reference + "'")
		tag_exists = cur.fetchone();
		if tag_exists:
			return jsonify(tag_exists)
	
		# Otherwise create new tag
		db.execute('insert into tag (name, reference) values(?, ?)', [request.json['tag'], reference])
		db.commit()
		
		# Then get new tag details and return it
		cur = db.execute("SELECT * FROM tag WHERE reference = '" + reference + "'")
		return jsonify(cur.fetchone())
	else:
		return False

if __name__ == "__main__":
	app.debug = True
	app.run()