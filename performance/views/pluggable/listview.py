from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.views import View

class ListView(View):
    methods = ['GET']
    template = 'pluggable/list.html'

    def __init__(
        self,
        model,
        template = None,
        item_renderer = None,
        page_title = None,
        query = None,
        context_processor = None,
        disabled = None,
    ):
        """
        :param model:
            database model to list.
        :param template:
            template to render for requests.
        :param item_renderer:
            callable that the template can use to render items.
        :param page_title:
            something the template can render for a title.
        :param query:
            object with `.paginate` attribute; a callable that is called and
            passed to the template as `pagination`.
        :param context_processor:
            an optional callable that return extra data to pass on to the template.
        :param disabled:
            an optional callable or bool, that decides if this view should
            throw 404.
        """
        self.model = model
        self.template = template or self.template
        self.item_renderer = item_renderer or str
        self.page_title = page_title
        self.context_processor = context_processor
        if query is None:
            query = self.model.query
        self.query = query
        self.disabled = disabled

    def dispatch_request(self, **eat_kwargs):
        if callable(self.disabled) and self.disabled():
            abort(404)
        if callable(self.query):
            query = self.query()
        else:
            query = self.query
        pagination = query.paginate()
        context = dict(
            pagination = pagination,
            item_renderer = self.item_renderer,
            page_title = self.page_title,
        )
        if callable(self.context_processor):
            extra = self.context_processor()
            if extra:
                context.update(extra)
        return render_template(self.template, **context)
