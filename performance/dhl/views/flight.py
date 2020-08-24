from flask import Blueprint
from flask import request
from flask import render_template
from flask import redirect

from ...authorization import edit_check
from ...extensions import db
from ...views.pluggable import CreateView
from ...views.pluggable import UpdateDeleteView

from ..forms import FlightForm

flight_bp = Blueprint('flight', __name__)

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
