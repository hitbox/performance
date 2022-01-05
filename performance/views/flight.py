from flask import Blueprint

from performance.authorization import edit_check
from performance.views.pluggable import CreateView
from performance.views.pluggable import UpdateDeleteView

flight_bp = Blueprint('flight', __name__, template_folder='../templates')

def flight_form_class():
    # NOTE: temp workaround for wtforms-alchemy's aggressiveness
    from ..forms import FlightForm
    return FlightForm


flight_bp.add_url_rule(
    '/create/<int:report_id>',
    view_func = edit_check(
        CreateView.as_view(
            'create',
            flight_form_class,
            template = 'flight/form.html',
        )))

flight_bp.add_url_rule(
    '/edit/<int:id>',
    view_func = edit_check(
        UpdateDeleteView.as_view(
            'edit',
            flight_form_class,
            template = 'flight/form.html',
        )))
