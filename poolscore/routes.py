from datetime import date
from functools import wraps
from flask import g, session, render_template, request, redirect, url_for, flash
from . import app, get_db
from .database import PermissionsError
from .database.entities import Tourney, Team, Match

#decorators
def validateAccess(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('activeuser'):
            g.user = get_db().getAccountByUsername(session.get('activeuser'))
        else:
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

def validate_match_start(req):
    if (req.form['home_players'] == "" or
        req.form['home_players'] == None or
        req.form['away_players'] == "" or
        req.form['away_players'] == None):
        return "Please select players"
    elif (req.form['home_players'] == req.form['away_players']):
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
    session.clear()
#    flash('You were logged out')
    return redirect(url_for('root'))


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/')
@validateAccess
def root():
    tourneyCount = get_db().getTourneyCountByAccountId(g.user.id)
    return render_template('index.html', tourneys = tourneyCount['count'])


@app.route('/account')
@validateAccess
def account():
    return render_template('account.html')

@app.route('/tournaments')
@validateAccess
def tournaments():
    tourneys = get_db().getTourneyListByAccountId(g.user.id)
    return render_template('tournaments.html', tourneys = tourneys)


@app.route('/tournament', methods=['GET', 'POST'])
@validateAccess
def tournament():
    '''Primary route for tournaments'''

    error = None
    # If active tourney exist then display tourney status view
    if request.args.get('tid') or request.form.get('tid'):
        '''Active Tourney'''

        if request.args.get('tid'):
            tourney_id = request.args.get('tid')
        elif request.form.get('tid'):
            tourney_id = request.form.get('tid')

        # get active Tourney, home team, away team & matches from DB
        # save entities to context
        try:
            g.tourney = get_db().getInstanceById(Tourney, tourney_id, g.user.id)
            g.home_team = get_db().getInstanceById(Team, g.tourney.home_team_id, g.user.id)
            g.away_team = get_db().getInstanceById(Team, g.tourney.away_team_id, g.user.id)
        except AttributeError:
            flash("No Tournament with ID {} found".format(tourney_id))
        except PermissionsError:
            pass

        if (g.tourney == None or g.home_team == None or g.away_team == None):
            if (session.get('activetourneyid') == tourney_id):
                session.pop('activetourneyid', None)
            return redirect(url_for('tournament'))
    

        #get all matches for tourney
        g.matches = get_db().getMatchesByTourneyId(g.tourney.id)

        #TODO: handle league selection
        g.league = {"name": "APA Eight Ball"}

        if request.method == 'POST':
            try:
                if (request.form['new_match']):
                    #Start a new Match
                    return redirect(url_for('match',tid=g.tourney.id))
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
                session['activetourneyid'] = str(t.id)

                return redirect(url_for('tournament',tid=t.id))

        '''Display Tourney start page'''
        return render_template('start_tournament.html', teams = teamDict, error=error )


@app.route('/tournament/match', methods=['GET', 'POST'])
@validateAccess
def match():
    '''Match View'''

    error = None
    if request.args.get('mid') or request.form.get('mid'):
        '''if a match id is passed then try to edit that match'''

        if request.args.get('mid'):
            match_id = request.args.get('mid')
        elif request.form.get('mid'):
            match_id = request.form.get('mid')

        # get active match, tourney, home team, away team, players & games from DB
        # save entities to context
        try:
            g.match = get_db().getInstanceById(Match, match_id, g.user.id)
            g.tourney = get_db().getInstanceById(Tourney, g.match.tourney_id, g.user.id)
            g.home_team = get_db().getInstanceById(Team, g.tourney.home_team_id, g.user.id)
            g.away_team = get_db().getInstanceById(Team, g.tourney.away_team_id, g.user.id)
            g.home_players = []
            g.away_players = []
            for player in g.match.home_player_ids:
                g.home_players.append(get_db().getInstanceById(Team, g.tourney.home_team_id, g.user.id))
            for player in g.match.away_player_ids:
                g.away_players.append(get_db().getInstanceById(Team, g.tourney.away_team_id, g.user.id))
        except AttributeError:
            flash("No Match with ID {} found".format(match_id))
        except PermissionsError:
            pass

        if g.tourney == None:
            return redirect(url_for('tournament'))
        if (g.match == None or len(g.home_players) == 0 or len(g.home_players) == 0):
            return redirect(url_for('tournament', tid=g.tourney.id))
    
        #get all games for tourney
        g.games = get_db().getGamesByMatchId(g.tourney.id)

        #TODO: handle league selection
        g.league = {"name": "APA Eight Ball"}

        return render_template('match.html')

    elif request.args.get('tid') or request.form.get('tid'):
        '''if a tourney id is passed then try to start a new match'''

        if request.args.get('tid'):
            tourney_id = request.args.get('tid')
        elif request.form.get('tid'):
            tourney_id = request.form.get('tid')

        try:
            g.tourney = get_db().getInstanceById(Tourney, tourney_id, g.user.id)
            g.home_team = get_db().getInstanceById(Team, g.tourney.home_team_id, g.user.id)
            g.away_team = get_db().getInstanceById(Team, g.tourney.away_team_id, g.user.id)
        except AttributeError:
            flash("No Tournament with ID {} found".format(tourney_id))
        except PermissionsError:
            pass
        if (g.tourney == None):
            return redirect(url_for('tournament', tid=tourney_id))

        #TODO: handle league selection
        g.league = {"name": "APA Eight Ball"}

        if request.method == 'POST':
            '''Start new Match'''
            error = validate_match_start(request)
            if not error:
                #create new match in DB
                m = Match(tourney_id=g.tourney.id,
                        home_player_ids = request.form['home_players'],
                        away_player_ids = request.form['away_players'])

                #save new match
                m.id = get_db().storeInstance(m, g.user.id)
                return redirect(url_for('match', tid=g.tourney.id, mid=m.id))

        g.homePlayers = get_db().getPlayersByAccountIdForTeam(g.user.id, g.tourney.home_team_id)
        g.awayPlayers = get_db().getPlayersByAccountIdForTeam(g.user.id, g.tourney.away_team_id)
        g.otherPlayers = get_db().getPlayersByAccountIdNotOnTeams(g.user.id, [g.tourney.home_team_id,g.tourney.away_team_id])

        '''Display Match start page'''
        return render_template('start_match.html', error=error )

    #Something went wrong - redirect back to rooot
    return redirect(url_for('root'))



