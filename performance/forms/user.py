import wtforms.validators

from flask_wtf import FlaskForm

from performance.extensions import db
from performance.forms import HiddenIntegerField
from performance.models import User

from .base import BaseForm

def validate_available_username(form, field):
    """
    Raise for already existing username.
    """
    query = db.select(
        User
    ).where(
        db.func.lower(User.username) == db.func.lower(field.data),
    )
    if db.session.execute(query).one_or_none():
        raise wtforms.ValidationError('Username is taken')

class LoginForm(BaseForm, FlaskForm):
    """
    Login form.
    """
    username = wtforms.StringField('Username')
    password = wtforms.PasswordField('Password')
    submit = wtforms.SubmitField('Login')


class ResetPasswordForm(BaseForm, FlaskForm):
    """
    Reset password form
    """
    password = wtforms.PasswordField('Password')
    confirm = wtforms.PasswordField('Confirm', validators=[wtforms.validators.EqualTo('password')])
    submit = wtforms.SubmitField('Reset')


class EditUserForm(
    BaseForm,
    FlaskForm,
):
    """
    Edit user account form for administration.
    """
    class Meta:
        # super class picks up Meta.model for new instances
        model = User
        # relabling
        presentation = True

    id = HiddenIntegerField(
        validators = [
            wtforms.validators.Optional(),
        ],
    )

    # requires unique in __init__
    username = wtforms.StringField(
        label = 'Username',
        validators = [
            wtforms.validators.InputRequired(),
        ],
        render_kw = dict(
            placeholder = 'username',
        ),
    )

    email = wtforms.StringField(
        label = 'Email',
        validators = [
            wtforms.validators.InputRequired(),
        ],
        render_kw = dict(
            placeholder = 'email',
        ),
    )

    password = wtforms.PasswordField(
        label = 'Password',
        render_kw = dict(
            autocomplete = 'new-password',
            placeholder = 'password',
        )
    )

    password_confirm = wtforms.PasswordField(
        label = 'Confirm',
        render_kw = dict(
            autocomplete = 'off',
            placeholder = 'password',
        )
    )

    is_active = wtforms.BooleanField(
        'Active?',
        default = True,
        render_kw = dict(
            title = 'Account can be used to login.',
        ),
    )

    reset_password = wtforms.BooleanField(
        'Reset password?',
        default = True,
        render_kw = dict(
            title = 'User must change their password after logging in.',
        ),
    )

    is_admin = wtforms.BooleanField(
        'Admin?',
        default = False,
        render_kw = dict(
            title = 'User has complete access to web interface.',
        ),
    )

    is_editor = wtforms.BooleanField(
        'Editor?',
        default = True,
        render_kw = dict(
            title = User.is_editor.doc,
        ),
    )

    can_edit_schedule = wtforms.BooleanField(
        'Edit schedules?',
        default = False,
        render_kw = dict(
            title = 'User may edit scheduled reports.'
        ),
    )

    submit = wtforms.SubmitField()

    def validate_username(form, field):
        if not form.id.data:
            # validate username for new user
            validate_available_username(form, field)

    def validate_password_confirm(form, field):
        """
        Raise for password confirmation.
        """
        if (
            form.password.data
            and field.data != form.password.data
        ):
            raise wtforms.ValidationError('Password confirmation does not match.')


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
