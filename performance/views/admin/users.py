from flask import Blueprint

from performance.forms import EditUserForm
from performance.forms import NewUserForm
from performance.glue import FormGetter
from performance.glue import FormSubmitter
from performance.models import User
from performance.views.pluggable import FormListView

user_bp = Blueprint('user', __name__, url_prefix='/users')

class UserFormSubmitter(FormSubmitter):
    """
    A FormSubmitter specific to the user forms.
    """

    def on_updated(self, instance, form):
        """
        Avoid overwriting password by removing the attribute so that
        populate_obj doesn't write an empty string.
        If the password is submitted, the form validates password confirmation.
        """
        if not form.password.data:
            del form.password


admin_list_view = FormListView.as_view(
    'list',
    instance_getter = lambda id: User.query.get_or_404(id),
    pagination_getter = lambda: User.query.order_by(User.username).paginate(),
    form_getter = FormGetter(EditUserForm, NewUserForm),
    form_submitter = UserFormSubmitter(User),
    template = 'admin/users.html',
)
user_bp.add_url_rule('/', view_func=admin_list_view)
user_bp.add_url_rule('/<int:id>', view_func=admin_list_view)
