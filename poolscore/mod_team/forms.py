from flask_wtf import Form
from wtforms import TextField, SelectMultipleField
from wtforms.validators import Required

from poolscore import app

class TeamForm(Form):
    name = TextField('Name', [Required(message = 'A team needs a name.')])
    location = TextField('Location')
    team_id = TextField('ID Number')
    players = SelectMultipleField('Players', coerce=int)

class PlayerForm(Form):
    first_name = TextField('First Name', [Required(message = 'A player needs a first name.')])
    last_name = TextField('Last Name', [Required(message = 'A player needs a Last name.')])
    player_id = TextField('Player ID', [Required(message = 'APA Player ID required.')])
    handicap = TextField('Handicap', [Required(message = 'Handicap required')])
    teams = SelectMultipleField('Teams', coerce=int)

