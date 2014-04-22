#!/usr/bin/python

from flask import Flask, request, render_template, jsonify, json, g

app = Flask(__name__)
app.config.from_object(__name__)

import timeline.database
import timeline.events
import timeline.tags

@app.route("/")
def index():
	return 'timeline!'

if __name__ == "__main__":
	app.debug = True
	app.run()