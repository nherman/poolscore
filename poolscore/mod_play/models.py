from sqlalchemy import and_
from sqlalchemy.orm import object_session
from sqlalchemy.sql import select, func

from poolscore import db
from poolscore.mod_common import models as common_models
from poolscore.mod_common.utils import Util, ModelUtil

class Tourney(common_models.Base):
    __tablename__ = 'tourney'
   
    # Tourney Date
    date = db.Column(db.DateTime, nullable = False)
    # Home Team ID
    home_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable = False)
    # Away Team ID
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable = False)
    # Ruleset Name
    ruleset = db.Column(db.String(128), nullable = False)
    # Scoring Method Name
    scoring_method = db.Column(db.String(128), nullable = False)
    # Winning Team ID
    winner_id =  db.Column(db.Integer, nullable = True)
    # Home Team Score
    home_score =  db.Column(db.Integer, nullable = True)
    # Away Team Score
    away_score =  db.Column(db.Integer, nullable = True)
    # Events
    events = db.Column(db.Text, nullable = True)
    # Data (?)
    data = db.Column(db.Text, nullable = True)

    home_team = db.relationship("Team", foreign_keys = [home_team_id])
    away_team = db.relationship("Team", foreign_keys = [away_team_id])

    all_matches = db.relationship("Match", backref = db.backref("tourney"), lazy="dynamic")

    @property
    def matches(self):
        return self.all_matches.filter(Match.deleted != True).all();


    # New instance instantiation procedure
    def __init__(self, active = True, date = None, home_team_id = None, away_team_id = None, ruleset = None, scoring_method = False, events = None, data = None):
        self.active = active
        self.date = date
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.ruleset = ruleset
        self.scoring_method = scoring_method
        self.events = events
        self.data = data

    def __repr__(self):
        return '<Tourney %r, %r, home: %r, away: %r>' % (self.id, self.date, self.home_team_id, self.away_team_id)

    @property
    def serialize_deep(self):
        d = Util.to_serializable_dict(self, self.__class__)
        d['home_team'] = Util.to_serializable_dict(self.home_team, self.home_team.__class__)
        d['away_team'] = Util.to_serializable_dict(self.away_team, self.away_team.__class__)
        return d

    @property
    def serialize(self):
        return self.serialize_shallow

    @property
    def serialize_shallow(self):
        d = Util.to_serializable_dict(self, self.__class__)
        return d

class Match(common_models.Base):
    __tablename__ = 'match'
   
    # Tourney ID
    tourney_id = db.Column(db.Integer, db.ForeignKey('tourney.id'), nullable = False)
    #Home Score
    home_score = db.Column(db.Integer, nullable = False)
    #Away Score
    away_score = db.Column(db.Integer, nullable = False)
    # Winner (team id)
    winner_id = db.Column(db.Integer, nullable = True)
    # Events
    events = db.Column(db.Text, nullable = True)
    # Data (?)
    data = db.Column(db.Text, nullable = True)

    players = db.relationship('MatchPlayer', cascade = "all, delete-orphan")
    all_games = db.relationship("Game", backref = db.backref("match"), lazy="dynamic")

    @property
    def games(self):
        return self.all_games.filter(Game.deleted != True).all();


    # Ordinal - position in match order that this game occured
    @property
    def ordinal(self):
        return object_session(self).\
            scalar(
                select([func.count(Match.id)]).\
                    where(and_(Match.tourney_id==self.tourney_id, Match.id <= self.id, Match.deleted != True))
            )

    @property
    def home_players(self):
        return self._get_players(is_home_team = True)

    @property
    def away_players(self):
        return self._get_players(is_home_team = False)

    def _get_players(self, is_home_team = None):
        players = []
        for mp in self.players:
            if(mp.is_home_team == is_home_team or is_home_team == None):
                players.append(mp.player)

        return players


    # New instance instantiation procedure
    def __init__(self, tourney_id = None, events = None, data = None, home_score = 0, away_score = 0):
        self.tourney_id = tourney_id
        self.home_score = home_score
        self.away_score = away_score
        self.events = events
        self.data = data

    def __repr__(self):
        return '<Match %r, (tourney %r)>' % (self.id, self.tourney_id)

    @property
    def serialize(self):
        return Util.to_serializable_dict(self, self.__class__)


class MatchPlayer(db.Model):
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
    is_home_team = db.Column(db.Boolean, nullable = False)
    player = db.relationship("Player")

    # New instance instantiation procedure
    def __init__(self, match_id = None, player_id = None, is_home_team = None):
        self.match_id = match_id
        self.player_id = player_id
        self.is_home_team = is_home_team

    def __repr__(self):
        return '<MatchPlayer match: %r, player: %r, home: %r>' % (self.match_id, self.player_id, self.is_home_team)

class Game(common_models.Base):
    __tablename__ = 'game'

    #Match ID
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable = False)
    # Winner (player id)
    winner_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable = True)
    # Events
    events = db.Column(db.Text, nullable = True)
    # Data (?)
    data = db.Column(db.Text, nullable = True)

    winner = db.relationship("Player")

    # Ordinal - position in match order that this game occured
    @property
    def ordinal(self):
        return object_session(self).\
            scalar(
                select([func.count(Game.id)]).\
                    where(and_(Game.match_id==self.match_id, Game.id <= self.id, Game.deleted != True))
            )

    def __init__(self, match_id = None, winner_id = 0, events = None, data = None):
        self.match_id = match_id
        self.winner_id = winner_id
        self.events = events
        self.data = data

    def __repr__(self):
        return '<Game %r, (match %r, tourney %r)>' % (self.id, self.match.id, self.match.tourney.id)

    @property
    def serialize(self):
        return Util.to_serializable_dict(self, self.__class__)


