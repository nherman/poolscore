# -*- coding: utf-8 -*-
"""
    poolscore
    ~~~~~~~~~~~~~~

    description?

    :copyright: 2014 by Nicholas Herman
    :license: ???, see ??? for more details.
"""

from flask import Flask, g, render_template
from .database import DbManager

app = Flask(__name__)
app.config.from_object('config')


###
# Attach DB instance to flask context
###
def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = DbManager().open(db_config=app.config['DATABASE'])
    return db


def close_db():
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.before_request
def before_request():
    '''init db connection on each request'''
    get_db()


@app.teardown_request
def teardown_request(exception):
    '''close connection on each response'''
    close_db()


###
# Routes
###

# handle 404s
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


#initialize routes
from . import routes