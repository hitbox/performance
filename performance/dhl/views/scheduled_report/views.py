from flask import Blueprint
from flask import url_for
from markupsafe import Markup

from performance.authorization import edit_check
from performance.views.pluggable import ListView
from performance.views.pluggable import ModelView

from performance.dhl.models import ScheduledReport

scheduled_report_bp = Blueprint('scheduled_report', __name__)

def render_scheduled_report(scheduled_report):
    href = url_for('scheduled_report.edit', id=scheduled_report.id)
    text = scheduled_report.name
    return Markup(f'<a href="{href}">{text}</a>')

scheduled_report_bp.add_url_rule(
    '/',
    view_func = edit_check(
        ListView.as_view(
            'index',
            ScheduledReport,
            item_renderer = render_scheduled_report,
            page_title = 'Scheduled Reports',
        )))

scheduled_report_bp.add_url_rule(
    '/<int:id>',
    view_func = edit_check(
        ModelView.as_view(
            'edit',
            ScheduledReport,
            'schedule/view.html',
            instance_name = 'scheduled_report',
        )))
