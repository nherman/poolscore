from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, send_from_directory
from poolscore import db
from poolscore import app

from poolscore.mod_common.utils import SecurityUtil
from poolscore.mod_play.models import Tourney



mod_home = Blueprint('home', __name__)

@mod_home.route('/', methods = ['GET'])
@SecurityUtil.requires_auth()
def index():
    tourneys = Tourney.secure_all()
    return render_template('home/index.html', tourneys = tourneys)