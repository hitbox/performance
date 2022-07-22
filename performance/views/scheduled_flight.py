from flask import Blueprint
from flask import request

from ..authorization import edit_schedule_check
from ..forms import ScheduledFlightForm
from ..models import ScheduledFlight
from ..models import ScheduledReport
from ..pluggable import FormListView

scheduled_flight_bp = Blueprint('scheduled_flight', __name__)

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
    return dict(
        scheduled_report = scheduled_report,
    )

def form_getter(**kwargs):
    form = ScheduledFlightForm(**kwargs)
    if hasattr(form, 'backurl'):
        del form.backurl
    return form

view_func = FormListView.as_view(
    name = 'listform',
    template = 'scheduled-flight/list-form.html',
    instance_getter = instance_getter,
    pagination_getter = lambda: None,
    form_getter = form_getter,
    form_submitter = ScheduledFlightForm.standard_submit,
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
