from flask import Blueprint
from flask import request

from performance.authorization import edit_schedule_check
from performance.extensions import db
from performance.forms import ScheduledFlightForm
from performance.models import ScheduledFlight
from performance.models import ScheduledReport
from performance.pluggable import FormListView

from .utils import update_context_for_default_flight_type

scheduled_flight_bp = Blueprint('flight', __name__)

@edit_schedule_check
@scheduled_flight_bp.before_request
def before_request():
    """
    Enforce user can edit scheduled flight.
    """

def instance_getter(*ignore_args, **ignore_kwargs):
    # FormListView.dispatch_request will always see an instance identity passed
    # to it because of scheduled_report_id. So we have to figure out if this is
    # a new or edit operation.
    if 'id' in request.view_args:
        # edit scheduled flight instance
        return ScheduledFlight.query.get(request.view_args['id'])

def context_processor():
    scheduled_report_id = request.view_args['scheduled_report_id']
    scheduled_report = ScheduledReport.query.get_or_404(scheduled_report_id)
    more_context = dict(
        scheduled_report = scheduled_report,
    )
    update_context_for_default_flight_type(more_context)
    return more_context

def form_getter(**kwargs):
    form = ScheduledFlightForm(**kwargs)

    # update scheduled report id
    form.scheduled_report_id.data = request.view_args['scheduled_report_id']
    return form

def form_submitter(form, instance):
    response = ScheduledFlightForm.standard_submit(form, instance)
    return response

view_func = FormListView.as_view(
    name = 'listform',
    template = 'scheduled-flight/list-form.html',
    instance_getter = instance_getter,
    pagination_getter = lambda: None,
    form_getter = form_getter,
    form_submitter = form_submitter,
    context_processor = context_processor,
)

scheduled_flight_bp.add_url_rule(
    '/edit/<int:scheduled_report_id>/<int:id>',
    view_func = view_func
)

scheduled_flight_bp.add_url_rule(
    '/create/<int:scheduled_report_id>',
    view_func = view_func
)
