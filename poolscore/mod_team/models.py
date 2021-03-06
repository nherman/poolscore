from poolscore import db
from poolscore.mod_common import models as common_models
from poolscore.mod_common.utils import Util, ModelUtil

# assign players to teams
team_player = db.Table('team_player', common_models.Base.metadata,
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key = True),
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'), primary_key = True)
)

class Team(common_models.Base):
    __tablename__ = 'team'
   
    # Team Name
    name = db.Column(db.String(128), nullable = False)
    # Team ID
    team_id = db.Column(db.String(32), nullable = False)
    # Team location
    location = db.Column(db.String(128), nullable = True)
    # Team owner
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Team Players
    players = db.relationship('Player', secondary=team_player,
        backref=db.backref('teams'))

    # New instance instantiation procedure
    def __init__(self, user_id = None, name = None,
        team_id = None, location = None):
        self.user_id = user_id
        self.name = name
        self.team_id = team_id
        self.location = location

    def __repr__(self):
        return '<Team %r, %r>' % (self.id, self.name)

    @property
    def serialize_deep(self):
        d = Util.to_serializable_dict(self, self.__class__)
        d['players'] = []
        for player in self.players:
            d['players'].append(player.serialize)
        return d

    @property
    def serialize(self):
        return self.serialize_shallow

    @property
    def serialize_shallow(self):
        d = Util.to_serializable_dict(self, self.__class__)
        return d

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
    # Player Teams
    # "teams" (see backref in Team)

    # New instance instantiation procedure
    def __init__(self, first_name = None, last_name = None,
        player_id = None, handicap = None):
        self.first_name = first_name
        self.last_name = last_name
        self.player_id = player_id
        self.handicap = handicap

    def __repr__(self):
        return '<Player %r, %r %r>' % (self.id, self.first_name, self.last_name or "")

    @property
    def serialize(self):
        return Util.to_serializable_dict(self, self.__class__)

