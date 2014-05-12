#!/usr/bin/python

from flask import request, render_template, jsonify, g
from timeline import app
import timeline.database as dbase

@app.route("/events/")
def events():
	db = dbase.get_db()
	cur = db.execute('SELECT * FROM event')
	json_list = {'events' : []}
	events = cur.fetchall()
	for event in events:
		json_list['events'].append(get_event(event[0]))
	return jsonify(json_list)
	
@app.route("/events/view/<int:event_id>")
def event_view(event_id):
	return jsonify(get_event(event_id))
	

@app.route("/events/edit/<int:event_id>")
def even_edit(event_id):
	event = get_event(event_id)
	date_from = event['event']['date_from'].split('-')
	date_to = event['event']['date_to'].split('-')
	event['event']['date_from'] = {'year' : int(date_from[0]), 'month' : int(date_from[1]), 'day' : int(date_from[2])}
	event['event']['date_to'] = {'year' : int(date_to[0]), 'month' : int(date_to[1]), 'day' : int(date_to[2])}
	return render_template('edit.html', event=event)

@app.route("/events/edit/", methods=['POST'])
def event_update():
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
	db = dbase.get_db()
	db.execute('UPDATE event SET ' + ', '.join(updates) + where)
	db.commit()

	# Delete all current tag connections			
	db.execute('DELETE FROM event_tag WHERE event_id = ' + str(values['id']))
	db.commit()
	
	# Add new tag connections
	tags_to_insert = []
	
	# delete all joins to prevent duplication
	db.execute('DELETE FROM event_tag WHERE event_id = ' + str(values['id']))
	db.commit()

	for tag in tags['tags']:
		tags_to_insert.append('(' + values['id'] + ', ' + str(tag['id']) + ')')
	db.execute('INSERT INTO event_tag (event_id, tag_id) VALUES ' + ', '.join(tags_to_insert))
	db.commit()

	return 'all good!'

@app.route("/events/add/", methods=['GET', 'POST'])
def event_add():
	if request.method == 'POST':
		data = {'event' : {}, 'tags' : []}
		for field in request.json:
			if 'tags' in field:
				data['tags'].append(field)
			else:
				data['event'][field['name']] = field['value']
		print data
		date_from = data['event']['date_from[year]'] + '-' + data['event']['date_from[month]'] + '-' + data['event']['date_from[day]']
		date_to = data['event']['date_to[year]'] + '-' + data['event']['date_to[month]'] + '-' + data['event']['date_to[day]']
		db = dbase.get_db()
		db.execute('insert into event (name, note, link, date_from, date_to) values(?, ?, ?, ?, ?)', [data['event']['name'], data['event']['note'], data['event']['link'], date_from, date_to])
		db.commit()
		
		# last_insert_rowid()
		
		##################################
		# get last inserted and add tags #
		##################################
		
		return jsonify(data)
	else:
		return render_template('add.html')

def get_event(event_id):
	result = {'event' : [], 'tags' : []}
	db = dbase.get_db()
	cur = db.execute('SELECT * FROM event WHERE id = ' + str(event_id))
	result['event'] = dbase.dict_row(cur.fetchone())
	cur = db.execute('select * from tag join event_tag on event_tag.tag_id = tag.id where event_tag.event_id = ' + str(event_id))
	for tag in cur.fetchall():
		result['tags'].append(dbase.dict_row(tag))
	return result
	
