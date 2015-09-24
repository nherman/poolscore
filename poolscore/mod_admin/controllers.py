from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, send_from_directory
from poolscore import db
from poolscore import app

from poolscore.mod_play.models import Tourney, Match, Game
from poolscore.mod_common.utils import SecurityUtil



mod_admin = Blueprint('admin', __name__, url_prefix = '/admin')

@mod_admin.route('/', methods = ['GET'])
@SecurityUtil.requires_auth()
def index():
    return render_template('admin/index.html')

@mod_admin.route('/tourney', methods = ['GET'])
@SecurityUtil.requires_auth()
def tourneys():
    tourneys = Tourney.query.order_by(Tourney.date_created).all()

    return render_template('admin/tourneys.html',
        tourneys = tourneys)

@mod_admin.route('/tourney/<int:id>', methods = ['GET'])
@SecurityUtil.requires_auth()
def tourney():
    return render_template('play/tourney.html')

@mod_admin.route('/tourney/new', methods = ['GET'])
@SecurityUtil.requires_auth()
def tourney_new():
    return render_template('admin/tourney_new.html')

