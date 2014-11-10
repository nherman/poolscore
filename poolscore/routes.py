from datetime import date
from functools import wraps
from flask import g, session, render_template, request, redirect, url_for, flash
from . import app, get_db
from .database.entities import Tourney, Team

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
    '''Primary route for tournaments'''

    error = None
    # If active tourney exist then display tourney status view
    if session.get('activetourneyid'):
        '''Active Tourney'''

        # get active Tourney, home team, away team & matches from DB
        # save entities to context
        g.tourney = get_db().getInstanceById(Tourney, session.get('activetourneyid'), g.user.id)
        if (g.tourney == None):
            session.pop('activetourneyid', None)
            return redirect(url_for('tournament'))
    
        g.home_team = get_db().getInstanceById(Team, g.tourney.home_team_id, g.user.id)
        g.away_team = get_db().getInstanceById(Team, g.tourney.away_team_id, g.user.id)
        g.matches = get_db().getMatchesByTourneyId(g.tourney.id)

        #TODO: handle league selection
        g.league = {"name": "APA Eight Ball"}

        if request.method == 'POST':
            print("method equals post")
            print(request.form.keys())
            try:
                if (request.form['new_match']):
                    #Start a new Match
                    return redirect(url_for('match'))
            except KeyError:
                pass

            try:
                if (request.form['end_tourney']):
                    #End the Tourney
                    #TODO: set winner and prompt confirmation
                    session.pop('activetourneyid', None)
            except KeyError:
                pass

            return redirect(url_for('root'))

        return render_template('tournament.html')

    else: 
        '''No active Tourney'''
        teamDict = get_db().getTeamsByAccountId(g.user.id)
        if request.method == 'POST':
            '''Start new Tourney'''
            error = validate_tourney_start(request)
            if not error:
                #create new tourney in DB
                now = date.today()
                t = Tourney(date=now,
                            home_team_id = request.form['home_team'],
                            away_team_id = request.form['away_team'],
                            ruleset = "8ball",
                            scoring_method = "apa8ball")

                #save new tourney
                t.id = get_db().storeInstance(t, g.user.id)
                #set active tourney in session
                session['activetourneyid'] = t.id

                return redirect(url_for('tournament'))

        '''Display Tourney start page'''
        return render_template('start_tournament.html', teams = teamDict )


@app.route('/tournament/match', methods=['GET', 'POST'])
@validateAccess
def match():
    '''Match View'''

    error = None
    if session.get('activetourneyid'):
        # get active Tourney, home team, away team & matches from DB
        # save entities to context
        g.tourney = get_db().getInstanceById(Tourney, session.get('activetourneyid'), g.user.id)
        if (g.tourney != None):
            g.home_team = get_db().getInstanceById(Team, g.tourney.home_team_id, g.user.id)
            g.away_team = get_db().getInstanceById(Team, g.tourney.away_team_id, g.user.id)



            g.match = get_db().getInstanceById(Match, session.get('activetourneyid'), g.user.id)


            return render_template('404.html')



    redirect(url_for('tournament'))



