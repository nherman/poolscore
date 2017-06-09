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
        self.createMatch(tourney["id"])

        #Get Match List
        res = self.client.get('/api/v1.0/tourneys/{}/matches.json'.format(tourney["id"]))
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('matches' in data)
        self.assertEqual(len(data['matches']), 1)
        self.assertTrue('id' in data['matches'][0])
        match_id = data['matches'][0]['id']

        #Get One Match
        res = self.client.get('/api/v1.0/tourneys/{}/matches/{}.json'.format(tourney["id"], match_id))
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('match' in data)
        match = data['match']
        self.assertEqual(match['tourney_id'], tourney["id"])
        self.assertTrue('home_players' in match)
        self.assertEqual(match['home_players'][0]['id'], 1)
        self.assertTrue('away_players' in match)
        self.assertEqual(match['away_players'][0]['id'], 2)
        self.assertTrue('events' in match)
        self.assertTrue('lag' in match['events'])
        self.assertEqual(match['events']['lag'], "HOME")
        self.assertNotEqual(match['events']['sweep'], None)

        #Modify Match
        events = dict(
                    rubber = True
                 )
        match = dict(
                    winner_id=2,
                    active=0,
                    events=events
                  )
        request = json.dumps(dict(match=match))
        res = self.client.put('/api/v1.0/tourneys/{}/matches/{}.json'.format(tourney["id"], match_id), data=request)
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('match' in data)
        match = data['match']
        self.assertNotEqual(match['events']['rubber'], None)
        self.assertEqual(match['events']['rubber'], True)
        self.assertEqual(match['winner_id'], 2) #NEED MODEL CHANGE HERE. winner_id currently ois int of team id. change to HOME or AWAY
        self.assertEqual(match['active'], 0)
        self.assertEqual(match['deleted'], 0)

        #"Delete" Match
        match = dict(deleted=True)
        request = json.dumps(dict(match=match))
        res = self.client.put('/api/v1.0/tourneys/{}/matches/{}.json'.format(tourney["id"], match_id), data=request)
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('match' in data)
        match = data['match']
        self.assertEqual(match['deleted'], 1)

        #Confirm Match list is empty
        res = self.client.get('/api/v1.0/tourneys/{}/matches.json'.format(tourney["id"]))
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('matches' in data)
        self.assertEqual(len(data['matches']), 0)

    def test_game_create_edit_delete(self):
        self.login('nick', 'password')

        tourney = self.createTourney()
        match = self.createMatch(tourney["id"])
        self.createGame(tourney["id"], match["id"])

        #Get Game List
        res = self.client.get('/api/v1.0/tourneys/{}/matches/{}/games.json'.format(tourney["id"], match["id"]))
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('games' in data)
        self.assertEqual(len(data['games']), 1)
        self.assertTrue('id' in data['games'][0])
        game_id = data['games'][0]['id']

        #Get One Game
        res = self.client.get('/api/v1.0/tourneys/{}/matches/{}/games/{}.json'.format(tourney["id"], match["id"], game_id))
        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertTrue('game' in data)
        game = data['game']
        self.assertEqual(game['match_id'], tourney["id"])
        self.assertTrue('winner_id' in game)
        self.assertEqual(game['winner_id'], 0)
        self.assertTrue('events' in game)


        # TODO test is breaking here. game['events'] not iterable - returning None?
        self.assertTrue('breaker' in game['events'])
        self.assertEqual(game['events']['breaker'], "HOME")
        self.assertEqual(game['events']['special_event'], None)
        self.assertEqual(game['events']['innings'], 0)
        self.assertEqual(game['events']['home_coaches'], 0)
        self.assertEqual(game['events']['home_safes'], 0)
        self.assertEqual(game['events']['away_coaches'], 0)
        self.assertEqual(game['events']['away_safes'], 0)



