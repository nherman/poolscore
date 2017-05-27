import os
import unittest
import tempfile

from sqlite3 import dbapi2 as sqlite3
from datetime import datetime

from flask import json

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

    def createTourney(self):
        timestamp = datetime.now()
        tourney_date = timestamp.strftime("%Y%m%dT%H:%M:%S")
        tourney_start_time = timestamp.strftime("%I:%M %p")
        events = dict(
                     start_time = tourney_start_time,
                     coin_toss = "HOME",
                     player_choice = "HOME"
                 )
        tourney = dict(
                      date=tourney_date,
                      home_team_id=1,
                      away_team_id=2,
                      scoring_method="APA8BALL",
                      ruleset="APA8BALL",
                      events = events
                  )
        request = json.dumps(dict(tourney=tourney))
        res = self.client.post('/api/v1.0/tourneys.json', data=request)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue('tourney' in data)

        return data['tourney']

