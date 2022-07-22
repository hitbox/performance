from flask import render_template
from flask import request
from flask.views import View

class BaseFormView(View):
    methods = ['GET', 'POST']

    def form_getter_arguments(self, view_args):
        return dict()

    def form_submitter_arguments(self, form):
        return (form, )

    def get_context(self, form):
        return dict(form=form)

    def dispatch_request(self, **view_args):
        """
        """
        form_args = self.form_getter_arguments(view_args)
        form = self.form_getter(**form_args)

        if request.method == 'POST':
            submit_args = self.form_submitter_arguments(form)
            response_for_submit = self.form_submitter(*submit_args)
            if response_for_submit:
                return response_for_submit

        context = self.get_context(form)
        if callable(self.context_func):
            extra = self.context_func()
            if extra:
                context.update(extra)
        return render_template(self.template, **context)


class CreateView(BaseFormView):

    def __init__(
        self,
        *, # keyword-only arguments
        template,
        form_getter,
        form_submitter,
        context = None,
    ):
        """
        """
        self.template = template
        self.form_getter = form_getter
        self.form_submitter = form_submitter
        self.context_func = context


class EditView(BaseFormView):

    def __init__(
        self,
        *, # keyword-only arguments
        # adds instance_getter
        template,
        instance_getter,
        form_getter,
        form_submitter,
        context = None,
    ):
        """
        """
        # the dance involving `.as_view` for pluggable views seems to prevent
        # using `super().__init__` here.
        self.template = template
        self.instance_getter = instance_getter
        self.form_getter = form_getter
        self.form_submitter = form_submitter
        self.context_func = context

    def form_getter_arguments(self, view_args):
        # save/gather instance for later
        self._instance = self.instance_getter(view_args)
        return dict(obj=self._instance)

    def form_submitter_arguments(self, form):
        # use save instance for submitter
        # save/gather form for later
        self._form = form
        return (self._form, self._instance)

    def get_context(self, form):
        context = super().get_context(form)
        context['instance'] = self._instance
        return context
