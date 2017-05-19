#!/usr/bin/env python

from poolscore import app
from poolscore import db

# This will create the database file using SQLAlchemy
if app.config.get('FORCE_SQLALCHEMY_CREATE_TABLES', False):
    db.create_all()

#run dev server
app.run(host='0.0.0.0', port=8080, debug=True)

