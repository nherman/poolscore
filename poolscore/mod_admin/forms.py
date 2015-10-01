from flask.ext.wtf import Form
from wtforms import TextField, SelectField, DateField, IntegerField, BooleanField
from wtforms.validators import Required

from poolscore import app

class TourneyForm(Form):
    __abstract__ = True

    date = DateField('Date', [Required(message = 'Enter tourney date')])
    ruleset = TextField('Ruleset', [Required(message = 'Ruleset required')], default="APA8BALL")
    scoring_method = TextField('Scoring Method', [Required(message = 'Scoring method required')], default="APA8BALL")
    data = TextField('Data')

class TourneyAddForm(TourneyForm):
    home_team = IntegerField('Home Team', [Required(message = 'Select Home Team.')])
    away_team = IntegerField('Away Team', [Required(message = 'Select Away Team.')])

class TourneyEditForm(TourneyForm):
    home_score = IntegerField('Home Score')
    away_score = IntegerField('Away Score')
    active = BooleanField('Active')

