import sqlalchemy as sa

from wtforms import BooleanField
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import ValidationError
from wtforms.validators import EqualTo
from wtforms.validators import InputRequired

from ..models import User

from .base import BaseFlaskForm

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


class EditUserForm(
    BaseFlaskForm,
):
    """
    Edit user account form for administration.
    """
    class Meta:
        # super class picks up Meta.model for new instances
        model = User
        # relabling
        presentation = True

    # requires unique in __init__
    username = StringField(
        label = 'Username',
        validators = [
            InputRequired(),
        ],
        render_kw = dict(
            placeholder = 'username',
        ),
    )

    email = StringField(
        label = 'Email',
        validators = [
            InputRequired(),
        ],
        render_kw = dict(
            placeholder = 'email',
        ),
    )

    password = PasswordField(
        label = 'Password',
        render_kw = dict(
            autocomplete = 'new-password',
            placeholder = 'password',
        )
    )

    password_confirm = PasswordField(
        label = 'Confirm',
        render_kw = dict(
            autocomplete = 'off',
            placeholder = 'password',
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not kwargs.get('obj', None):
            # new user so add username validator
            self.username.validators.append(validate_available_username)

    def validate_password_confirm(form, field):
        """
        Raise for password confirmation.
        """
        if (
            form.password.data
            and field.data != form.password.data
        ):
            raise ValidationError('Password confirmation does not match.')


    @classmethod
    def standard_submit(cls, form, instance=None):
        """
        Avoid overwriting password by removing the attribute so that
        populate_obj doesn't write an empty string.
        If the password is submitted, the form validates password confirmation.
        Here, if password is not given, we remove the password attribute.
        """
        if not form.password.data:
            del form.password
            del form.password_confirm
        return super().standard_submit(form, instance)
