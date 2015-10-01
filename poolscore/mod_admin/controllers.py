from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from poolscore import db
from poolscore import app

from poolscore.mod_play.models import Tourney, Match, Game
from poolscore.mod_common.utils import SecurityUtil



mod_admin = Blueprint('admin', __name__, url_prefix = '/admin')


@mod_admin.route('/', methods = ['GET'])
def index():
    return redirect(url_for('admin.tourneys'))

@mod_admin.route('/tourney', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourneys():
    tourneys = Tourney.query.order_by(Tourney.date_created).all()

    return render_template('admin/tourneys.html',
        tourneys = tourneys)

@mod_admin.route('/tourney/<int:id>', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourney():
    return render_template('play/tourney.html')

@mod_admin.route('/tourney/new', methods = ['GET'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def tourney_new():
    return render_template('admin/tourney_new.html')

