from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import request
from flask import url_for

from .. import settings
from ..authorization import edit_schedule_check
from ..forms import ScheduledFlightForm
from ..forms import ScheduledReportForm
from ..models import ScheduledReport
from ..pluggable import FormListView

scheduled_report_bp = Blueprint('scheduled_report', __name__)

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
        scheduled_report = ScheduledReport.query.one()
        return redirect(url_for('scheduled_flight.listform', scheduled_report_id=scheduled_report.id))

def context_processor():
    """
    Add a scheduled flight form instance the template can show on the same page.
    """
    form = ScheduledFlightForm()
    if 'id' in request.view_args:
        form.scheduled_report_id.data = request.view_args['id']
    return dict(new_scheduled_flight_form=form)

def response_for_delete(form):
    return redirect(url_for('scheduled_report.list'))

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
