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
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
ps_env = os.getenv('PS_ENV', 'Dev') + 'Config'
app.config.from_object('config.' + ps_env)
app.permanent_session_lifetime = timedelta(minutes=30)

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def not_found(error):
    return render_template('403.html'), 403


# Import a module using its blueprint handler variable
from mod_auth.controllers import mod_auth as auth_module
from mod_home.controllers import mod_home as home_module
from mod_team.controllers import mod_team as team_module
from mod_play.controllers import mod_play as play_module
from mod_api.controllers import mod_api as api_module
from mod_admin.controllers import mod_admin as admin_module
from mod_user.controllers import mod_user as user_module

# Register blueprints
app.register_blueprint(auth_module)
app.register_blueprint(home_module)
app.register_blueprint(team_module)
app.register_blueprint(play_module)
app.register_blueprint(api_module)
app.register_blueprint(admin_module)
app.register_blueprint(user_module)

# Register Jinja Globals & Custom Filters
from mod_common.jinja_globals import globals, filters
for key, fn in globals.items():
    app.jinja_env.globals[key] = fn
for key, fn in filters.items():
    app.jinja_env.filters[key] = fn
