import click

from flask import Blueprint

from performance.extensions import db
from performance.glue import FormGetter
from performance.glue import FormSubmitter
from performance.models import Contract
from performance.models import PerformanceTier
from performance.views.pluggable import FormListView

performance_contract_bp = Blueprint(
    'performance_contract',
    __name__,
    url_prefix = '/performance-contract',
)

def contract_form_class(*args, **kwargs):
    from performance.forms import ContractForm
    form = ContractForm(*args, **kwargs)
    form.submit.label.text = 'Update'
    return form

def new_contract_form_class(*args, **kwargs):
    from performance.forms import ContractForm
    form = ContractForm(*args, **kwargs)
    form.submit.label.text = 'Create'
    del form.delete
    return form

def get_pagination():
    return Contract.query.order_by(Contract.date_range_start).paginate()

view = FormListView.as_view(
    'list',
    instance_getter = lambda id: Contract.query.get_or_404(id),
    pagination_getter = get_pagination,
    form_getter = FormGetter(contract_form_class, new_contract_form_class),
    form_submitter = FormSubmitter(Contract, object_name='Performance Contract'),
    template = 'admin/performance_contracts.html',
)

performance_contract_bp.add_url_rule('/', view_func=view)
performance_contract_bp.add_url_rule('/<int:id>', view_func=view)

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
