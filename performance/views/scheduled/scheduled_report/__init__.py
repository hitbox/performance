from flask import redirect
from flask import request
from flask import url_for

from performance import settings
from performance.authorization import edit_schedule_check
from performance.extensions import db
from performance.forms import ScheduledFlightForm
from performance.forms import ScheduledReportForm
from performance.models import ScheduledReport
from performance.pluggable import FormListView

from ..utils import _default_flight_type
from ..utils import update_context_for_default_flight_type

from . import commandline # import for decorators
from .blueprint import scheduled_report_bp

@scheduled_report_bp.before_request
@edit_schedule_check
def before_request():
    """
    Enforce user can edit schedules and redirect to the only schedule if
    configured for only one schedule.
    """
    # decorator enforces access
    if (
        'id' not in request.view_args
        and settings.scheduled_reports_onlyone()
    ):
        # throw exception for not one
        # redirect to the flights
        stmt = db.select(ScheduledReport)
        scheduled_report = db.session.scalars(stmt).one()
        url = url_for(
            'scheduled.flight.listform',
            scheduled_report_id = scheduled_report.id,
        )
        return redirect(url)

def context_processor():
    """
    Add a scheduled flight form instance the template can show on the same page.
    """
    form = ScheduledFlightForm()
    # default FlightType for new scheduled flight
    form.flight_type.data = _default_flight_type()


    context = dict(
        new_scheduled_flight_form = form,
    )
    update_context_for_default_flight_type(context)
    return context

def response_for_delete(form):
    return redirect(url_for('scheduled.report.list'))

view_func = FormListView.as_view(
    'list',
    instance_getter = ScheduledReport.noapp_get_or_404,
    pagination_getter = ScheduledReport.noapp_pagination,
    form_getter = ScheduledReportForm,
    form_submitter = ScheduledReportForm.standard_submit,
    response_for_delete = response_for_delete,
    template = 'scheduled-report/list-form.html',
    context_processor = context_processor,
)

scheduled_report_bp.add_url_rule(
    '/',
    view_func = view_func,
)

scheduled_report_bp.add_url_rule(
    '/<int:id>',
    view_func = view_func,
)
