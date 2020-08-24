import click

from flask.cli import AppGroup

from ..extensions import db
from ..models import User

user_cli = AppGroup('user', help='Add a user account.')

@user_cli.command(help='Create user.')
@click.option('--username')
@click.option('--email')
@click.password_option()
@click.option('--reset-password/--no-reset-password', default=True,
              help='Require user to reset password.')
@click.option('--is-editor', default=False, is_flag=True, help='Allow edit')
@click.option('--is-admin', default=False, is_flag=True, help='Allow admin')
def add(username, email, password, reset_password, is_editor, is_admin):
    "Add User"
    user = User(username=username, email=email, password=password,
                reset_password=reset_password, is_editor=is_editor,
                is_admin=is_admin)
    db.session.add(user)
    db.session.commit()
