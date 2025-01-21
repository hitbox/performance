import calendar

from flask import Blueprint
from flask import redirect
from flask import request
from flask import url_for

from performance.authorization import edit_check
from performance.extensions import db
from performance.forms import AssumedBestForm
from performance.models import AssumedBest
from performance.pluggable import CreateView
from performance.pluggable.simpler import EditView

assumed_best_bp = Blueprint('assumed_best', __name__)

@edit_check
@assumed_best_bp.before_request
def before_request():
    """
    Enforce user is_edit.
    """

@assumed_best_bp.context_processor
def context_processor():
    return dict(calendar=calendar)

@assumed_best_bp.route('/for/<int:year>/<int:month>')
def for_(year, month):
    """
    Convenience for templates to avoid lots of control flow.
    """
    assumed_best = db.session.get(AssumedBest, {'year': year, 'month': month})
    if not assumed_best:
        url = url_for('.create', year=year, month=month, **request.args)
    else:
        url = url_for('.edit', year=year, month=month, **request.args)
    return redirect(url)

def form_class():
    return AssumedBestForm

assumed_best_bp.add_url_rule(
    '/create/<int:year>/<int:month>',
    view_func = CreateView.as_view(
        'create',
        form_class,
        template = 'assumed-best/edit.html',
    )
)

assumed_best_bp.add_url_rule(
    '/edit/<int:year>/<int:month>',
    view_func = EditView.as_view(
        'edit',
        template = 'assumed-best/edit.html',
        instance_getter = AssumedBest.noapp_get_or_404,
        form_getter = AssumedBestForm,
        form_submitter = AssumedBestForm.standard_submit,
    ),
)
