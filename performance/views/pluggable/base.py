from flask import render_template
from flask.views import View

class EditView(View):
    methods = ['GET', 'POST']
    template = 'pluggable/form.html'

    def __init__(
        self,
        instance_getter,
        form_class_getter,
        valid_submit_response,
        template = None,
    ):
        self.instance_getter = instance_getter
        self.form_class_getter = form_class_getter
        self.valid_submit_response = valid_submit_response
        self.template = template or self.template

    def dispatch_request(self, **instance_identity):
        instance = self.instance_getter(instance_identity)
        form = self.form_class_getter(instance)

        if form.validate_on_submit():
            return self.valid_submit_response(instance, form)

        context = dict(form=form, instance=instance)
        return render_template(self.template, **context)


class BaseEditView(View):
    methods = ['GET', 'POST']
    template = 'pluggable/form.html'

    def __init__(
        self,
        form_class,
        model = None,
        instance_query = None,
        template = None,
        instance_name = None,
        form_render_kw = None,
        context_processor = None,
        disabled = None,
    ):
        if callable(form_class):
            form_class = form_class()
        self.form_class = form_class
        if model is None:
            if (
                hasattr(self.form_class, 'Meta')
                and hasattr(self.form_class.Meta, 'model')
            ):
                model = self.form_class.Meta.model
        self.model = model
        self.instance_query = instance_query
        self.template = template or self.template
        self.instance_name = instance_name
        self.form_render_kw = form_render_kw
        self.context_processor = context_processor
        self.disabled = disabled

    def get_query(self):
        if self.instance_query is not None:
            return self.instance_query
        return self.model.query

    def get_instance(self, identity):
        query = self.get_query()
        return query(identity)

    def get_context(self, **context):
        if callable(self.context_processor):
            extra = self.context_processor()
            if extra:
                context.update(extra)
        context.setdefault('form_render_kw', self.form_render_kw)
        context.setdefault('instance_name', self.instance_name)
        return context
