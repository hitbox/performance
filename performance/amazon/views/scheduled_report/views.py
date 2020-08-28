from operator import attrgetter

from flask import Blueprint
from flask import render_template
from flask import url_for
from markupsafe import Markup

from performance.authorization import edit_check
from performance.models import FlightType
from performance.views.pluggable import ListView

from performance.amazon.models import ScheduledReport

scheduled_report_bp = Blueprint(
    'scheduled_report',
    __name__,
    template_folder = 'templates',
)

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

@scheduled_report_bp.route('/<int:id>')
@edit_check
def edit(id):
    """
    Edit ScheduledReport.
    """
    scheduled_report = ScheduledReport.query.get_or_404(id)
    # [(flight_type, flight of that type), ...]
    grouped = [
        (flight_type,
         sorted(
             (flight for flight in scheduled_report.scheduled_flights
              if flight.flight_type == flight_type),
             key = attrgetter('flight_number')))
        for flight_type in FlightType.query.order_by(FlightType.report_order)
    ]
    context = dict(
        scheduled_report = scheduled_report,
        grouped = grouped,
    )
    return render_template('scheduled_report/edit.html', **context)
