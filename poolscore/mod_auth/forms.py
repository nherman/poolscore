from flask.ext.wtf import Form

from wtforms import TextField, PasswordField
from wtforms.validators import Required

# Define the login form (WTForms)
class LoginForm(Form):
    email = TextField('Email Address', [
        Required(message = 'Forgot your email address?')])
    password = PasswordField('Password', [
        Required(message = 'Must provide a password.')])
