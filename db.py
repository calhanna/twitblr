"""
Contains all the functions that interact with the database.
Adds 'db' to the session, allowing the database to be accessed from everywhere
"""

from flask import g, current_app, flash
import pymysql

def create_connection():
    try:
        return pymysql.connect(
            host="10.0.0.17",
            user="calhanna",
            # host="localhost",
            # user="root",
            password="ALBUM",
            db="calhanna",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.Cursor
        )
    except pymysql.err.OperationalError:
        print("Cucumber error. Please reinstall universe and restart. ")
        return DummyConnection()

def get_db():
    """ Adds a database connection to the session """
    if 'db' not in g:
        g.db = create_connection()

    return g.db

def teardown_db(exception):
    """ I don't know what this means tbh, I assume it's meant to close the connection if something crashes? Doesn't work. """
    db = g.pop('db', None)

    if db is not None:
        db.close()

class DummyConnection():
    """ Creates a fake database connection in case we can't access the real database """
    def __init__(self):
        pass

    def cursor(self):
        return False

    def __enter__(self):
        return self

    def commit(self):
        print("Dummy connection. Cannot commit to database")
        pass