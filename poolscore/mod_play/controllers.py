from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, send_from_directory
from poolscore import db
from poolscore import app

from poolscore.mod_play.models import Tourney, Match, Game
from poolscore.mod_common.utils import SecurityUtil



mod_team = Blueprint('play', __name__, url_prefix = '/play')

@mod_team.route('/', methods = ['GET'])
@SecurityUtil.requires_auth()
def index():
    return render_template('play/index.html')