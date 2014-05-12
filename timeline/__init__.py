#!/usr/bin/python

from flask import Flask, request, render_template, jsonify, json, g
import os

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'timeline.db'),
	DEBUG=True
))
app.config.from_envvar('TIMELINE_SETTINGS', silent=True)

import timeline.events
import timeline.tags

@app.route("/")
def index():
	return 'timeline!'

if __name__ == "__main__":
	app.debug = True
	app.run()
