from flask import Blueprint

from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from ..extensions import db
from ..extensions import login_manager
from ..forms import LoginForm
from ..models import User

login_manager.login_message_category = 'warning'
login_manager.login_view \
    = login_manager.refresh_view \
    = 'user.login'

user_bp = Blueprint('user', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
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

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@user_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
