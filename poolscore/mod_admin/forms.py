from flask_wtf import Form
from wtforms import TextField, SelectField, SelectMultipleField, DateField, IntegerField, BooleanField, DateTimeField
from wtforms.validators import Required, NumberRange, Optional

from poolscore import app

class TourneyForm(Form):
    __abstract__ = True

    date = DateField('Date', [Required(message = 'Enter tourney date')])
    ruleset = TextField('Ruleset', [Required(message = 'Ruleset required')], default="APA8BALL")
    scoring_method = TextField('Scoring Method', [Required(message = 'Scoring method required')], default="APA8BALL")
    data = TextField('Data')
    owner_id = SelectField('Owner',[Required(message = 'Select Tourney Owner.')], coerce=int, default = 1)

class TourneyAddForm(TourneyForm):
    home_team_id = SelectField('Home Team', [NumberRange(min=1,message = 'Select Home Team.')], coerce=int)
    away_team_id = SelectField('Away Team', [NumberRange(min=1,message = 'Select Away Team.')], coerce=int)

class TourneyEditForm(TourneyForm):
    home_score = IntegerField('Home Score', [Optional(strip_whitespace = True)])
    away_score = IntegerField('Away Score', [Optional(strip_whitespace = True)])
    winner_id = SelectField('Winner', coerce=int)
    active = BooleanField('Active')
    events = TextField('Events')

class MatchForm(Form):
    __abstract__ = True

    events = TextField('Events')
    data = TextField('Data')
    owner_id = SelectField('Owner',[Required(message = 'Select Match Owner.')], coerce=int, default = 1)

class MatchAddForm(MatchForm):
    home_players = SelectMultipleField('Home Players', [Required(message = 'Select Home Players.')], coerce=int)
    away_players = SelectMultipleField('Away Players', [Required(message = 'Select Away Players.')], coerce=int)

class MatchEditForm(MatchForm):
    home_score = IntegerField('Home Score', [Optional(strip_whitespace = True)])
    away_score = IntegerField('Home Score', [Optional(strip_whitespace = True)])
    winner_id = SelectField('Winner', coerce=int)
    active = BooleanField('Active')

class GameForm(Form):
    winner_id = SelectField('Winner', coerce=int)
    events = TextField('Events')
    data = TextField('Data')
    active = BooleanField('Active', default = True)
    owner_id = SelectField('Owner',[Required(message = 'Select Game Owner.')], coerce=int, default = 1)
