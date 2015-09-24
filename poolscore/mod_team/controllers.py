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
def add_user():
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
            team.user_id = session.user_id

            db.session.add(team)
            db.session.commit()
            flash('Team %s has been added' % (team.name), 'success')
            return redirect(url_for('team.index'))
    return render_template("team/add.html", form = form)
