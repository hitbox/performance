import calendar

from flask import Blueprint

from performance.authorization import edit_check
from performance.forms import AssumedBestForm
from performance.models import AssumedBest
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

view_func = EditView.as_view(
    'edit',
    template = 'assumed-best/edit.html',
    instance_getter = AssumedBest.noapp_get_or_404,
    form_getter = AssumedBestForm,
    form_submitter = AssumedBestForm.standard_submit,
)

assumed_best_bp.add_url_rule('/edit', view_func=view_func)

assumed_best_bp.add_url_rule('/edit/<int:id>', view_func=view_func)
