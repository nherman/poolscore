from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from poolscore import db
from poolscore import app

from poolscore.mod_auth.models import User
from poolscore.mod_team.models import Team, Player
from poolscore.mod_play.models import Tourney, Match, Game
from poolscore.mod_common.utils import SecurityUtil
from poolscore.mod_admin.forms import TourneyAddForm, TourneyEditForm



mod_admin = Blueprint('admin', __name__, url_prefix = '/admin')


@mod_admin.route('/', methods = ['GET'])
def index():
    return redirect(url_for('.tourneys'))

@mod_admin.route('/tourney/', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourneys():
    tourneys = Tourney.query.order_by(Tourney.date_created).all()

    # # get team names
    # for tourney_obj in tourney_objs:
    #     tourneys.append((tourney_obj,
    #         Team.query.filter_by(id=tourney.home_team_id).first()))


    return render_template('admin/tourney/index.html',
        tourneys = tourneys)

@mod_admin.route('/tourney/<int:tourney_id>/', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourney(tourney_id):
    tourney = Tourney.query.filter_by(id=tourney_id).first()
    if not tourney:
        return render_template('404.html'), 404

    return render_template('admin/tourney/edit.html', tourney = tourney)

@mod_admin.route('/tourney/add/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourney_add():
    print "tourney_add"
    form = TourneyAddForm(request.form)
    user_choices = [(u.id, "{}, {} ({})".format(u.last_name, u.first_name, u.id)) for u in User.query.all()]
    team_choices = [(-1,"Select a Team")] + [(t.id, "{} ({})".format(t.name, t.id)) for t in Team.query.all()]
    form.owner_id.choices = user_choices
    form.home_team_id.choices = team_choices
    form.away_team_id.choices = team_choices

    if form.validate_on_submit():
        print "passed validator"
        tourney = Tourney(
            date = form.date.data,
            home_team_id = form.home_team_id.data,
            away_team_id = form.away_team_id.data,
            scoring_method = form.scoring_method.data,
            ruleset = form.ruleset.data)

        if (form.data.data != None):
            tourney.data = form.data.data

        db.session.add(tourney)
        db.session.commit()

        if form.owner_id.data != session["user_id"]:
            owner = User.query.filter_by(id=form.owner_id.data).first()
            if owner != None:
                tourney.grant_permission(owner.id)

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

    matches = Match.query.filter_by(tourney_id = tourney_id).order_by(Match.ordinal).all()

    return render_template('admin/match/index.html', tourney = tourney, matches = matches)

@mod_admin.route('/tourney/<int:tourney_id>/add/', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def match_add(tourney_id):
    tourney = Tourney.query.filter_by(id=tourney_id).first()
    if not tourney:
        return render_template('404.html'), 404

    return render_template('admin/match/add.html', tourney = tourney)

@mod_admin.route('/match/<int:match_id>/', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def match(match_id):
    match = Match.query.filter_by(id=match_id).first()
    if not match:
        return render_template('404.html'), 404

    tourney = Tourney.query.filter_by(id=match.tourney_id).first()

    return render_template('admin/match/edit.html', tourney = tourney, match = match)

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

