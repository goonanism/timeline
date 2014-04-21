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
		json_list['events'].append(get_event(event[0]))
	return jsonify(json_list)
	
@app.route("/events/view/<int:event_id>")
def event_view(event_id):
	return jsonify(get_event(event_id))
	
@app.route("/events/edit/", defaults={'event_id' : None}, methods=['GET', 'POST'])
@app.route("/events/edit/<int:event_id>", methods=['GET', 'POST'])
def event_edit(event_id):
	if request.method == 'POST' and event_id == None:
		values = {}
		tags = {}
		for value in request.json:
			if value.has_key('name'):
				if value['name'] != 'tag':
					values[value['name']] = value['value']
			if value.has_key('tags'):
				tags = value
		
		values['date_from'] = values['date_from[year]'] + '-' + values['date_from[month]'] + '-' + values['date_from[day]']
		values.pop('date_from[year]', None)
		values.pop('date_from[month]', None)
		values.pop('date_from[day]', None)
		
		values['date_to'] = values['date_to[year]'] + '-' + values['date_to[month]'] + '-' + values['date_to[day]']
		values.pop('date_to[year]', None)
		values.pop('date_to[month]', None)
		values.pop('date_to[day]', None)
		
		updates = []
		where = ''
		for key, value in values.iteritems():
			if key == 'id':
				where += ' WHERE id = ' + str(value)
			else:
				updates.append(key + " = '" + str(value) + "'")
		db = get_db()
		db.execute('UPDATE event SET ' + ', '.join(updates) + where)
		db.commit()

		# Delete all current tag connections			
		db.execute('DELETE FROM event_tag WHERE event_id = ' + str(values['id']))
		db.commit()
		
		# Add new tag connections
		tags_to_insert = []
		#################################
		#								#
		#		Prevent duplication		#
		#								#
		#################################
 		for tag in tags['tags']:
 			tags_to_insert.append('(' + values['id'] + ', ' + str(tag['id']) + ')')
 			db.execute('INSERT INTO event_tag (event_id, tag_id) VALUES ' + ', '.join(tags_to_insert))
 			db.commit()
			
		return 'all good!'
	else:
		event = get_event(event_id)
		date_from = event['event']['date_from'].split('-')
		date_to = event['event']['date_to'].split('-')
		event['event']['date_from'] = {'year' : int(date_from[0]), 'month' : int(date_from[1]), 'day' : int(date_from[2])}
		event['event']['date_to'] = {'year' : int(date_to[0]), 'month' : int(date_to[1]), 'day' : int(date_to[2])}
		return render_template('edit.html', event=event)

@app.route("/events/add/", methods=['GET', 'POST'])
def event_add():
	if request.method == 'POST':
		date_from = request.form['date_from[year]'] + '-' + request.form['date_from[month]'] + '-' + request.form['date_from[day]']
		date_to = request.form['date_to[year]'] + '-' + request.form['date_to[month]'] + '-' + request.form['date_to[day]']
		db = get_db()
		db.execute('insert into event (name, note, link, date_from, date_to) values(?, ?, ?, ?, ?)', [request.form['name'], request.form['note'], request.form['link'], date_from, date_to])
		db.commit()
		return jsonify(request.form)
	else:
		return render_template('add.html')

def get_event(event_id):
	result = {'event' : [], 'tags' : []}
	db = get_db()
	cur = db.execute('SELECT * FROM event WHERE id = ' + str(event_id))
	result['event'] = dict_row(cur.fetchone())
	cur = db.execute('select * from tag join event_tag on event_tag.tag_id = tag.id where event_tag.event_id = ' + str(event_id))
	for tag in cur.fetchall():
		result['tags'].append(dict_row(tag))
	return result
	

@app.route("/tags/")
def get_tags():
	#################################
	#								#
	#		Add Event Data			#
	#								#
	#################################
	db = get_db()
	cur = db.execute('SELECT * FROM tag')
	json_list = {'tags' : []}
	events = cur.fetchall()
	for event in events:
		json_list['tags'].append(dict_row(event))
	return jsonify(json_list)
	
@app.route("/tags/view/<int:tag_id>")
def get_tag():
	#################################################
	#												#
	#		Individual tag with Event Data			#
	#												#
	#################################################
	pass

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