from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for

from performance.extensions import db
from performance.glue import FormGetter
from performance.glue import FormSubmitter
from performance.models import Contract
from performance.models import PerformanceTier
from performance.views.pluggable import FormListView

from . import performance_contract

performance_tier_bp = Blueprint(
    'performance_tier',
    __name__,
    url_prefix = '/performance-tier',
)

def tier_form_class(*args, **kwargs):
    from performance.forms import PerformanceTierForm
    return PerformanceTierForm(*args, **kwargs)

def get_pagination():
    return PerformanceTier.query.order_by(PerformanceTier.order).paginate()

@performance_tier_bp.route(
    '/contract/<int:contract_id>/new-tier',
    methods=['GET', 'POST'])
def new(contract_id):
    """
    Create new performance tier for a contract.
    """
    contract = Contract.query.get_or_404(contract_id)
    form = tier_form_class()
    form.submit.label.text = 'Create'
    del form.delete

    if form.validate_on_submit():
        performance_tier = PerformanceTier()
        db.session.add(performance_tier)
        form.populate_obj(performance_tier)
        contract.tiers.append(performance_tier)
        db.session.commit()
        url = url_for('admin.performance_contract.list', id=contract.id)
        return redirect(url)

    context = dict(
        contract = contract,
        form = form,
        pagination = performance_contract.get_pagination(),
    )
    return render_template('admin/performance_tiers.html', **context)

@performance_tier_bp.route('/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """
    :param id: PerformanceTier id.
    """
    performance_tier = PerformanceTier.query.get_or_404(id)
    form = tier_form_class(obj=performance_tier)
    form.submit.label.text = 'Update'

    if form.validate_on_submit():
        contract_id = performance_tier.contract.id
        if form.delete.data:
            db.session.delete(performance_tier)
        else:
            form.populate_obj(performance_tier)
        db.session.commit()
        url = url_for('admin.performance_contract.list', id=contract_id)
        return redirect(url)

    context = dict(
        form = form,
        instance = performance_tier,
        pagination = performance_contract.get_pagination(),
    )
    return render_template('admin/performance_tiers.html', **context)

def trash():
    view = FormListView.as_view(
        'list',
        instance_getter = lambda id: PerformanceTierForm.query.get_or_404(id),
        pagination_getter = get_pagination,
        form_getter = FormGetter(tier_form_class),
        form_submitter = FormSubmitter(PerformanceTier),
        template = 'admin/performance_tiers.html',
    )

    performance_tier_bp.add_url_rule('/', view_func=view)
    performance_tier_bp.add_url_rule('/<int:id>', view_func=view)
