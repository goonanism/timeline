#!/usr/bin/python

from flask import request, render_template, jsonify, g
from timeline import app
from database import Database


class Tag():
	def __init__(self):
		self.db = Database()
	def get(self, tag_id):
		results = { 'Tags' : {}, 'Events' : [] }
		tag = self.db.execute('SELECT * FROM tag WHERE id = ?', [tag_id])
		results['Tags'] = self.db.dict_row(tag.fetchone())
		events = self.db.execute('SELECT * FROM event JOIN event_tag ON event.id = event_tag.event_id WHERE event_tag.tag_id = ?', [tag_id])
		for event in events:
			results['Events'].append(self.db.dict_row(event))
		return results

	def get_all(self):
		tags = self.db.execute('SELECT id FROM tag')
		results = {'Tags' : []}
		for tag in tags.fetchall():
			print self.get(tag[0])
			results['Tags'].append(self.get(tag[0]))
		return results

	def save(self, data):
		pass
	def delete(self, tag_id):
		pass




@app.route("/tags/")
def get_tags():

	# @todo: event data
	tags = Tag()
	return jsonify(tags.get_all())

@app.route("/tags/view/<int:tag_id>")
def get_tag(tag_id):
	tags = Tag()
	return jsonify(tags.get(tag_id))

@app.route("/tags/add/", methods=['GET', 'POST'])
def add_tags():
	if request.method == 'POST':
		reference = request.json['tag'].replace(' ', '-').lower()
		db = dbase.get_db()

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
