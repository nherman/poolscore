from functools import wraps
from flask import g, session, render_template, request, redirect, url_for, flash
from . import app, get_db
from .database.entities import User

#decorators
def validateAccess(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('activeuser'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


#helpers
def validate_login(req):
    if req.form['username'] == "" or req.form['username'] == None:
        return "Please enter your user name."

    if req.form['password'] == "" or req.form['password'] == None:
        return "Please enter your password."

    data = get_db().get_password_by_username(req.form['username'])

    if data == None or not data['active']:
        return "Username doesn't exist"

    if data['password'] != req.form['password']:
        return "Password is incorrect"

    return 0

#routes
@app.route('/')
@validateAccess
def root():
    user = get_db().get_user_by_name(session.get('activeuser'))
    print(user.date_created)

    return render_template('index.html', test=app.config['DATABASE'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        error = validate_login(request)
        if not error:
            session['activeuser'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('root'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('activeuser', None)
    flash('You were logged out')
    return redirect(url_for('root'))



