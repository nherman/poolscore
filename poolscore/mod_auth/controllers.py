from flask import Blueprint, request, render_template, \
                  flash, session, redirect, url_for

from poolscore import db
from poolscore import app
from poolscore.mod_auth.forms import LoginForm
from poolscore.mod_auth.models import User
from poolscore.mod_common.utils import SecurityUtil, Util

#from poolscore.mod_common.passwords.validators import PasswordValidator, ValidationError

mod_auth = Blueprint('auth', __name__, url_prefix = '/auth')

@mod_auth.after_request
def remove_if_invalid(response):
    if "__invalidate__" in session:
        response.delete_cookie(app.session_cookie_name)
    return response

@mod_auth.route('/login/', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter(User.username == username).first()

        if user and user.active and user.check_password(form.password.data):
            SecurityUtil.create_session(user)
            flash('Welcome %s %s' % (user.first_name, user.last_name), 'info')
            return redirect(url_for('index'))
        flash('Wrong username or password', 'error')
    return render_template("auth/login.html", form = form)

@mod_auth.route('/logout/', methods = ['GET', 'POST'])
def logout():
    SecurityUtil.invalidate_session()
    flash('You were logged out', 'success')
    return redirect(url_for('index'))
