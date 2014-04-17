#!/usr/bin/python

from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "Timeline amazing!"

@app.route("/add/")
def add():
	return "add"

if __name__ == "__main__":
    app.run()