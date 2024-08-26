from flask import url_for
from flask_login import current_user
from markupsafe import Markup

from performance.extensions import db
from performance.models import Performance

def _default_flight_type():
    performance_metadata = db.session.scalars(db.select(Performance)).one()
    return performance_metadata.default_flight_type

def update_context_for_default_flight_type(context):

    default_flight_type = _default_flight_type()

    if default_flight_type is None and current_user.is_admin:
        url = url_for('admin.settings.edit')
        alert_for_default_flight_type = Markup(
            f'<p class="page">Set default flight type in <a href="{url}">Settings</a>.</p>'
        )
        context.setdefault('alert_for_default_flight_type', alert_for_default_flight_type)
