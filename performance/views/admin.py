from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from ..authorization import admin_check
from ..extensions import db
from ..forms import UserForm
from ..forms.user import available_username
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

@admin_bp.route('/users/new', methods=['GET', 'POST'])
def new_user():
    """
    Create new user.
    """
    form = UserForm()
    form.submit.label.text = 'Create user'

    if form.validate_on_submit():
        new_user = User()
        db.session.add(new_user)
        form.populate_obj(new_user)
        db.session.commit()
        flash('New user created', 'success')
        return redirect(url_for('.users'))

    context = dict(
        form = form,
    )
    return render_template('/admin/edit_user.html', **context)


@admin_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    """
    Edit user account.
    """
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    form.submit.label.text = 'Update user'

    # allow existing username
    del form.username
    #form.username.validators.remove(available_username)

    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash('User updated', 'success')
        return redirect(url_for('.users'))

    context = dict(
        form = form,
        user = user,
    )
    return render_template('/admin/edit_user.html', **context)
