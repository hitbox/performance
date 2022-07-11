from flask import render_template
from flask.views import View

class FormListView(View):
    """
    A listing with a form to add, edit and delete instances.
    """
    methods = ['GET', 'POST']

    def __init__(
        self,
        instance_getter,
        pagination_getter,
        form_getter,
        form_submitter,
        template,
        context_processor = None,
    ):
        self.instance_getter = instance_getter
        self.pagination_getter = pagination_getter
        self.form_getter = form_getter
        self.form_submitter = form_submitter
        self.template = template
        self.context_processor = context_processor

    def dispatch_request(self, **instance_identity):
        if instance_identity:
            instance = self.instance_getter(instance_identity)
        else:
            instance = None

        form = self.form_getter(instance)

        result_for_submit = self.form_submitter(instance, form)
        if result_for_submit:
            return result_for_submit

        context = dict(
            pagination = self.pagination_getter(),
            instance = instance,
            form = form,
        )
        if callable(self.context_processor):
            extra = self.context_processor()
            context.update(extra)
        return render_template(self.template, **context)
