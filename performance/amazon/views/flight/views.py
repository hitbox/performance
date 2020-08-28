from flask import Blueprint

from performance.authorization import edit_check
from performance.views.pluggable import CreateView
from performance.views.pluggable import UpdateDeleteView

from performance.amazon.forms import FlightForm

flight_bp = Blueprint('flight', __name__, template_folder='templates')

flight_bp.add_url_rule(
    '/create/<int:report_id>',
    view_func = edit_check(
        CreateView.as_view(
            'create',
            FlightForm,
            template = 'flight/form.html',
        )))

flight_bp.add_url_rule(
    '/edit/<int:id>',
    view_func = edit_check(
        UpdateDeleteView.as_view(
            'edit',
            FlightForm,
            template = 'flight/form.html',
        )))
