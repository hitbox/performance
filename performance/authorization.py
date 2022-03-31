from functools import wraps

from flask import abort
from flask import current_app
from flask import flash
from flask import redirect
from flask import url_for
from flask_login import current_user
from flask_login import login_required

def development_only(func):
    """
    Decorate view to abort if not in development environment.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if (current_app.env != 'development'):
            abort(403)
        return func(*args, **kwargs)
    return decorated_view

def redirect_password_reset(func):
    """
    Check and redirect if user is required to change their password.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if (hasattr(current_user, 'reset_password')
                and current_user.reset_password):
            flash('Password reset required', 'info')
            return redirect(url_for('user.reset_password'))
        return func(*args, **kwargs)
    return decorated_view

def edit_required(func):
    """
    View requires logged in user to have editing privileges.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if (not hasattr(current_user, 'is_editor')
                or not current_user.is_editor):
            abort(403)
        return func(*args, **kwargs)
    return decorated_view

def edit_schedule_required(func):
    """
    View requires logged in user to be admin or to have edit schedule privileges.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        is_admin = getattr(current_user, 'is_admin', False)
        can_edit_schedule = getattr(current_user, 'can_edit_schedule', False)
        if (not (is_admin or can_edit_schedule)):
            abort(403)
        return func(*args, **kwargs)
    return decorated_view

def admin_required(func):
    """
    View requires logged in user to have admin privileges.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if (not hasattr(current_user, 'is_admin')
                or not current_user.is_admin):
            abort(403)
        return func(*args, **kwargs)
    return decorated_view

def basic_check(view):
    """
    Logged in and password doesn't require resetting.
    """
    return redirect_password_reset(login_required(view))

def edit_check(view):
    """
    User is logged in, doesn't require password change and is an editor.
    """
    return edit_required(basic_check(view))

def admin_check(view):
    """
    Admin user is logged in and doesn't require password change.
    """
    return admin_required(basic_check(view))

def edit_schedule_check(view):
    """
    User is admin or can_edit_schedule flag is True.
    """
    return edit_schedule_required(basic_check(view))
