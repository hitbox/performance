from flask import flash
from flask import url_for
from markupsafe import Markup

from performance.extensions import db
from performance.models import Performance

def flash_for_default_scheduled_flight_message():
    """
    Flash if the default scheduled flight type is not set.
    """
    settings = db.session.scalars(db.select(Performance)).one_or_none()
    if not settings.default_flight_type:
        url = url_for('admin.settings.edit')
        markup = Markup(
            'A default scheduled flight type is not set.'
            ' Admins can update it under'
            f' <a href="{url}">Settings</a>.'
        )
        flash(markup, 'warning')
