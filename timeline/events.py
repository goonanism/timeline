#!/usr/bin/python

from flask import request, render_template, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from timeline import app
db = SQLAlchemy(app)

tags = db.Table('event_tag',
	db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
	db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

class Event(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255))
	note = db.Column(db.Text())
	link = db.Column(db.String(255))
	date_from = db.Column(db.Date())
	date_to = db.Column(db.Date())
	milestone = db.Column(db.Boolean)

	# tags = db.relationship('Tag', secondary=tags,
    #     backref=db.backref('event', lazy='dynamic'))

	def __repr__(self):
		return '<Event %r>' % self.name

def event_to_json(data):
	d = data.__dict__
	d.pop('_sa_instance_state')
	d['date_from'] = str(d['date_from'])
	d['date_to'] = str(d['date_to'])
	return d

@app.route("/events/")
def events():
	events = Event.query.all()
	json = {'Events' : []}
	for row in events:
		json['Events'].append(event_to_json(row))
	return jsonify(json)

@app.route("/events/view/<int:event_id>")
def event_view(event_id):
	event = Event.query.filter_by(id=event_id).first()
	json = event_to_json(event)
	return jsonify(json)

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
			data['Tags'] = []
			for tag in value['tags']:
				data['Tags'].append(tag['id'])

	event = Event()
	event.save(data)

	return event.save(data)

@app.route("/events/add/", methods=['GET', 'POST'])
def event_add():
	if request.method == 'POST':
		data = {'Event' : {}, 'Tags' : []}
		for field in request.json:
			if 'tags' in field:
				for tag in field['tags']:
					data['Tags'].append(tag['Tag']['id'])
			else:
				data['Event'][field['name']] = field['value']
		event = Event()
		event_id = event.save(data)
		return jsonify(data)
	else:
		return render_template('add.html')
