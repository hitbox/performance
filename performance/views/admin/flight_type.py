from flask import Blueprint

from performance.models import FlightType
from performance.forms import FlightTypeForm
from performance.pluggable import FormListView

flight_type_bp = Blueprint('flight_type', __name__, url_prefix='/flight-type')

formlist_view = FormListView.as_view(
    'list',
    instance_getter = FlightType.noapp_get_or_404,
    pagination_getter = FlightType.noapp_pagination,
    form_getter = FlightTypeForm,
    form_submitter = FlightTypeForm.standard_submit,
    template = 'admin/flight-types.html',
)

flight_type_bp.add_url_rule('/', view_func=formlist_view)
flight_type_bp.add_url_rule('/<int:id>', view_func=formlist_view)
