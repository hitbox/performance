from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField

from ..models import User

from .base import BaseFlaskForm
from .base import ModelForm

class LoginForm(BaseFlaskForm):
    """
    Login form.
    """
    username = StringField('username')
    password = PasswordField('password')
    submit = SubmitField('login')


class UserForm(ModelForm):
    """
    Form form manipulating actual User objects.
    """
    class Meta:
        model = User
