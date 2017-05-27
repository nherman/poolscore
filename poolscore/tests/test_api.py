from flask import json
from datetime import datetime

from poolscore.tests import BaseTestCase

class APITestCase(BaseTestCase):

    def test_tourney_create_edit_delete(self):
        self.login('nick', 'password')

        self.createTourney()

        #Get Tourney List
        res = self.client.get('/api/v1.0/tourneys.json')
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('tourneys' in data)
        self.assertEqual(len(data['tourneys']), 1)
        self.assertTrue('id' in data['tourneys'][0])
        tourney_id = data['tourneys'][0]['id']


        #Get Tourney Count
        res = self.client.get('/api/v1.0/tourneys/count.json')
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('count' in data)
        self.assertEqual(data['count'], 1)


        #Get One Tourney
        res = self.client.get('/api/v1.0/tourneys/{}.json'.format(tourney_id))
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('tourney' in data)
        tourney = data['tourney']
        self.assertEqual(tourney['home_team_id'], 1)
        self.assertEqual(tourney['away_team_id'], 2)
        self.assertTrue('events' in tourney)
        self.assertTrue('end_time' in tourney['events'])
        self.assertEqual(tourney['events']['end_time'], None)
        self.assertNotEqual(tourney['events']['start_time'], None)

        #Modify Tourney
        events = dict(
                    end_time = datetime.now().strftime("%I:%M %p")
                 )
        tourney = dict(
                    winner_id=1,
                    active=0,
                    events=events
                  )
        request = json.dumps(dict(tourney=tourney))
        res = self.client.put('/api/v1.0/tourneys/{}.json'.format(tourney_id), data=request)
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('tourney' in data)
        tourney = data['tourney']
        self.assertNotEqual(tourney['events']['end_time'], None)
        self.assertNotEqual(tourney['events']['start_time'], None)
        self.assertEqual(tourney['winner_id'], 1)
        self.assertEqual(tourney['active'], 0)
        self.assertEqual(tourney['deleted'], 0)

        #"Delete" Tourney
        tourney = dict(deleted=True)
        request = json.dumps(dict(tourney=tourney))
        res = self.client.put('/api/v1.0/tourneys/{}.json'.format(tourney_id), data=request)
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('tourney' in data)
        tourney = data['tourney']
        self.assertEqual(tourney['deleted'], 1)

        #Confirm Tourney list is empty
        res = self.client.get('/api/v1.0/tourneys.json')
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('tourneys' in data)
        self.assertEqual(len(data['tourneys']), 0)

    def test_match_create_edit_delete(self):
        self.login('nick', 'password')
        tourney = self.createTourney()

            ###
            # Create new match for tourney
            #
            # attributes format:
            # {
            #   "match": {
            #       "events": {
            #           match_event: "",
            #           ...
            #      },
            #       match_attribute: "",
            #       ...
            #   },
            #   "home_players": [],
            #   "away_players": [],
            # }
            ###




