import unittest

from poolscore.tests import BaseTestCase

class APITestCase(BaseTestCase):

    def test_tourney_create_edit_delete(self):
        self.login('nick', 'password')

        rv = self.client.post('/play/new/', data=dict(
            home_team_id=1,
            away_team_id=2,
            date="2017-05-18",
            start_time="11%3A29+PM"
        ), follow_redirects=True)

        assert "nick's Team" in rv.data
