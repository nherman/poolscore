from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, send_from_directory
from poolscore import db
from poolscore import app

from poolscore.mod_common.utils import SecurityUtil



mod_home = Blueprint('home', __name__, url_prefix = '/home')

@mod_home.route('/', methods = ['GET'])
@SecurityUtil.requires_auth()
def index():
    return render_template('home/index.html')