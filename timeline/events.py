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
			a dictionary with a key of Event and a list of values to be saved. If 'id' is included it will update, otherwise a new entry will be create.

			Optionally, you can also have a Tag key with a list of tag IDs to be saved to the event.

			ie:
				{ 'Event' : { 'name' : 'World War I' }, 'Tag' : [ 4, 7, 82 ] }
		'''

		# values for query
		fields = []
		values_to_save = []
		question_marks = []
		saved_id = False

		# create the relevant lists
		for field, values in data['Event'].iteritems():
			if field != 'id':
				fields.append(field)
				values_to_save.append(values)
				question_marks.append('?')

		# if it's an update - ie there is an id
		if 'id' in data['Event']:
			saved_id = data['Event']['id']
			values_to_save.append(int(data['Event']['id']))
			set_fields = ' = ?, '.join(fields) + ' = ?'
			self.db.execute('UPDATE event SET ' + set_fields + ' WHERE id = ?', values_to_save)
			self.db.commit()

		# otherwise create a new entry:
		else:
			cursor = self.db.execute('INSERT INTO event (' + ', '.join(fields) + ') VALUES( ' + ', '.join(question_marks) + ' )', values_to_save)
			self.db.commit()
			saved_id = cursor.lastrowid

		# if 'Tag' in data and data['Tag']:
		# 	self.db.execute('DELETE FROM event_tag WHERE event_id = ?', str(values['id']))
		# 	tag_values = []
		# 	# create a list of values to pass to
		# 	for tag in event.Tag:
		# 		tag_values.append('(' + saved_id + ', ' + tag + ')')
		#
		# 	self.db.execute('INSERT INTO event_tag (event_id, tag_id) VALUES ' + ', '.join(tag_values))
		return saved_id

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
	event = Event()
	return render_template('edit.html', event=event.get(event_id))

@app.route("/events/edit/", methods=['POST'])
def event_update():
	data = { 'Event' : {} }
	for value in request.json:
		if value.has_key('name'):
			data['Event'][value['name']] = value['value']
		if value.has_key('tags'):
			data['Tags'] = value

	event = Event()
	event.save(data)

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
		event = Event()
		event_id = event.save(data)
		print event_id
		return jsonify(data)
	else:
		return render_template('add.html')
