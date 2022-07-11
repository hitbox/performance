from flask import Blueprint

from performance.glue import FormGetter
from performance.glue import FormSubmitter
from performance.models import Delay
from performance.views.pluggable import FormListView

delay_bp = Blueprint('delay', __name__, url_prefix='/delay')

# NOTE: delete removed for both forms because unsure what that should look like.

def delay_form_class(*args, **kwargs):
    from performance.forms import DelayForm
    form = DelayForm(*args, **kwargs)
    form.submit.label.text = 'Update'
    del form.delete
    return form

def new_delay_form_class(*args, **kwargs):
    from performance.forms import DelayForm
    form = DelayForm(*args, **kwargs)
    form.submit.label.text = 'Create'
    del form.delete
    return form

admin_list_view = FormListView.as_view(
    'list',
    instance_getter = lambda id: Delay.query.get_or_404(id),
    pagination_getter = lambda: Delay.query.order_by(Delay.code).paginate(),
    form_getter = FormGetter(delay_form_class, new_delay_form_class),
    form_submitter = FormSubmitter(Delay),
    template = 'admin/delay_codes.html',
)
delay_bp.add_url_rule('/', view_func=admin_list_view)
delay_bp.add_url_rule('/<int:id>', view_func=admin_list_view)
