#!/usr/bin/python

from flask import request, render_template, jsonify, g
from timeline import app
from database import Database

class Event():
	def __init__(self):
		self.db = Database()
	def get(self, event_id):
		''' returns a dictionary of Event and associated tags for event id provided '''
		result = {'event' : [], 'tags' : []}
		cur = self.db.execute('SELECT * FROM event WHERE id = ?', [str(event_id)])
		result['event'] = self.db.dict_row(cur.fetchone())
		cur = self.db.execute('select * from tag join event_tag on event_tag.tag_id = tag.id where event_tag.event_id = ?', [str(event_id)])
		for tag in cur.fetchall():
			result['tags'].append(self.db.dict_row(tag))
		return result

	def get_all(self):
		cur = self.db.execute('SELECT * FROM event')
		events = {'events' : []}
		results = cur.fetchall()
		for event in results:
			events['events'].append(self.get(event[0]))
		return jsonify(events)

	def save(self, data):
		'''
			@todo - data validation and exception handling

			a dictionary with a key of Event and a list of values to be saved. If 'id' is included it will update, otherwise a new entry will be create.

			Optionally, you can also have a Tag key with a list of tag IDs to be saved to the event.

			ie:
				{ 'Event' : { 'name' : 'World War I' }, 'Tag' : [ 4, 7, 82 ] }
		'''
		fields = []
		values_to_save = []
		question_marks = []
		# @todo:
		saved_id = False
		for field, values in data['Event'].iteritems():
			if field is not 'id':
				fields.append(field)
				values_to_save.append(values)
				question_marks.append('?')
		if 'id' in data['Event']:
			saved_id = data['Event']['id']
			values_to_save.append(data['Event']['id'])
			self.db.execute('UPDATE event SET ' + ', '.join(fields) + ' VALUES( ' + ', '.join(question_marks) + ' ) WHERE id = ?', values_to_save)
		else:
			cursor = self.db.execute('INSERT INTO event (' + ', '.join(fields) + ') VALUES( ' + ', '.join(question_marks) + ' )', values_to_save)
			saved_id = cursor.lastrowid
		if 'Tag' in data and data['Tag']:
			self.db.execute('DELETE FROM event_tag WHERE event_id = ?', str(values['id']))
			tag_values = []
			# create a list of values to pass to
			for tag in event.Tag:
				tag_values.append('(' + saved_id + ', ' + tag + ')')

			self.db.execute('INSERT INTO event_tag (event_id, tag_id) VALUES ' + ', '.join(tag_values))

	def delete(self, event_id):
		pass

@app.route("/events/")
def events():
	events = Event()
	return events.get_all()

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
	db = database.get_db()
	db.execute('UPDATE event SET ' + ', '.join(updates) + where)
	db.commit()

	# Delete all current tag connections
	db.execute('DELETE FROM event_tag WHERE event_id = ' + str(values['id']))
	db.commit()

	# Add new tag connections
	tags_to_insert = []

	# delete all joins to prevent duplication


	for tag in tags['tags']:
		tags_to_insert.append('(' + values['id'] + ', ' + str(tag['id']) + ')')

	return 'all good!'

@app.route("/events/add/", methods=['GET', 'POST'])
def event_add():
	if request.method == 'POST':
		data = {'Event' : {}, 'Tags' : []}
		for field in request.json:
			if 'tags' in field:
				data['Tags'].append(field)
			else:
				data['Event'][field['name']] = field['value']
		data['Event']['date_from'] = data['Event']['date_from[year]'] + '-' + data['Event']['date_from[month]'] + '-' + data['Event']['date_from[day]']
		data['Event']['date_to'] = data['Event']['date_to[year]'] + '-' + data['Event']['date_to[month]'] + '-' + data['Event']['date_to[day]']
		data['Event'].pop('date_from[year]')
		data['Event'].pop('date_from[month]')
		data['Event'].pop('date_from[day]')
		data['Event'].pop('date_to[year]')
		data['Event'].pop('date_to[month]')
		data['Event'].pop('date_to[day]')
		data['Event'].pop('tag')
		event = Event()
		event.save(data)
		return jsonify(data)
	else:
		return render_template('add.html')
