from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, send_from_directory
from poolscore import db
from poolscore import app

from poolscore.mod_team.models import Team, Player
from poolscore.mod_team.forms import TeamForm, PlayerForm
from poolscore.mod_common.utils import SecurityUtil



mod_team = Blueprint('team', __name__, url_prefix = '/team')

@mod_team.route('/', methods = ['GET'])
@SecurityUtil.requires_auth()
def index():
    teams = Team.secure_all()

    return render_template('team/index.html', teams = teams)

@mod_team.route('/add/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
def add():
    form = TeamForm(request.form)
    form.players.choices = [(p.id, "{}, {} ({})".format(p.last_name, p.first_name, p.player_id)) for p in Player.secure_all()]

    if form.validate_on_submit():
        team = Team.query.filter(Team.name == form.name.data).first()
        if team:
            flash('Team name %s already exists' % (team.name), 'error')
            return redirect(url_for('team.add'))
        else:
            team = Team(
                name = form.name.data, 
                location = form.location.data,
                team_id = form.team_id.data)
            team.user_id = session["user_id"]

            #assign players
            for player_id in form.players.data:
                q = Player.query.filter_by(id=player_id)
                p = q.first()
                if p:
                    team.players.append(p)

            db.session.add(team)
            db.session.commit()
            flash('Team %s has been added' % (team.name), 'success')
            return redirect(url_for('team.index'))
    return render_template("team/add.html", form = form)

@mod_team.route('/<int:id>/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
def edit(id):
    team = Team.query.filter_by(id = id).first()

    if not team:
        return render_template('404.html'), 404

    form = TeamForm(request.form)
    form.players.choices = [(p.id, "{}, {} ({})".format(p.last_name, p.first_name, p.player_id)) for p in Player.secure_all()]
    if form.validate_on_submit():
        existing_team = Team.query.filter(Team.id != id).filter(Team.name == form.name.data).first()
        if existing_team:
            flash('A team with name \"%s\"" already exists at location \"%s\"' % existing_team.name, existing_team.location, 'error')
            return redirect(url_for('team.edit_team', id = id))
        else:

            team.name = form.name.data
            team.location = form.location.data
            team.team_id = form.team_id.data
            team.active = True

            #assign players
            while team.players:
                del team.players[0]
            for player_id in form.players.data:
                q = Player.query.filter_by(id=player_id)
                p = q.first()
                if p:
                    team.players.append(p)

            db.session.merge(team)
            db.session.commit()

            flash('Team %s has been saved' % team.name, 'success')
            return redirect(url_for('team.index'))
    if request.method == 'GET':
        form.name.data = team.name
        form.location.data = team.location
        form.team_id.data = team.team_id
        form.players.data = [p.id for p in team.players]


    return render_template("team/edit.html", form = form, team = team)

@mod_team.route('/player/', methods = ['GET'])
@SecurityUtil.requires_auth()
def players():
    players = Player.secure_all()

    return render_template('team/player/index.html', players = players)

@mod_team.route('/player/add/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
def add_player():
    form = PlayerForm(request.form)
    form.teams.choices = [(t.id, "{} ({})".format(t.name, t.team_id)) for t in Team.secure_all()]

    if form.validate_on_submit():
        player = Player.query.filter(Player.player_id == form.player_id.data).first()
        if player:
            flash('Player id %s already exists' % (player.player_id), 'error')
            return redirect(url_for('team.add_player'))
        else:
            player = Player(
                first_name = form.first_name.data, 
                last_name = form.last_name.data, 
                player_id = form.player_id.data,
                handicap = form.handicap.data)

            #assign teams
            for team_id in form.teams.data:
                q = Team.query.filter_by(id=team_id)
                t = q.first()
                if t:
                    player.teams.append(t)

            db.session.add(player)
            db.session.commit()
            flash('Player %s has been added' % (player.player_id), 'success')
            return redirect(url_for('team.players'))
    return render_template("team/player/add.html", form = form)

@mod_team.route('/player/<int:id>/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
def edit_player(id):
    player = Player.query.filter_by(id = id).first()

    if not player:
        return render_template('404.html'), 404

    form = PlayerForm(request.form)
    form.teams.choices = [(t.id, "{} ({})".format(t.name, t.team_id)) for t in Team.secure_all()]
    if form.validate_on_submit():
        existing_player = Player.query.filter(Player.id != id).filter(Player.player_id == form.player_id.data).first()
        if existing_player:
            flash('A player with id \"%s\"" already exists' % existing_player.player_id, 'error')
            return redirect(url_for('team.edit_player', id = id))
        else:
            player.first_name = form.first_name.data
            player.last_name = form.last_name.data
            player.handicap = form.handicap.data
            player.player_id = form.player_id.data
            player.active = True

            #assign teams
            while player.teams:
                del player.teams[0]
            for team_id in form.teams.data:
                q = Team.query.filter_by(id=team_id)
                t = q.first()
                if t:
                    player.teams.append(t)

            db.session.merge(player)
            db.session.commit()

            flash('Player %s has been saved' % player.player_id, 'success')
            return redirect(url_for('team.players'))
    if request.method == 'GET':
        form.first_name.data = player.first_name
        form.last_name.data = player.last_name
        form.handicap.data = player.handicap
        form.player_id.data = player.player_id
        form.teams.data = [t.id for t in player.teams]

    return render_template("team/player/edit.html", form = form, player = player)
