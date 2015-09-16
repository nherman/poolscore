# -*- coding: utf-8 -*-
"""
    poolscore
    ~~~~~~~~~~~~~~

    description?

    :copyright: 2014 by Nicholas Herman
    :license: ???, see ??? for more details.
"""

import os
from datetime import timedelta
from flask import Flask, g, render_template, redirect, url_for, session
from flask.ext.sqlalchemy import SQLAlchemy
from .database import DbManager

app = Flask(__name__)
#app.config.from_object('config')
ps_env = os.getenv('PS_ENV', 'Dev') + 'Config'
app.config.from_object('config.' + ps_env)
app.permanent_session_lifetime = timedelta(minutes=30)

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

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

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def not_found(error):
    return render_template('403.html'), 403

# Global index page (redirect to the home index)
@app.route('/', methods = ['GET'])
def index():
    return redirect(url_for('home.index'), code = 301)


# Import a module using its blueprint handler variable
from mod_home.controllers import mod_home as home_module

# Register blueprints
app.register_blueprint(home_module)



#initialize routes
#from . import routes