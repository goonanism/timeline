#!/usr/bin/python
from flask import request, render_template, jsonify, g
from timeline import app
import database

@app.route("/tags/")
def get_tags():
	#################################
	#								#
	#		Add Event Data			#
	#								#
	#################################
	db = dbase.get_db()
	cur = db.execute('SELECT * FROM tag')
	json_list = {'tags' : []}
	events = cur.fetchall()
	for event in events:
		json_list['tags'].append(dbase.dict_row(event))
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
