from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, send_from_directory
from poolscore import db
from poolscore import app

from poolscore.mod_team.models import Team, Player
from poolscore.mod_common.utils import SecurityUtil



mod_team = Blueprint('team', __name__, url_prefix = '/team')

@mod_team.route('/', methods = ['GET'])
@SecurityUtil.requires_auth()
def index():
    return render_template('team/index.html')