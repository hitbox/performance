import sqlalchemy as sa

from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms import ValidationError
from wtforms.validators import EqualTo
from wtforms.validators import InputRequired

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


class UserModelForm(ModelForm):
    """
    Form for manipulating actual User objects.
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


def available_username(form, field):
    """
    Raise for already existing username.
    """
    user = User.query.filter(
        sa.func.lower(User.username) == sa.func.lower(field.data)
    ).one_or_none()
    if user:
        raise ValidationError('Username is taken')

class UserForm(FlaskForm):
    """
    Edit user account.
    """

    username = StringField(
        label = 'username',
        validators = [
            InputRequired(),
            available_username,
        ],
    )
    email = StringField(
        label = 'email',
        validators = [
            InputRequired(),
        ],
    )
    password = PasswordField(
        label = 'password',
        validators = [
            InputRequired(),
        ],
        render_kw = dict(
            autocomplete = 'off',
        )
    )
    password_confirm = PasswordField(
        label = 'confirm password',
        validators = [
            InputRequired(),
        ],
        render_kw = dict(
            autocomplete = 'off',
        )
    )

    is_active = BooleanField('Active?', default=True)
    reset_password = BooleanField('Reset password?', default=True)

    is_admin = BooleanField('Admin?', default=False)
    is_editor = BooleanField('Editor?', default=True)
    can_edit_schedule = BooleanField(
        'Edit schedules?',
        default = False,
        render_kw = dict(
            title = 'User may edit scheduled reports.'
        ),
    )

    submit = SubmitField()

    def validate_password_confirm(form, field):
        """
        Raise for password confirmation.
        """
        if field.data != form.password.data:
            raise ValidationError('Password confirmation does not match.')
