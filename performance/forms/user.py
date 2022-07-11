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

def validate_available_username(form, field):
    """
    Raise for already existing username.
    """
    user = User.query.filter(
        sa.func.lower(User.username) == sa.func.lower(field.data)
    ).one_or_none()
    if user:
        raise ValidationError('Username is taken')

class LoginForm(BaseFlaskForm):
    """
    Login form.
    """
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Login')


class ResetPasswordForm(BaseFlaskForm):
    """
    Reset password form
    """
    password = PasswordField('Password')
    confirm = PasswordField('Confirm', validators=[EqualTo('password')])
    submit = SubmitField('Reset')


class UserFormMixin:
    """
    Common fields for new and edit user forms.
    """
    class Meta:
        # any fields the subclasses define that should sort before the ones here.
        fields_order = [
            'username',
            'email',
            'password',
            'password_confirm',
        ]


    email = StringField(
        label = 'Email',
        validators = [
            InputRequired(),
        ],
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
        if (
            form.password.data
            and field.data != form.password.data
        ):
            raise ValidationError('Password confirmation does not match.')


class NewUserForm(UserFormMixin, BaseFlaskForm):
    """
    New user account.
    """
    username = StringField(
        label = 'Username',
        validators = [
            InputRequired(),
            validate_available_username,
        ],
    )

    password = PasswordField(
        label = 'Password',
        validators = [
            InputRequired(),
        ],
        render_kw = dict(
            autocomplete = 'off',
        )
    )

    password_confirm = PasswordField(
        label = 'Confirm password',
        validators = [
            InputRequired(),
        ],
        render_kw = dict(
            autocomplete = 'off',
        )
    )


class EditUserForm(UserFormMixin, BaseFlaskForm):
    """
    Edit user form.
    """
    # does not require unique
    username = StringField(label='Username', validators = [InputRequired()])

    password = PasswordField(
        label = 'Password',
        render_kw = dict(
            autocomplete = 'off',
        )
    )

    password_confirm = PasswordField(
        label = 'Confirm password',
        render_kw = dict(
            autocomplete = 'off',
        )
    )

