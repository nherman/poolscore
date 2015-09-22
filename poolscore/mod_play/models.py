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

    # New instance instantiation procedure
    def __init__(self, date = None, home_team_id = None, away_team_id = None, ruleset = None, scoring_method = False):
        self.date = date
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.ruleset = ruleset
        self.scoring_method = scoring_method

    def __repr__(self):
        return '<Tourney %r, %r, home: %r, away: %r>' % (self.id, self.date, self.home_team_id, self.away_team_id)


class Player(common_models.Base):
    __tablename__ = 'player'
   
    # First Name
    first_name = db.Column(db.String(128), nullable = False)
    # Last Name
    last_name = db.Column(db.String(128), nullable = True)
    # Player ID
    player_id = db.Column(db.String(32), nullable = True)
    # handicap
    handicap = db.Column(db.Integer, nullable = False)

    # New instance instantiation procedure
    def __init__(self, first_name = None, last_name = None,
        player_id = None, handicap = None):
        self.first_name = first_name
        self.last_name = last_name
        self.player_id = player_id
        self.handicap = handicap

    def __repr__(self):
        return '<Player %r, %r %r>' % (self.id, self.first_name, self.last_name or "")


# assign players to teams
team_player = db.Table('team_player', common_models.Base.metadata,
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key = True),
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'), primary_key = True)
)
