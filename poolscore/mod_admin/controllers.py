from datetime import date

from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

from poolscore import db
from poolscore import app

from poolscore.mod_common.models import EntityUser
from poolscore.mod_auth.models import User
from poolscore.mod_team.models import Team, Player
from poolscore.mod_play.models import Tourney, Match, Game, MatchPlayer
from poolscore.mod_common.utils import SecurityUtil
from poolscore.mod_admin.forms import TourneyAddForm, TourneyEditForm, \
                                      MatchAddForm, MatchEditForm, \
                                      GameAddForm, GameEditForm



mod_admin = Blueprint('admin', __name__, url_prefix = '/admin')


@mod_admin.route('/', methods = ['GET'])
def index():
    return redirect(url_for('.tourneys'))

@mod_admin.route('/tourney/', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourneys():
    tourneys = Tourney.query.order_by(Tourney.date_created).all()

    return render_template('admin/tourney/index.html',
        tourneys = tourneys)

@mod_admin.route('/tourney/<int:tourney_id>/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourney(tourney_id):
    tourney = Tourney.query.filter_by(id=tourney_id).first()
    if not tourney:
        return render_template('404.html'), 404

    tourney_entityuser = EntityUser.query.filter_by(entity = "Tourney", row_id = tourney.id).order_by(EntityUser.user_id.desc()).first()
    form = TourneyEditForm(request.form)

    user_choices = [(u.id, "{}, {} ({})".format(u.last_name, u.first_name, u.id)) for u in User.query.all()]
    form.owner_id.choices = user_choices

    teams = Team.query.filter(Team.id.in_([tourney.home_team_id, tourney.away_team_id])).all()
    winner_choices = [(-1,"Select a Team")] + [(t.id, "{} ({})".format(t.name, t.id)) for t in teams]
    form.winner_id.choices = winner_choices

    has_matches = Match.query.filter_by(tourney_id = tourney.id).count() > 0

    if form.validate_on_submit():
        tourney.date = form.date.data
        tourney.ruleset = form.ruleset.data
        tourney.scoring_method = form.scoring_method.data
        tourney.home_score = form.home_score.data
        tourney.away_score = form.away_score.data
        tourney.data = form.data.data
        tourney.active = form.active.data

        if tourney.winner_id > 0:
            tourney.winner_id = form.winner_id.data

        if form.owner_id.data != tourney_entityuser.user_id:
            new_owner = User.query.filter_by(id=form.owner_id.data).first()
            if new_owner != None:
                if (tourney_entityuser.user_id > 1):
                    tourney.revoke_permission(tourney_entityuser.user_id)
                tourney.grant_permission(new_owner.id)


        # TODO: add home_games and home_games as count of games where winner_id == home | away
        #       update home_score automatically on game save if winner_id != None and scoring_method exists



        db.session.merge(tourney)
        db.session.commit()

        flash('Tourney %s vs. %s has been saved' % (tourney.home_team_id, tourney.away_team_id), 'success')

    if request.method == 'GET':
        form.date.data = tourney.date
        form.ruleset.data = tourney.ruleset
        form.scoring_method.data = tourney.scoring_method
        form.winner_id.data = tourney.winner_id
        form.home_score.data = tourney.home_score
        form.away_score.data = tourney.away_score
        form.data.data = tourney.data
        form.owner_id.data = tourney_entityuser.user_id or 1
        form.active.data = tourney.active


    return render_template('admin/tourney/edit.html', tourney = tourney, has_matches = has_matches, form = form)

@mod_admin.route('/tourney/add/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourney_add():
    form = TourneyAddForm(request.form)
    user_choices = [(u.id, "{}, {} ({})".format(u.last_name, u.first_name, u.id)) for u in User.query.all()]
    team_choices = [(-1,"Select a Team")] + [(t.id, "{} ({})".format(t.name, t.id)) for t in Team.query.all()]
    form.owner_id.choices = user_choices
    form.home_team_id.choices = team_choices
    form.away_team_id.choices = team_choices
    form.date.data = date.today()

    if form.validate_on_submit():
        tourney = Tourney(
            date = form.date.data,
            home_team_id = form.home_team_id.data,
            away_team_id = form.away_team_id.data,
            scoring_method = form.scoring_method.data,
            ruleset = form.ruleset.data,
            data = form.data.data)

        db.session.add(tourney)
        db.session.commit()

        if form.owner_id.data != session["user_id"]:
            new_owner = User.query.filter_by(id=form.owner_id.data).first()
            if new_owner != None:
                tourney.grant_permission(new_owner.id)

        flash('Tourney %s vs. %s has been added' % (tourney.home_team_id, tourney.away_team_id), 'success')
        return redirect(url_for('admin.index'))

    return render_template('admin/tourney/add.html', form = form)


@mod_admin.route('/tourney/<int:tourney_id>/matches/', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def matches(tourney_id):
    tourney = Tourney.query.filter_by(id=tourney_id).first()
    if not tourney:
        return render_template('404.html'), 404

    return render_template('admin/match/index.html', tourney = tourney)

@mod_admin.route('/tourney/<int:tourney_id>/matches/add/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def match_add(tourney_id):
    tourney = Tourney.query.filter_by(id=tourney_id).first()
    if not tourney:
        return render_template('404.html'), 404

    tourney_entityuser = EntityUser.query.filter_by(entity = "Tourney", row_id = tourney.id).order_by(EntityUser.user_id.desc()).first()

    form = MatchAddForm(request.form)
    form.home_players.choices = [(p.id, "{}, {} ({})".format(p.last_name, p.first_name, p.player_id)) for p in tourney.home_team.players]
    form.away_players.choices = [(p.id, "{}, {} ({})".format(p.last_name, p.first_name, p.player_id)) for p in tourney.away_team.players]

    user_choices = [(u.id, "{}, {} ({})".format(u.last_name, u.first_name, u.id)) for u in User.query.all()]
    form.owner_id.choices = user_choices
    form.owner_id.data = tourney_entityuser.user_id or 1

    print "HOME PLAYERS"
    print form.home_players
    print form.home_players.data

    if form.validate_on_submit():

        print "passed validation"
        # TODO: this is passing validation even when players not selected
        # TODO: DB locked error on submit caused by invalid data or poor transation handling (or both)?


        ordinal = len(tourney.matches) + 1
        match = Match(
            tourney_id = tourney.id,
            ordinal = ordinal,
            data = form.data.data)
        db.session.add(match)
        db.session.commit()

        def assign_players(players, is_home_team):
            for player in players:
                matchplayer = MatchPlayer(
                    match_id = match.id,
                    player_id = player.id,
                    is_home_team = is_home_team)
                db.session.add(player)

        #Assign Home Player(s)
        assign_players(form.home_players.data, True)

        #Assign Away Player(s)
        assign_players(form.away_players.data, False)
    
        db.session.commit()

        if form.owner_id.data != session["user_id"]:
            new_owner = User.query.filter_by(id=form.owner_id.data).first()
            if new_owner != None:
                if (tourney_entityuser.user_id > 1):
                    tourney.revoke_permission(tourney_entityuser.user_id)
                match.grant_permission(new_owner.id)

        flash('Match %s vs. %s has been added' % (match.home_players[0].id, match.away_players[0].id), 'success')
        return redirect(url_for('admin.matches'))


    return render_template('admin/match/add.html', tourney = tourney, form = form)

@mod_admin.route('/match/<int:match_id>/', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def match(match_id):
    match = Match.query.filter_by(id=match_id).first()
    if not match:
        return render_template('404.html'), 404

    tourney_entityuser = EntityUser.query.filter_by(entity = "Tourney", row_id = tourney.id).order_by(EntityUser.user_id.desc()).first()
    # TODO: assign owner

    return render_template('admin/match/edit.html', match = match, tourney = match.tourney)

@mod_admin.route('/match/<int:match_id>/games', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def games(match_id):
    match = Match.query.filter_by(id=match_id).first()
    if not match:
        return render_template('404.html'), 404

    games = Game.query.filter_by(match_id = match_id).order_by(Game.ordinal).all()

    return render_template('admin/game/index.html', match = match, games = games)

@mod_admin.route('match/<int:match_id>/add', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def game_add(match_id):
    match = Match.query.filter_by(id=game.match_id).first()
    if not match:
        return render_template('404.html'), 404

    tourney = Tourney.query.filter_by(id=match.tourney_id).first()

    return render_template('admin/game/add.html', tourney = tourney, match = match)

@mod_admin.route('/game/<int:game_id>', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def game(game_id):
    game = Game.query.filter_by(id=game_id).first()
    if not game:
        flash("game id: {} not found".format(game_id))
        return render_template('404.html'), 404

    match = Match.query.filter_by(id=game.match_id).first()

    if (match != None):
        tourney = Tourney.query.filter_by(id=match.tourney_id).first()

    return render_template('admin/game/edit.html', tourney = tourney, match = match, game=game)

