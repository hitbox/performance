from flask import render_template
from flask import request
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
        response_for_delete = None,
        context_processor = None,
        extra_context = None,
    ):
        """
        :param instance_getter:
            callable taking an identity dict that returns an instance for that identity.
        :param pagination_getter:
            no-arguments callable returning pagination.
        :param form_getter:
            callable taking an instance, possibly None, returning a form.
        :param form_submitter:
            callable taking optional instance and possibly returning a response object.
        :param template:
            used as the first argument to render_template
        :param context_processor:
            if given, a callable to return extra data for the context given to
            the template.
        :param extra_context:
            Always passed extra context for the template.
        """
        self.instance_getter = instance_getter
        self.pagination_getter = pagination_getter
        self.form_getter = form_getter
        self.form_submitter = form_submitter
        self.template = template
        self.response_for_delete = response_for_delete
        self.context_processor = context_processor
        self.extra_context = extra_context

    def dispatch_request(self, **instance_identity):
        """
        Main function to dispatch requests for the table and forms.
        """
        if instance_identity:
            instance = self.instance_getter(instance_identity)
        else:
            instance = None

        form = self.form_getter(obj=instance)

        if request.method == 'POST':
            result_for_submit = self.form_submitter(form, instance)
            if form.is_delete and self.response_for_delete:
                return self.response_for_delete(form)
            elif result_for_submit:
                return result_for_submit

        context = dict(
            instance = instance,
            form = form,
        )
        if self.extra_context:
            context.update(self.extra_context)

        if callable(self.pagination_getter):
            context['pagination'] = self.pagination_getter()

        if callable(self.context_processor):
            extra = self.context_processor()
            if extra:
                context.update(extra)
        return render_template(self.template, **context)
