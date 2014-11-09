from datetime import date
from functools import wraps
from flask import g, session, render_template, request, redirect, url_for, flash
from . import app, get_db
from .database.entities import Tourney

#decorators
def validateAccess(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('activeuser'):
            g.user = get_db().getAccountByUsername(session.get('activeuser'))
        else:
            print("decorated: no session")
            return redirect(url_for('login'))

        return f(*args, **kwargs)

    return decorated


#helpers
def validate_login(req):
    if req.form['username'] == "" or req.form['username'] == None:
        return "Please enter your user name."

    if req.form['password'] == "" or req.form['password'] == None:
        return "Please enter your password."

    data = get_db().getPasswordByUsername(req.form['username'])

    if data == None or not data['active']:
        return "Username doesn't exist"

    if data['password'] != req.form['password']:
        return "Password is incorrect"

    return 0

def validate_tourney_start(req):
    if (req.form['home_team'] == "" or
        req.form['home_team'] == None or
        req.form['away_team'] == "" or
        req.form['away_team'] == None):
        return "Please select home team and away team"
    elif (req.form['home_team'] == req.form['away_team']):
        flash("Playing with yourself again, eh?")

    return 0


#routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        error = validate_login(request)
        if not error:
            session['activeuser'] = request.form['username']
#            flash('You were logged in')
            return redirect(url_for('root'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('activeuser', None)
#    flash('You were logged out')
    return redirect(url_for('root'))


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/')
@validateAccess
def root():
    return render_template('index.html')


@app.route('/account')
@validateAccess
def account():
    return render_template('account.html')

@app.route('/tournament', methods=['GET', 'POST'])
@validateAccess
def tournament():
    error = None
    # If active tourney exist then display tourney status view
    if session.get('activetourneyid'):
        pass
    else: 
        teamDict = get_db().getTeamsByAccountId(g.user.id)
        if request.method == 'POST':
            error = validate_tourney_start(request)
            if not error:
                now = date.today()
                t = Tourney(date=now,
                            home_team_id = request.form['home_team'],
                            away_team_id = request.form['away_team'],
                            ruleset = "8ball",
                            scoring_method = "apa8ball")
                #save new tourney
                t.id = get_db().storeInstance(t)


        return render_template('start_tournament.html', teams = teamDict )





