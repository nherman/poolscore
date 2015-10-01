from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, send_from_directory
from poolscore import db
from poolscore import app

from poolscore.mod_auth.models import User
from poolscore.mod_user.forms import UserForm
from poolscore.mod_common.utils import SecurityUtil


mod_user = Blueprint('user', __name__, url_prefix = '/user')

@mod_user.route('/', methods = ['GET'])
@SecurityUtil.requires_auth()
def index():
    if SecurityUtil.is_admin():
        users = User.query.all()
        return render_template('user/index.html', users = users)
    else:
        id = session.get('user_id', None)
        return redirect(url_for('user.edit', id = id))


@mod_user.route('/add/', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
@SecurityUtil.requires_admin()
def add():
    form = UserForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter((User.email == form.email.data) |
            (User.username == form.username.data)).first()
        if user:
            flash('User email %s or username %s already exists' % (user.email, user.username), 'error')
            return redirect(url_for('user.add'))
        else:
            user = User(
                first_name = form.first_name.data, 
                last_name = form.last_name.data,
                email = form.email.data,
                username = form.username.data,
                password = form.password.data)
            user.active = True if form.active.data else False

            db.session.add(user)
            db.session.commit()

            user.grant_permission(user.id)

            flash('User %s %s has been added' % (user.first_name, user.last_name), 'success')
            return redirect(url_for('user.index'))
    return render_template("user/add.html", form = form)

@mod_user.route('/<int:id>', methods = ['GET', 'POST'])
@SecurityUtil.requires_auth()
def edit(id):
    user = User.secure_query().filter(User.id == id).first()
    if not user:
        return render_template('404.html'), 404
    form = UserForm(request.form)
    form.password.validators = []

    if form.validate_on_submit():
        existing_user = User.query.filter(User.id != id).filter(
            (User.email == form.email.data) | (User.username == form.username.data)).first()
        if existing_user:
            flash('User with username \'%s\' or email \'%s\' already exists' % existing_user.username, existing_user.email, 'error')
            return redirect(url_for('user.edit', id = id))
        else:
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            user.username = form.username.data
            user.active = True if form.active.data else False
            if form.password.data: 
                user.password = form.password.data

            db.session.merge(user)
            db.session.commit()

            flash('User %s has been saved' % user.first_name, 'success')
            return redirect(url_for('user.index'))
    if request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
        form.username.data = user.username
        form.active.data = True if user.active else False
    return render_template("user/edit.html", form = form, user = user)

