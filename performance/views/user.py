import click

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from ..extensions import db
from ..extensions import login_manager
from ..models import User

login_manager.login_message_category = 'warning'
login_manager.login_view = 'user.login'
login_manager.refresh_view = 'user.login'

user_bp = Blueprint('user', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page
    """
    from ..forms import LoginForm
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            db.func.lower(User.username) == db.func.lower(form.username.data)
        ).one_or_none()
        if user is None:
            flash('Invalid', 'error')
        elif user.password == form.password.data:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

@user_bp.route('/reset-password', methods=['GET', 'POST'])
@login_required
def reset_password():
    """
    Reset password form
    """
    from ..forms import ResetPasswordForm
    form = ResetPasswordForm()
    if form.validate_on_submit():
        form.populate_obj(current_user)
        current_user.reset_password = False
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('reset_password.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@user_bp.route('/profile')
@login_required
def profile():
    """
    User profile page
    """
    return render_template('profile.html')

@user_bp.cli.command('add', help='Add user.')
@click.option('--username', prompt=True,)
@click.option('--email', prompt=True,)
@click.password_option()
@click.option('--reset-password/--no-reset-password', default=True,
              help='Require user to reset password.')
@click.option('--is-editor', default=False, is_flag=True, help='Allow edit', prompt=True)
@click.option('--is-admin', default=False, is_flag=True, help='Allow admin', prompt=True)
@click.option('--can-edit-schedule', default=False, is_flag=True, help='User can edit schedules', prompt=True)
def add(
    username,
    email,
    password,
    reset_password,
    is_editor,
    is_admin,
    can_edit_schedule,
):
    """
    Add User
    """
    user = User(
        username = username,
        email = email,
        password = password,
        reset_password = reset_password,
        is_editor = is_editor,
        is_admin = is_admin,
        can_edit_schedule = can_edit_schedule,
    )
    db.session.add(user)
    db.session.commit()
