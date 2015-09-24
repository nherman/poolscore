from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, send_from_directory
from poolscore import db
from poolscore import app

from poolscore.mod_team.models import Team, Player
from poolscore.mod_team.forms import TeamForm
from poolscore.mod_common.utils import SecurityUtil



mod_team = Blueprint('team', __name__, url_prefix = '/team')

@mod_team.route('/', methods = ['GET'])
@SecurityUtil.requires_auth()
def index():
    teams = Team.query.all()

    return render_template('team/index.html', teams = teams)

@mod_team.route('/add/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
def add():
    form = TeamForm(request.form)
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

            db.session.merge(team)
            db.session.commit()

            flash('Team %s has been saved' % team.name, 'success')
            return redirect(url_for('team.index'))
    if request.method == 'GET':
        form.name.data = team.name
        form.location.data = team.location
        form.team_id.data = team.team_id

    return render_template("team/edit.html", form = form, team = team)
