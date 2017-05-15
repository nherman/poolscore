#run dev server
from poolscore import app
from poolscore import db

# This will create the database file using SQLAlchemy
if app.config.get('FORCE_SQLALCHEMY_CREATE_TABLES', False):
    db.create_all()

app.run(host='0.0.0.0', port=8080, debug=True)

