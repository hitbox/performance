from flask_login import AnonymousUserMixin
from flask_login import UserMixin
from sqlalchemy_utils import PasswordType

from performance.extensions import db
from performance.extensions import login_manager

from .mixin import AppContextMixin

class AnonymousUser(AnonymousUserMixin):

    @property
    def is_admin(self):
        return False


class User(
    AppContextMixin,
    UserMixin,
    db.Model,
):
    """
    A user of the web app with certain privileges.
    """

    id = db.Column(
        db.Integer,
        primary_key = True,
    )

    username = db.Column(
        db.String,
        unique = True,
        nullable = False,
        doc = 'Account username.',
        info = dict(
            human_field_name = 'Username',
        ),
    )

    email = db.Column(
        db.String,
        nullable = False,
        doc = 'Account email.',
        info = dict(
            human_field_name = 'Email',
        ),
    )

    password = db.Column(
        PasswordType(
            schemes = ['pbkdf2_sha512'],
        ),
    )

    is_admin = db.Column(
        db.Boolean,
        default = False,
        doc = "User account has full access to web interface.",
        info = dict(
            human_field_name = 'Admin?',
        ),
    )

    is_editor = db.Column(
        db.Boolean,
        default = False,
        doc = "User can edit reports and flights.",
        info = dict(
            human_field_name = 'Editor?',
        ),
    )

    is_active = db.Column(
        db.Boolean,
        default = True,
        doc = "User can login.",
        info = dict(
            human_field_name = 'Active?',
        ),
    )

    reset_password = db.Column(
        db.Boolean,
        default = True,
        doc = "User must change password.",
        info = dict(
            human_field_name = 'Reset Password?',
        ),
    )

    can_edit_schedule = db.Column(
        db.Boolean,
        default = False,
        doc = "User can edit the scheduled reports and flights.",
        info = dict(
            human_field_name = 'Edit Schedules?',
        ),
    )

    @db.validates('username', 'password')
    def validate_username(self, key, value):
        if value == '':
            raise ValueError(f'{key} cannot be an empty string')
        return value


login_manager.anonymous_user = AnonymousUser
