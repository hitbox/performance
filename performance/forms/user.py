from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import EqualTo

from ..models import User

from .base import BaseFlaskForm
from .base import ModelForm

class LoginForm(BaseFlaskForm):
    """
    Login form.
    """
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Login')


class UserForm(ModelForm):
    """
    Form form manipulating actual User objects.
    """
    class Meta:
        model = User


class ResetPasswordForm(BaseFlaskForm):
    """
    Reset password form
    """
    password = PasswordField('password')
    confirm = PasswordField('reset', validators=[EqualTo('password')])
    submit = SubmitField('Reset')
