from flask_login import UserMixin
from sqlalchemy_utils import PasswordType

from ..extensions import db

from .mixin import AppContextMixin

class User(
    AppContextMixin,
    UserMixin,
    db.Model,
):
    """
    A user of the web app with certain privileges.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']))
    is_admin = db.Column(
        db.Boolean,
        default=False,
        doc="User can administrate.")
    is_editor = db.Column(
        db.Boolean,
        default=False,
        doc="User can edit reports and flights.")
    is_active = db.Column(
        db.Boolean,
        default=True,
        doc="User can login.")
    reset_password = db.Column(
        db.Boolean,
        default=True,
        doc="User must change password.")
    can_edit_schedule = db.Column(
        db.Boolean,
        default=False,
        doc="User can edit the scheduled reports and flights.")

    @db.validates('username', 'password')
    def validate_username(self, key, value):
        if value == '':
            raise ValueError(f'{key} cannot be an empty string')
        return value
