from flask_wtf import Form
from wtforms import SelectField, DateField, DateTimeField
from wtforms.validators import Required, NumberRange, Optional

class NewTourneyForm(Form):
    __abstract__ = True

    home_team_id = SelectField('Home Team', [NumberRange(min=1,message = 'Select Home Team.')], coerce=int)
    away_team_id = SelectField('Away Team', [NumberRange(min=1,message = 'Select Away Team.')], coerce=int)
    date = DateField('Date', [Required(message = 'Enter tourney date')])
    start_time = DateTimeField('Start Time', [Required(message = 'Enter start time')], format="%I:%M %p", default="07:00")
    coin_toss = SelectField('Coin Toss', [Optional()], choices=[("","Select Home or Away"),('HOME','Home'),('AWAY','Away')])
    player_choice = SelectField('First Player Choice', choices=[("","Select Home or Away"),('HOME','Home'),('AWAY','Away')])
