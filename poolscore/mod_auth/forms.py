from flask_wtf import Form

from wtforms import TextField, PasswordField
from wtforms.validators import Required

# Define the login form (WTForms)
class LoginForm(Form):
    username = TextField('Username', [
        Required(message = 'Forgot your username?')])
    password = PasswordField('Password', [
        Required(message = 'Must provide a password.')])
