import datetime

import click

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from ..authorization import admin_check
from ..authorization import basic_check
from ..authorization import edit_check
from ..extensions import db
from ..forms import UserForm
from ..forms.user import available_username
from ..models import Contract
from ..models import PerformanceTier
from ..models import User
from ..views.pluggable import CreateView
from ..views.pluggable import ListView
from ..views.pluggable import UpdateDeleteView

admin_bp = Blueprint('admin', __name__)

def contract_form_class():
    from ..forms import ContractForm
    return ContractForm

def tier_form_class():
    from ..forms import PerformanceTierForm
    return PerformanceTierForm

def new_tier_form():
    """
    Return form for new PerformanceTier objects.
    """
    form_class = tier_form_class()
    form = form_class()
    del form.delete
    form.submit.label.text = 'Add tier'
    return form

def new_contract_form():
    """
    """
    form_class = contract_form_class()
    form = form_class()
    del form.delete
    form.submit.label.text = 'Add new contract'
    return form

@admin_bp.before_request
@admin_check
def before_request():
    """
    Using decorators to enforce user is logged in as admin for all routes.
    """

@admin_bp.route('/')
def index():
    """
    Admin related index page.
    """
    return render_template('admin/index.html')

@admin_bp.route('/users')
def users():
    """
    List users for admin.
    """
    users = User.query.paginate()
    context = dict(
        User = User,
        users = users,
    )
    return render_template('admin/users.html', **context)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
def new_user():
    """
    Create new user.
    """
    form = UserForm()
    form.submit.label.text = 'Create user'

    if form.validate_on_submit():
        new_user = User()
        db.session.add(new_user)
        form.populate_obj(new_user)
        db.session.commit()
        flash('New user created', 'success')
        return redirect(url_for('.users'))

    context = dict(
        form = form,
    )
    return render_template('/admin/edit_user.html', **context)


@admin_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    """
    Edit user account.
    """
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    form.submit.label.text = 'Update user'

    # allow existing username
    del form.username
    #form.username.validators.remove(available_username)

    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash('User updated', 'success')
        return redirect(url_for('.users'))

    context = dict(
        form = form,
        user = user,
    )
    return render_template('/admin/edit_user.html', **context)

@admin_bp.route('/contracts/<int:contract_id>/tiers/new', methods=['POST'])
def contract_add_tier(contract_id):
    """
    Add performance tier to a contract.
    """
    contract = Contract.query.get_or_404(contract_id)
    PerformanceTierForm = tier_form_class()
    form = PerformanceTierForm()

    if form.validate_on_submit():
        tier = PerformanceTier()
        form.populate_obj(tier)
        contract.tiers.append(tier)
        db.session.commit()
        return redirect(url_for('admin.edit_contract', id=contract.id))

    # How to do form errors?


# list contracts
admin_bp.add_url_rule(
    '/contracts/list',
    view_func = basic_check(
        ListView.as_view(
            'list_contracts',
            Contract,
            template = 'contract/list.html',
            context_processor = lambda: dict(
                new_contract_form = new_contract_form(),
            ),
        )))

# create contract
admin_bp.add_url_rule(
    '/contracts/create',
    view_func = edit_check(
        CreateView.as_view(
            'create_contract',
            contract_form_class,
            template = 'contract/contract-form.html',
            context_processor = lambda: dict(
                new_tier_form = new_tier_form(),
            ),
        )))

# edit contract
admin_bp.add_url_rule(
    '/contracts/edit/<int:id>',
    view_func = edit_check(
        UpdateDeleteView.as_view(
            'edit_contract',
            contract_form_class,
            template = 'contract/contract-form.html',
            context_processor = lambda: dict(
                new_tier_form = new_tier_form(),
            ),
        )))

# create (performance) tier
admin_bp.add_url_rule(
    '/tier/create',
    view_func = edit_check(
        CreateView.as_view(
            'create_tier',
            tier_form_class,
        )))

# edit (performance) tier
admin_bp.add_url_rule(
    '/tier/edit/<int:id>',
    view_func = edit_check(
        UpdateDeleteView.as_view(
            'edit_tier',
            tier_form_class,
            context_processor = lambda: dict(
                page_title = 'Edit Contract',
            ),
        )))

# CLI #

@admin_bp.cli.command('list')
def list_contracts():
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

@admin_bp.cli.command('add')
@click.option('--start', prompt=True, type=click.DateTime(['%Y-%m-%d']))
@click.option('--end', prompt=True, type=click.DateTime(['%Y-%m-%d']))
@click.option('--name')
def add_contract(start, end, name):
    """
    """
    contract = Contract(
        date_range_start = start,
        date_range_end = end,
        name = name,
    )
    db.session.add(contract)
    db.session.commit()
