from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask.views import View

from ..extensions import db

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

    def dispatch_request(self):
        """
        """
        if callable(self.disabled) and self.disabled():
            abort(404)
        pagination = self.query.paginate()
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


class BaseEditView(View):
    methods = ['GET', 'POST']
    template = 'pluggable/form.html'

    def __init__(
        self,
        form_class,
        model=None,
        template=None,
        instance_name=None,
        form_render_kw=None,
        context_processor = None,
        disabled = None,
    ):
        """
        :param form_class:
            form class or callable.
        :param model:
            database model to lookup instance to edit.
        :param template:
            template to render for requests.
        :param instance_name:
            name for template context of instance being edited.
        :param form_render_kw:
            extra context for template.
        :param context_processor:
            an optional callable that return extra data to pass on to the template.
        :param disabled:
            an optional callable or bool, that decides if this view should
            throw 404.
        """
        if callable(form_class):
            form_class = form_class()
        self.form_class = form_class
        self.model = model or self.form_class.Meta.model
        self.template = template or self.template
        self.instance_name = instance_name
        self.form_render_kw = form_render_kw
        self.context_processor = context_processor
        self.disabled = disabled

    def get_context(self, **context):
        if callable(self.context_processor):
            extra = self.context_processor()
            if extra:
                context.update(extra)
        context.setdefault('form_render_kw', self.form_render_kw)
        context.setdefault('instance_name', self.instance_name)
        return context


class UpdateDeleteView(BaseEditView):

    def dispatch_request(self, **ident):
        if callable(self.disabled) and self.disabled():
            abort(404)
        instance = self.model.query.get_or_404(ident)
        form = self.form_class(obj=instance)
        form.submit.label.text = 'Update'
        if form.validate_on_submit():
            if form.delete.data:
                db.session.delete(instance)
            elif form.submit.data:
                form.populate_obj(instance)
            db.session.commit()
            if hasattr(form, 'backurl') and form.backurl.data:
                return redirect(form.backurl.data)
        context = self.get_context(
            form = form,
            instance = instance,
        )
        return render_template(self.template, **context)


class CreateView(BaseEditView):

    def dispatch_request(self, **kwargs):
        if callable(self.disabled) and self.disabled():
            abort(404)
        form = self.form_class()
        instance = None
        if form.validate_on_submit():
            instance = self.model()
            db.session.add(instance)
            form.populate_obj(instance)
            db.session.commit()
            if hasattr(form, 'backurl') and form.backurl.data:
                return redirect(form.backurl.data)
        elif request.method == 'GET':
            form.submit.label.text = 'Create'
            del form.delete
        context = self.get_context(
            form = form,
            instance = instance,
        )
        return render_template(self.template, **context)
