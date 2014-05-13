#!/usr/bin/python

from flask import g
import sqlite3

from timeline import app

class Database:
    def __init__(self):
        self.db = self.get_db()
    def connect_db(self):
    	"""Connects to the specific database."""
    	rv = sqlite3.connect(app.config['DATABASE'])
    	rv.row_factory = sqlite3.Row
    	return rv

    def get_db(self):
    	"""Opens a new database connection if there is none yet for the
    	current application context.
    	"""
    	if not hasattr(g, 'sqlite_db'):
    		g.sqlite_db = self.connect_db()
    	return g.sqlite_db

    def execute(self, query, variables = None):
        if variables:
            return self.db.execute(query, variables)
        return self.db.execute(query)

    @app.teardown_appcontext
    def close_db(error):
    	"""Closes the database again at the end of the request."""
    	if hasattr(g, 'sqlite_db'):
    		g.sqlite_db.close()

    def dict_row(self, row):
    	return dict(zip(row.keys(), row))
