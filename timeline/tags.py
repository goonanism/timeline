#!/usr/bin/python

from flask import request, render_template, jsonify, g
from timeline import app
from database import Database


class Tag():
	def __init__(self):
		self.db = Database()
	def get(self, tag_id, recursive = True):
		results = { 'Tag' : {} }
		tag = self.db.execute('SELECT * FROM tag WHERE id = ?', [tag_id])
		results['Tag'] = self.db.dict_row(tag.fetchone())

		### we can turn off getting events
		if recursive:
			results['Events'] = []
			events = self.db.execute('SELECT * FROM event JOIN event_tag ON event.id = event_tag.event_id WHERE event_tag.tag_id = ?', [tag_id])
			for event in events:
				results['Events'].append(self.db.dict_row(event))
		return results

	def get_all(self, recursive = True):
		tags = self.db.execute('SELECT id FROM tag')
		results = {'Tags' : []}
		for tag in tags.fetchall():
			results['Tags'].append(self.get(tag[0], recursive))
		return results

	def save(self, data):

		fields = []
		values_to_save = []
		question_marks = []
		saved_id = False

		for field, value in data['Tag'].iteritems():
			if field != 'id':
				fields.append(field)
				values_to_save.append(value)
				question_marks.append('?')
		if 'id' in data['Tag']: # ie if it's an update
			saved_id = int(data['Tag']['id'])
			values_to_save.append(saved_id)
			set_fields = ' = ?, '.join(fields) + ' = ?'
			self.db.execute('UPDATE tag SET ' + set_fields + ' WHERE id = ?', values_to_save)
			self.db.commit()

		else:
			cursor = self.db.execute('INSERT INTO tag (' + ', '.join(fields) + ') VALUES( ' + ', '.join(question_marks) + ' )', values_to_save)
			self.db.commit()
			saved_id = cursor.lastrowid

		return saved_id

	def exists(self, reference):
		cur = self.db.execute("SELECT * FROM tag WHERE reference = '" + reference + "'")
		tag_exists = cur.fetchone();
		if tag_exists:
			return tag_exists
		return False

	def delete(self, tag_id):
		pass

@app.route("/tags/")
def get_tags():

	# @todo: event data
	tags = Tag()
	return jsonify(tags.get_all(False))

@app.route("/tags/view/<int:tag_id>")
def get_tag(tag_id):
	tags = Tag()
	return jsonify(tags.get(tag_id))

@app.route("/tags/add/", methods=['GET', 'POST'])
def add_tags():
	if request.method == 'POST':

		reference = request.json['tag'].replace(' ', '-').lower()

		tag = Tag()
		exists = tag.exists(reference)
		if exists:
			return jsonify(exists)

		data = {'Tag' : {'name' : request.json['tag'], 'reference' : reference }}

		tag.save(data)


		# Otherwise create new tag
		db.execute('insert into tag (name, reference) values(?, ?)', [request.json['tag'], reference])
		db.commit()

		# Then get new tag details and return it
		cur = db.execute("SELECT * FROM tag WHERE reference = '" + reference + "'")
		return jsonify(cur.fetchone())
	else:
		return False
