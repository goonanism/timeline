#!/usr/bin/python

from flask import request, render_template, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from timeline import app
db = SQLAlchemy(app)

class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255))
	reference = db.Column(db.String(255))

	def __repr__(self):
		return '<Tag %r>' % self.name

def tag_to_json(data):
	d = data.__dict__
	d.pop('_sa_instance_state')
	return d

@app.route("/tags/")
def get_tags():
	# @todo: event data
	tags = Tag.query.all()
	json = {'Tags' : []}
	for row in tags:
		json['Tags'].append(tag_to_json(row))
	return jsonify(json)

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
