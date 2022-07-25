from flask import Blueprint
from flask import abort
from flask import current_app
from flask import redirect
from flask import request
from flask import url_for

from performance.forms import PerformanceTierForm
from performance.models import Contract
from performance.models import PerformanceTier
from performance.pluggable import FormListView

performance_tier_bp = Blueprint(
    'performance_tier',
    __name__,
    url_prefix = '/performance-tier',
)

@performance_tier_bp.before_request
def before_request():
    """
    Allow only if configured.
    """
    if not current_app.config.get('PERFORMANCE_CONTRACTS'):
        abort(404)

def instance_getter(identity):
    """
    Function to get proper request arg since we're dependent on contract_id.
    """
    if 'id' in identity:
        return PerformanceTier.query.get_or_404(identity['id'])

def context_processor():
    contract_id = request.view_args['contract_id']
    contract = Contract.query.get_or_404(contract_id)
    return dict(
        contract = contract,
    )

def response_for_delete(form):
    return redirect(
        url_for(
            'admin.performance_tier.listform',
            contract_id = request.view_args['contract_id'],
        )
    )

view_func = FormListView.as_view(
    'listform',
    instance_getter = instance_getter,
    pagination_getter = None, #PerformanceTier.noapp_pagination,
    form_getter = PerformanceTierForm,
    form_submitter = PerformanceTierForm.standard_submit,
    response_for_delete = response_for_delete,
    template = 'admin/performance-tiers.html',
    context_processor = context_processor,
)

performance_tier_bp.add_url_rule('/<int:contract_id>', view_func=view_func)

performance_tier_bp.add_url_rule('/<int:contract_id>/<int:id>', view_func=view_func)
