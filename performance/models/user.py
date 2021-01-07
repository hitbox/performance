from flask_login import UserMixin
from sqlalchemy_utils import PasswordType

from ..extensions import db

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']))
    is_admin = db.Column(db.Boolean, default=False)
    is_editor = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    reset_password = db.Column(db.Boolean, default=True)
