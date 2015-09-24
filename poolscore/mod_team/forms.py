from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import Required

from poolscore import app

class TeamForm(Form):
    name = TextField('Name', [Required(message = 'A team needs a name.')])
    location = TextField('Location')
    team_id = TextField('ID Number')
