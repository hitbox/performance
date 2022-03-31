from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for

from ..authorization import admin_check
from ..models import User

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@admin_check
def before_request():
    """
    Using decorators to enforce user is logged in as admin for all routes.
    """

@admin_bp.route('/')
def index():
    return redirect(url_for('admin.users'))

@admin_bp.route('/users')
def users():
    """
    List users for admin.
    """
    users = User.query.paginate()
    context = dict(
        User = User,
        users = users,
    )
    return render_template('admin/users.html', **context)
