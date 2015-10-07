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
    # Data (?)
    data = db.Column(db.Text, nullable = True)

    home_team = db.relationship("Team", foreign_keys = [home_team_id])
    away_team = db.relationship("Team", foreign_keys = [away_team_id])

    matches = db.relationship("Match", backref = db.backref("tourney"))

    # New instance instantiation procedure
    def __init__(self, active = True, date = None, home_team_id = None, away_team_id = None, ruleset = None, scoring_method = False, data = None):
        self.active = active
        self.date = date
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.ruleset = ruleset
        self.scoring_method = scoring_method
        self.data = data

    def __repr__(self):
        return '<Tourney %r, %r, home: %r, away: %r>' % (self.id, self.date, self.home_team_id, self.away_team_id)


class Match(common_models.Base):
    __tablename__ = 'match'
   
    # Tourney ID
    tourney_id = db.Column(db.Integer, db.ForeignKey('tourney.id'), nullable = False)
    # Ordinal - position in touney order that this match occured
    ordinal = db.Column(db.Integer, nullable = False)
    #Home Score
    home_score = db.Column(db.Integer, nullable = False)
    #Away Score
    away_score = db.Column(db.Integer, nullable = False)
    # Winner (team id)
    winner_id = db.Column(db.Integer, nullable = True)
    # Data (?)
    data = db.Column(db.Text, nullable = True)

    home_players = db.relationship('MatchPlayer', \
                   primaryjoin = "and_(Match.id == MatchPlayer.match_id, MatchPlayer.is_home_team == True)", \
                   lazy = "dynamic")
    away_players = db.relationship('MatchPlayer', \
                   primaryjoin = "and_(Match.id == MatchPlayer.match_id, MatchPlayer.is_home_team == False)", \
                   lazy = "dynamic")

    games = db.relationship("Game", backref = db.backref("match"), lazy = "dynamic")

    # Home Games
    home_games = db.relationship("Game", \
                 primaryjoin = "and_(Match.id == Game.match_id, Match.tourney_id == Game.winner_id)", \
                 lazy = "dynamic")
    #Away Games
    home_games = db.relationship("Game", \
                 primaryjoin = "and_(Match.id == Game.match_id, Match.tourney_id == Game.winner_id)", \
                 lazy = "dynamic")


    # New instance instantiation procedure
    def __init__(self, tourney_id = None, ordinal = None, data = None):
        self.tourney_id = tourney_id
        self.ordinal = ordinal
        self.home_score = 0
        self.away_score = 0
        self.data = None

    def __repr__(self):
        return '<Match %r, (tourney %r)>' % (self.id, self.tourney_id)

# assign players to matches
# match_player = db.Table('match_player', common_models.Base.metadata,
#     db.Column('match_id', db.Integer, db.ForeignKey('match.id'), primary_key = True),
#     db.Column('player_id', db.Integer, db.ForeignKey('player.id'), primary_key = True),
#     db.Column('is_home_team', db.Boolean, nullable = False)
# )

class MatchPlayer(common_models.Base):
    __tablename__ = 'matchplayer'

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


