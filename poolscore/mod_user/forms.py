from flask_wtf import Form
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import Required, Email

from poolscore import app

class UserForm(Form):
    first_name = TextField('First Name', [Required(message = 'Enter user first name.')])
    last_name = TextField('Last Name', [Required(message = 'Enter user last name.')])
    email = TextField('Email Address', [Email(), 
        Required(message = 'Enter user email.')])
    username = TextField('Username', [Required(message = 'Enter username.')])
    password = PasswordField('Password', [
        Required(message = 'Must provide a password.')])
    active = BooleanField('Active')
