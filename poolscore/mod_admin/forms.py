from flask.ext.wtf import Form
from wtforms import TextField, SelectField, SelectMultipleField, DateField, IntegerField, BooleanField
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
    home_score = IntegerField('Home Score', [Optional()])
    away_score = IntegerField('Away Score', [Optional()])
    winner = SelectField('Winner', coerce=int)
    active = BooleanField('Active')

