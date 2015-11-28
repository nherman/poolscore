from datetime import date

from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from sqlalchemy import exc

from poolscore import db

from poolscore.mod_common.models import EntityUser
from poolscore.mod_auth.models import User
from poolscore.mod_team.models import Team, Player
from poolscore.mod_play.models import Tourney, Match, Game, MatchPlayer
from poolscore.mod_common.utils import SecurityUtil
from poolscore.mod_admin.forms import TourneyAddForm, TourneyEditForm, \
                                      MatchAddForm, MatchEditForm, \
                                      GameForm



mod_admin = Blueprint('admin', __name__, url_prefix = '/admin')


@mod_admin.route('/', methods = ['GET'])
def index():
    return redirect(url_for('.tourneys'))

@mod_admin.route('/tourney/', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourneys():
    hide_deleted = request.args.get("deleted") == None
    tourneys = Tourney._query(hide_deleted).all()

    return render_template('admin/tourney/index.html',
        tourneys = tourneys, hide_deleted = hide_deleted)


@mod_admin.route('/tourney/add/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourney_add():
    form = TourneyAddForm(request.form)
    user_choices = [(u.id, "{}, {} ({})".format(u.last_name, u.first_name, u.id)) for u in User._query().all()]
    team_choices = [(-1,"Select a Team")] + [(t.id, "{} ({})".format(t.name, t.id)) for t in Team._query().all()]
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

@mod_admin.route('/tourney/<int:tourney_id>/delete', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourney_delete(tourney_id):
    tourney = Tourney.query.filter_by(id=tourney_id).first()
    if not tourney:
        return render_template('404.html'), 404
    
    with db.session.no_autoflush:
        try:
            for match in tourney.matches:
                for game in match.games:
                    game.delete()
                match.delete()

            tourney.delete()
            db.session.commit()

            flash('Tourney deleted', 'success')
            return redirect(url_for('.tourneys'))
        except exc.SQLAlchemyError as ex:
            db.session.rollback()

            flash('Error: %s' % (ex), 'error')
            return redirect(url_for('.tourney', tourney_id = tourney.id))

@mod_admin.route('/tourney/<int:tourney_id>/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourney(tourney_id):
    tourney = Tourney.query.filter_by(id=tourney_id).first()
    if not tourney:
        return render_template('404.html'), 404

    tourney_entityuser = EntityUser.query.filter_by(entity = "Tourney", row_id = tourney.id).order_by(EntityUser.user_id.desc()).first()
    form = TourneyEditForm(request.form)

    user_choices = [(u.id, "{}, {} ({})".format(u.last_name, u.first_name, u.id)) for u in User._query().all()]
    form.owner_id.choices = user_choices

    teams = Team._query().filter(Team.id.in_([tourney.home_team_id, tourney.away_team_id])).all()
    winner_choices = [(-1,"Select a Team")] + [(t.id, "{} ({})".format(t.name, t.id)) for t in teams]
    form.winner_id.choices = winner_choices

    hide_deleted = request.args.get("deleted") == None
    if (hide_deleted):
        matches = tourney.matches
    else:
        matches = tourney.all_matches.all()


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


        # TODO: add home_games and away_games as count of games where winner_id == home | away
        #       update home_score automatically on game save if winner_id != None and scoring_method exists
        #       allow tourney delete - remember to cascade properly and delete matches, matchplayers, and games



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


    return render_template('admin/tourney/edit.html', tourney = tourney, matches = matches, form = form, hide_deleted = hide_deleted)

@mod_admin.route('/tourney/<int:tourney_id>/match/add/', methods = ['GET', 'POST'])
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

    user_choices = [(u.id, "{}, {} ({})".format(u.last_name, u.first_name, u.id)) for u in User._query().all()]
    form.owner_id.choices = user_choices
    form.owner_id.data = tourney_entityuser.user_id or 1

    if form.validate_on_submit():

        match = Match(
            tourney_id = tourney.id,
            data = form.data.data)
        db.session.add(match)
        db.session.commit()

        def assign_players(player_ids, is_home_team):
            for pid in player_ids:
                matchplayer = MatchPlayer(
                    match_id = match.id,
                    player_id = pid,
                    is_home_team = is_home_team)
                db.session.add(matchplayer)

        #Assign Home Player(s)
        assign_players(form.home_players.data, True)

        #Assign Away Player(s)
        assign_players(form.away_players.data, False)
    
        db.session.commit()

        if form.owner_id.data != session["user_id"]:
            new_owner = User.query.filter_by(id=form.owner_id.data).first()
            if new_owner != None:
                if (tourney_entityuser.user_id > 1):
                    match.revoke_permission(tourney_entityuser.user_id)
                match.grant_permission(new_owner.id)

        flash('Match %s vs. %s has been added' % (match.home_players[0].first_name, match.away_players[0].first_name), 'success')
        return redirect(url_for('admin.match', match_id = match.id))


    return render_template('admin/match/add.html', tourney = tourney, form = form)

@mod_admin.route('/match/<int:match_id>/delete', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def match_delete(match_id):
    match = Match.query.filter_by(id=match_id).first()
    if not match:
        return render_template('404.html'), 404

    ordinal = match.ordinal

    with db.session.no_autoflush:
        try:
            for game in match.games:
                game.delete()

            match.delete()
            db.session.commit()

            flash('Match %s deleted' % (ordinal), 'success')
            return redirect(url_for('.tourney', tourney_id = match.tourney_id))
        except exc.SQLAlchemyError as ex:
            db.session.rollback()

            flash('Error: %s' % (ex), 'error')
            return redirect(url_for('.match', match_id = match.id))

@mod_admin.route('/match/<int:match_id>/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def match(match_id):
    match = Match.query.filter_by(id=match_id).first()
    if not match:
        return render_template('404.html'), 404

    match_entityuser = EntityUser.query.filter_by(entity = "Match", row_id = match.id).order_by(EntityUser.user_id.desc()).first()
    form = MatchEditForm(request.form)

    user_choices = [(u.id, "{}, {} ({})".format(u.last_name, u.first_name, u.id)) for u in User._query().all()]
    form.owner_id.choices = user_choices

    winner_choices = [(-1,"Select a Player")] + [(p.id, "{} {} ({})".format(p.first_name, p.last_name, p.id)) for p in match._get_players()]
    form.winner_id.choices = winner_choices

    hide_deleted = request.args.get("deleted") == None
    if (hide_deleted):
        games = match.games
    else:
        games = match.all_games.all()

    if form.validate_on_submit():
        match.home_score = form.home_score.data
        match.away_score = form.away_score.data
        match.data = form.data.data
        match.active = form.active.data

        if match.winner_id > 0:
            match.winner_id = form.winner_id.data

        if form.owner_id.data != match_entityuser.user_id:
            new_owner = User.query.filter_by(id=form.owner_id.data).first()
            if new_owner != None:
                match.grant_permission(new_owner.id)
                if (match_entityuser.user_id > 1):
                    match.revoke_permission(match_entityuser.user_id)


        db.session.merge(match)
        db.session.commit()

        flash('Match %s vs. %s has been saved' % (match.home_players[0].first_name, match.away_players[0].first_name), 'success')

    if request.method == 'GET':
        form.winner_id.data = match.winner_id
        form.home_score.data = match.home_score
        form.away_score.data = match.away_score
        form.data.data = match.data
        form.owner_id.data = match_entityuser.user_id or 1
        form.active.data = match.active


    return render_template('admin/match/edit.html', match = match, tourney = match.tourney, games = games, hide_deleted = hide_deleted, form = form)

@mod_admin.route('/match/<int:match_id>/game/add/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def game_add(match_id):
    match = Match.query.filter_by(id=match_id).first()
    if not match:
        return render_template('404.html'), 404

    match_entityuser = EntityUser.query.filter_by(entity = "Match", row_id = match.id).order_by(EntityUser.user_id.desc()).first()

    form = GameForm(request.form)

    user_choices = [(u.id, "{}, {} ({})".format(u.last_name, u.first_name, u.id)) for u in User._query().all()]
    form.owner_id.choices = user_choices
    form.owner_id.data = match_entityuser.user_id or 1

    winner_choices = [(-1,"Select a Player")] + [(p.id, "{} {} ({})".format(p.first_name, p.last_name, p.id)) for p in match._get_players()]
    form.winner_id.choices = winner_choices

    if form.validate_on_submit():

        game = Game(
            match_id = match.id,
            data = form.data.data)
        db.session.add(game)
        db.session.commit()

        if form.owner_id.data != session["user_id"]:
            new_owner = User.query.filter_by(id=form.owner_id.data).first()
            if new_owner != None:
                if (match_entityuser.user_id > 1):
                    game.revoke_permission(match_entityuser.user_id)
                game.grant_permission(new_owner.id)


        flash('Game %s' % (game.ordinal), 'success')
        return redirect(url_for('admin.game', game_id = game.id))


    return render_template('admin/game/add.html', tourney = match.tourney, match = match, form = form)

@mod_admin.route('/game/<int:game_id>/', methods = ['GET', 'POST', 'DELETE'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def game(game_id):
    game = Game.query.filter_by(id=game_id).first()
    if not game:
        return render_template('404.html'), 404

    game_entityuser = EntityUser.query.filter_by(entity = "Game", row_id = game.id).order_by(EntityUser.user_id.desc()).first()
    form = GameForm(request.form)

    user_choices = [(u.id, "{}, {} ({})".format(u.last_name, u.first_name, u.id)) for u in User._query().all()]
    form.owner_id.choices = user_choices

    winner_choices = [(-1,"Select a Player")] + [(p.id, "{} {} ({})".format(p.first_name, p.last_name, p.id)) for p in game.match._get_players()]
    form.winner_id.choices = winner_choices

    if form.validate_on_submit():
        game.data = form.data.data
        game.active = form.active.data

        if form.winner_id.data > 0:
            game.winner_id = form.winner_id.data

        if form.owner_id.data != game_entityuser.user_id:
            new_owner = User.query.filter_by(id=form.owner_id.data).first()
            if new_owner != None:
                game.grant_permission(new_owner.id)
                if (game_entityuser.user_id > 1):
                    game.revoke_permission(game_entityuser.user_id)


        db.session.merge(game)
        db.session.commit()

        flash('Game %s' % (game.ordinal), 'success')

    if request.method == 'GET':
        form.winner_id.data = game.winner_id
        form.data.data = game.data
        form.owner_id.data = game_entityuser.user_id or 1
        form.active.data = game.active


    return render_template('admin/game/edit.html', tourney = game.match.tourney, match = game.match, game = game, form = form)

@mod_admin.route('/game/<int:game_id>/delete', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def game_delete(game_id):
    game = Game.query.filter_by(id=game_id).first()
    if not game:
        return render_template('404.html'), 404

    ordinal = game.ordinal

    with db.session.no_autoflush:
        try:
            game.delete()
            db.session.commit()

            flash('Game %s deleted' % (ordinal), 'success')
            return redirect(url_for('.match', match_id = game.match_id))
        except exc.SQLAlchemyError as ex:
            db.session.rollback()

            flash('Error: %s' % (ex), 'error')
            return redirect(url_for('.game', game_id = game.id))


