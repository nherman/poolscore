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
        """
            APA Tourney events:

            "coin_toss": None,
            "player_choice": None,
            "start_time": None,
            "end_time": None
        """
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

    def createMatch(self, tourney_id, match=None):
        """
            APA Match events:

            "lag": None,
            "sweep": False,
            "rubber": False
        """
        if match is None:
            events = dict(
                lag = "HOME"
            )
            match = dict(
                home_players=[1],
                away_players=[2],
                events = events
            )

        request = json.dumps(dict(match=match))

        res = self.client.post('/api/v1.0/tourneys/{}/matches.json'.format(tourney_id), data=request)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue('match' in data)

        return data['match']

    def createGame(self, tourney_id, match_id, game=None):
        """
            APA Game events:

            "breaker":None,
            "innings": 0,
            "home_coaches": 0,
            "home_safes": 0,
            "away_coaches": 0,
            "away_safes": 0,
            "special_event_options": (None,"8_break","break_run","early_8","scratch_8","forfeit"),
            "special_event": None
        """
        if game is None:
            events = dict(
                breaker = "HOME"
            )
            game = dict(
                events = events
            )

        request = json.dumps(dict(game=game))

        res = self.client.post('/api/v1.0/tourneys/{}/matches/{}/games.json'.format(tourney_id, match_id), data=request)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue('game' in data)

        return data['game']