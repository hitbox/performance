import sqlalchemy as sa

from flask import Blueprint
from flask import render_template
from flask.views import MethodView

from performance.extensions import db
from performance.forms import EditUserForm
from performance.forms.user import validate_available_username
from performance.models import User
from performance.pluggable import FormListView

class UserView(MethodView):
    # This exists here, so as to try out some ideas while fixing the user admin
    # page.

    def __init__(self, **kwargs):
        self.context_processor = kwargs.pop('context_processor', None)
        self.form_getter = kwargs.pop('form_getter', None)
        self.form_submitter = kwargs.pop('form_submitter', None)
        self.instance_getter = kwargs.pop('instance_getter', None)
        self.pagination_getter = kwargs.pop('pagination_getter', None)
        self.response_for_delete = kwargs.pop('response_for_delete', None)
        self.template = kwargs.pop('template', None)
        self.extra_context = kwargs.pop('extra_context', None)
        if any(kwargs):
            raise ValueError(
                f'Unexpected keyword arguments {kwargs}')

    def get_form_and_instance(self, instance_identity):
        if instance_identity:
            user = db.session.get(User, instance_identity)
        else:
            user = None

        form = EditUserForm(obj=user)
        return (form, user)

    def get_pagination(self):
        pagination = User.noapp_pagination()
        return pagination

    def render_template_from_context(self, form, instance):
        context = dict(
            form = form,
            pagination = self.get_pagination(),
            instance = instance,
        )
        if self.extra_context:
            context.update(self.extra_context)
        return render_template(self.template, **context)

    def get(self, **instance_identity):
        form, user = self.get_form_and_instance(instance_identity)
        return self.render_template_from_context(form, user)

    def post(self, **instance_identity):
        form, user = self.get_form_and_instance(instance_identity)

        result_for_submit = self.form_submitter(form, user)
        if form.is_delete and self.response_for_delete:
            return self.response_for_delete(form)
        elif result_for_submit:
            return result_for_submit

        return self.render_template_from_context(form, user)


user_bp = Blueprint('user', __name__, url_prefix='/users')

user_view = UserView.as_view(
    'list',
    instance_getter = User.noapp_get_or_404,
    pagination_getter = User.noapp_pagination,
    form_getter = EditUserForm,
    form_submitter = EditUserForm.standard_submit,
    template = 'admin/users.html',
    extra_context = dict(
        User = User,
    ),
)

user_bp.add_url_rule('/', view_func=user_view)

user_bp.add_url_rule('/<int:id>', view_func=user_view)
