import os
import unittest
import tempfile

from sqlite3 import dbapi2 as sqlite3

from poolscore import app
from poolscore import db

class BaseTestCase(unittest.TestCase):

    def setUp(self):

        # create tmp database
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']

        # get test client
        self.client = app.test_client()

        with app.app_context():

            # create tables
            db.create_all()

            # insert mock data
            connection = sqlite3.connect(app.config['DATABASE'])

            with app.open_resource('../bootstrap-data/bootstrap-sqlite.sql', mode='r') as f:
                connection.cursor().executescript(f.read())

            connection.commit()
            connection.close()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def login(self, username, password):
        return self.client.post('/auth/login/', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout/', follow_redirects=True)

