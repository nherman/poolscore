import json
from datetime import date, time, datetime

from flask import Blueprint, request, render_template, \
                  flash, session, redirect, url_for

from poolscore import db
from poolscore.mod_common.utils import SecurityUtil
from poolscore.mod_common.rulesets import Rulesets
from poolscore.mod_team.models import Team
from poolscore.mod_play.models import Tourney
from poolscore.mod_play.forms import NewTourneyForm


mod_play = Blueprint('play', __name__, url_prefix = '/play')

@mod_play.route('/', methods = ['GET'])
@SecurityUtil.requires_auth()
def index():
    tourneys = Tourney.secure_all()
    if (len(tourneys) == 0):
        return redirect(url_for('play.new'))
    if (len(tourneys) == 1):
        return redirect(url_for('play.play', id = tourneys[0].id))

    return render_template('play/index.html', tourneys = tourneys)

@mod_play.route('/new/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
def new():
    form = NewTourneyForm(request.form)
    team_choices = [(-1,"Select a Team")] + [(t.id, "{} ({})".format(t.name, t.id)) for t in Team._query().all()]
    form.home_team_id.choices = team_choices
    form.away_team_id.choices = team_choices

    ruleset = scoring_method = "APA8BALL"
    events = Rulesets[ruleset].tourney_events

    if form.validate_on_submit():
        #convert date to time string for JSON serialization
        if isinstance(form.start_time.data, datetime):
            try:
                start_time = form.start_time.data.time()
                events['start_time'] = start_time.isoformat()
            except TypeError():
                pass

        events['coin_toss'] = form.coin_toss.data
        events['player_choice'] = form.player_choice.data
        eventsJSON = json.dumps(events)

        tourney = Tourney(
            date = form.date.data,
            home_team_id = form.home_team_id.data,
            away_team_id = form.away_team_id.data,
            events = eventsJSON,
            scoring_method = scoring_method,
            ruleset = ruleset)

        db.session.add(tourney)
        db.session.commit()

        flash('Tourney %s vs. %s has been added' % (tourney.home_team_id, tourney.away_team_id), 'success')
        return redirect(url_for('play.play', id = tourney.id))

    if request.method == 'GET':
        timestamp = datetime.now()
        form.date.data = timestamp.today()
        form.start_time.data = timestamp

    return render_template('play/new.html', form = form)

@mod_play.route('/<int:id>/', methods = ['GET'])
@SecurityUtil.requires_auth()
def play(id):
    return render_template('play/index.html')
