#!/usr/bin/python

from flask import Flask, request, render_template, jsonify, json
from flask.ext.sqlalchemy import SQLAlchemy
import os
import datetime

app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'timeline.db')

db = SQLAlchemy(app)

event_tag = db.Table('event_tag',
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
	tags = db.relationship('Tag', secondary=event_tag, backref=db.backref('events', lazy='dynamic'))

	def __init__(self, name, note, link, date_from, date_to, milestone):
		self.name = name
		self.note = note
		self.link = link
		self.date_from = date_from
		self.date_to = date_to
		self.milestone = milestone

	def __repr__(self):
		return '<Event %r>' % self.name

	def serialise(self):
		return {
			'id' : self.id,
			'name' : self.name,
			'note' : self.note,
			'link' : self.link,
			'date_from' : str(self.date_from),
			'date_to' : str(self.date_to),
			'milestone' : self.milestone,
			'tags' : self.tags_for_events(self.tags)
		}
	def _serialise(self):
		return {
			'id' : self.id,
			'name' : self.name,
			'note' : self.note,
			'link' : self.link,
			'date_from' : str(self.date_from),
			'date_to' : str(self.date_to),
			'milestone' : self.milestone
		}
	def tags_for_events(self, tags):
		return [tag._serialise() for tag in tags]


class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255))
	reference = db.Column(db.String(255))

	def __init__(self, name, reference):
		self.name = name
		self.reference = reference

	def __repr__(self):
		return '<Tag %r>' % self.name
	def serialise(self):
		return {
			'id' : self.id,
			'name' : self.name,
			'reference' : self.reference,
			'events' : self.events_for_tags(self.events)
		}
	def _serialise(self):
		return {
			'id' : self.id,
			'name' : self.name,
			'reference' : self.reference
		}
	def events_for_tags(self, events):
		return [event._serialise() for event in events]


################
# Start Routes #
################

@app.route("/")
def index():
	return app.send_static_file('index.html')

######################
# Start Event Routes #
######################

@app.route("/events/")
def events():
	events = Event.query.all()
	return jsonify(Events = [item.serialise() for item in events])

@app.route("/events/view/<int:event_id>")
def event_view(event_id):
	event = Event.query.filter_by(id=event_id).first()
	if event:
		return jsonify(event.serialise())
	else:
		return jsonify([])

@app.route("/events/edit/", methods=['POST'])
@app.route("/events/add/", methods=['GET', 'POST'])
def event_update(data = None):
	'''
	Create or update an event from json sent via POST. Returns error or event id

	'''
	if data == None:
		data = request.json
	else:
		data = json.loads(data)

	if 'id' in data:
		# If id is passed, update an existing record
		event = Event.query.get(data['id'])
		tags = []
		if not event:
			return jsonify({ 'error' : 'No record with this id' })

		for key, value in data.iteritems():
			if key == 'tags':
				for tag in data[key]:
					tags.append(Tag.query.get(tag))
				setattr(event, 'tags', tags)

			else:
				setattr(event, key, value)

		db.session.commit()
		return jsonify({ 'success' : 'Successfully updated', 'id' : event.id })

	else:
		# check if record already exists based on name
		event = Event.query.filter_by( name = data['name'].strip() )
		if event.count() > 0:
			return jsonify({ 'error' : "Event already exists"})

		# otherwise, create a blank data set
		event_data = {
			'name' : None,
			'note' : None,
			'link' : None,
			'date_from' : None,
			'date_to' : None,
			'milestone' : None
		}

		#fill in the vaules that we have
		for event in data:
			if event == 'date_from' or event == 'date_to':
				# made date fields date objects
				date = data[event].split('-')
				event_data[event] = datetime.date(int(date[0]), int(date[1]), int(date[2]))
			else:
				event_data[event] = data[event]

		# create a new event
		new_event = Event(
				event_data['name'],
				event_data['note'],
				event_data['link'],
				event_data['date_from'],
				event_data['date_to'],
				event_data['milestone']
			)

		if event_data['tags']:
			tags = []
			for tag in event_data['tags']:
				tags.append(Tag.query.get(tag))
			setattr(new_event, 'tags', tags)

		# save
		db.session.add(new_event)
		db.session.commit()

		return jsonify({ 'success' : 'Successfully saved', 'id' : new_event.id })

##############
# Tag Routes #
##############

@app.route("/tags/")
def get_tags():
	tags = Tag.query.all()
	return jsonify(tags = [tag.serialise() for tag in tags])

@app.route("/tags/view/<int:tag_id>")
def get_tag(tag_id):
	tag = Tag.query.filter_by(id=tag_id).first()
	if tag:
		return jsonify(tag.serialise())
	else:
		return jsonify([])

@app.route("/tags/add/", methods=['GET', 'POST'])
def add_tags():
	return 'add tag'

####################
# GOOOOOOOO Flask! #
####################

if __name__ == "__main__":
	app.debug = True
	app.run()
