from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask.views import View

class SimpleListView(View):

    def __init__(
        self,
        items_getter,
        template = 'pluggable/list.html',
        extra_context = None,
    ):
        self.items_getter = items_getter
        self.template = template
        self.extra_context = extra_context

    def dispatch_request(self, **eat_kwargs):
        context = dict(
            items = self.items_getter(),
        )
        if callable(self.extra_context):
            context.update(self.extra_context())
        return render_template(self.template, **context)
