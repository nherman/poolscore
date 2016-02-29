import json
from datetime import date

from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, send_from_directory

from poolscore.mod_common.utils import SecurityUtil
from poolscore.mod_common.rulesets import Rulesets
from poolscore.mod_team.models import Team
from poolscore.mod_play.models import Tourney
from poolscore.mod_play.forms import NewTourneyForm


mod_play = Blueprint('play', __name__, url_prefix = '/play')

@mod_play.route('/', methods = ['GET'])
@SecurityUtil.requires_auth()
def index():
    tournies = Tourney.secure_all()
    if (len(tournies) == 0):
        return redirect(url_for('play.new'))
    if (len(tournies) == 1):
        return redirect(url_for('play.play', id = tournies[0].id))

    return render_template('play/index.html', tournies = tournies)

@mod_play.route('/new/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
def new():
    print "NEW"
    form = NewTourneyForm(request.form)
    team_choices = [(-1,"Select a Team")] + [(t.id, "{} ({})".format(t.name, t.id)) for t in Team._query().all()]
    form.home_team_id.choices = team_choices
    form.away_team_id.choices = team_choices
    form.date.data = date.today()
    form.start_time.data = date.today() #add 19 hours?

    ruleset = scoring_method = "APA8BALL"
    events = json.dumps(Rulesets[ruleset].tourney_events),

    if form.validate_on_submit():
        events['coin_toss'] = form.data.coin_toss
        events['player_choice'] = form.data.player_choice
        events['start_time'] = form.data.start_time

        tourney = Tourney(
            date = form.date.data,
            home_team_id = form.home_team_id.data,
            away_team_id = form.away_team_id.data,
            events = events,
            scoring_method = scoring_method,
            ruleset = ruleset)

        db.session.add(tourney)
        db.session.commit()

        flash('Tourney %s vs. %s has been added' % (tourney.home_team_id, tourney.away_team_id), 'success')
        return redirect(url_for('play.play', id = tourney.id))

    return render_template('play/new.html', form = form)

@mod_play.route('/<int:id>/', methods = ['GET'])
@SecurityUtil.requires_auth()
def play(id):
    return render_template('play/index.html')
