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
    winner =  db.Column(db.Integer, nullable = True)
    # Home Team Score
    home_score =  db.Column(db.Integer, nullable = True)
    # Away Team Score
    away_score =  db.Column(db.Integer, nullable = True)
    # Data (?)
    data = db.Column(db.Text, nullable = True)

    home_team = db.relationship("Team", foreign_keys = [home_team_id])
    away_team = db.relationship("Team", foreign_keys = [away_team_id])

    # New instance instantiation procedure
    def __init__(self, active = True, date = None, home_team_id = None, away_team_id = None, ruleset = None, scoring_method = False, data = None):
        self.active = active
        self.date = date
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.ruleset = ruleset
        self.scoring_method = scoring_method
        self.data = None

    def __repr__(self):
        return '<Tourney %r, %r, home: %r, away: %r>' % (self.id, self.date, self.home_team_id, self.away_team_id)


class Match(common_models.Base):
    __tablename__ = 'match'
   
    # Tourney ID
    tourney_id = db.Column(db.Integer, db.ForeignKey('tourney.id'), nullable = False)
    # Ordinal - position in touney order that this match occured
    ordinal = db.Column(db.Integer, nullable = False)
    # Home Games
    home_games = db.Column(db.Integer, nullable = False)
    #Away Games
    away_games = db.Column(db.Integer, nullable = False)
    #Home Score
    home_score = db.Column(db.Integer, nullable = False)
    #Away Score
    away_score = db.Column(db.Integer, nullable = False)
    # Winner (team id)
    winner_id = db.Column(db.Integer, nullable = True)
    # Data (?)
    data = db.Column(db.Text, nullable = True)

    # New instance instantiation procedure
    def __init__(self, tourney_id = None, ordinal = None):
        self.tourney_id = tourney_id
        self.ordinal = ordinal
        self.home_games = 0
        self.away_games = 0
        self.home_score = 0
        self.away_score = 0

    def __repr__(self):
        return '<Match %r, (tourney %r)>' % (self.id, self.tourney_id)

# assign players to matches
match_player = db.Table('match_player', common_models.Base.metadata,
    db.Column('match_id', db.Integer, db.ForeignKey('match.id'), primary_key = True),
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'), primary_key = True),
    db.Column('is_home_team', db.Boolean, nullable = False)
)

class Game(common_models.Base):
    __tablename__ = 'game'

    #Match ID
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable = False)
    # Ordinal - position in match order that this game occured
    ordinal = db.Column(db.Integer, nullable = False)
    # Winner (team id)
    winner_id = db.Column(db.Integer, nullable = True)
    # Data (?)
    data = db.Column(db.Text, nullable = True)

# record game events
game_events = db.Table('game_events', common_models.Base.metadata,
    db.Column('id', db.Integer, primary_key = True),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'), nullable = False),
    db.Column('name', db.Text, nullable = False),
    db.Column('value', db.Text, nullable = True)
)

# record match events
match_events = db.Table('match_events', common_models.Base.metadata,
    db.Column('id', db.Integer, primary_key = True),
    db.Column('match_id', db.Integer, db.ForeignKey('match.id'), nullable = False),
    db.Column('name', db.Text, nullable = False),
    db.Column('value', db.Text, nullable = True)
)

# record tourney events
tourney_events = db.Table('tourney_events', common_models.Base.metadata,
    db.Column('id', db.Integer, primary_key = True),
    db.Column('tourney_id', db.Integer, db.ForeignKey('tourney.id'), nullable = False),
    db.Column('name', db.Text, nullable = False),
    db.Column('value', db.Text, nullable = True)
)


