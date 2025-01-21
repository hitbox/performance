import click

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import redirect
from flask import url_for

from performance.extensions import db
from performance.forms import ContractForm
from performance.models import Contract
from performance.pluggable import FormListView

# TODO
# - Fix form and update other as necessary.

performance_contract_bp = Blueprint(
    'performance_contract',
    __name__,
    url_prefix = '/performance-contract',
)

@performance_contract_bp.before_request
def before_request():
    """
    Allow only if configured.
    """
    if not current_app.config.get('PERFORMANCE_CONTRACTS'):
        abort(404)

def response_for_delete(form):
    return redirect(url_for('admin.performance_contract.listform'))

view_func = FormListView.as_view(
    'listform',
    instance_getter = Contract.noapp_get_or_404,
    pagination_getter = Contract.noapp_pagination,
    form_getter = ContractForm,
    form_submitter = ContractForm.standard_submit,
    response_for_delete = response_for_delete,
    template = 'admin/performance-contracts.html',
    extra_context = dict(
        class_ = Contract,
    ),
)

performance_contract_bp.add_url_rule('/', view_func=view_func)

performance_contract_bp.add_url_rule('/<int:id>', view_func=view_func)

# CLI #

@performance_contract_bp.cli.command('list')
def list_contracts():
    """
    List performance contracts.
    """
    contracts = (
        Contract.query
        .order_by(Contract.date_range_start)
        .all()
    )
    if not contracts:
        print('No contracts')
    else:
        for contract in contracts:
            if contract.name:
                name = contract.name
            else:
                name = '<unnamed>'
            print(f'"{name}" runs from {contract.date_range_start} to {contract.date_range_end}')
            if not contract.tiers:
                print('    No tiers')
            else:
                for tier in contract.tiers:
                    print(f'    {tier.human_performance_range()}')

@performance_contract_bp.cli.command('add')
@click.option('--start', prompt=True, type=click.DateTime(['%Y-%m-%d']))
@click.option('--end', prompt=True, type=click.DateTime(['%Y-%m-%d']))
@click.option('--name')
def add_performance_contract(start, end, name):
    """
    Add performance contract.
    """
    contract = Contract(
        date_range_start = start,
        date_range_end = end,
        name = name,
    )
    db.session.add(contract)
    db.session.commit()
