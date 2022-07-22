from flask import Blueprint

from performance.forms import EditUserForm
from performance.models import User
from performance.pluggable import FormListView

user_bp = Blueprint('user', __name__, url_prefix='/users')

admin_list_view = FormListView.as_view(
    'list',
    instance_getter = User.noapp_get_or_404,
    pagination_getter = User.noapp_pagination,
    form_getter = EditUserForm,
    form_submitter = EditUserForm.standard_submit,
    template = 'admin/users.html',
)

user_bp.add_url_rule('/', view_func=admin_list_view)

user_bp.add_url_rule('/<int:id>', view_func=admin_list_view)
