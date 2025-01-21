from flask import Blueprint

from performance.forms import DelayForm
from performance.models import Delay
from performance.pluggable import FormListView

delay_bp = Blueprint('delay', __name__, url_prefix='/delay')

admin_list_view = FormListView.as_view(
    'list',
    instance_getter = Delay.noapp_get_or_404,
    pagination_getter = Delay.noapp_pagination,
    form_getter = DelayForm,
    form_submitter = DelayForm.standard_submit,
    template = 'admin/delay-codes.html',
    extra_context = dict(
        class_ = Delay,
    ),
)

delay_bp.add_url_rule('/', view_func=admin_list_view)

delay_bp.add_url_rule('/<int:id>', view_func=admin_list_view)
