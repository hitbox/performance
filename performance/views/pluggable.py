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
    ):
        self.model = model
        self.template = template or self.template
        self.item_renderer = item_renderer or str
        self.page_title = page_title
        if query is None:
            query = self.model.query
        self.query = query

    def dispatch_request(self):
        pagination = self.query.paginate()
        context = dict(
            pagination = pagination,
            item_renderer = self.item_renderer,
            page_title = self.page_title,
        )
        return render_template(self.template, **context)


class GroupbyView(View):
    methods = ['GET']
    template = 'pluggable/groupby.html'

    def __init__(self, query, attribute, title=None, template=None):
        """
        :param query: callable returning items to list.
        :param attribute: attribute of items to group by.
        :param title: page title.
        :param template: html template.
        """
        self.query = query
        self.attribute = attribute
        self.title = title
        self.template = template or self.template

    def dispatch_request(self):
        context = dict(
            items = self.query(),
            attribute = self.attribute,
            title = self.title,
        )
        return render_template(self.template, **context)


class ModelView(View):
    """
    Simple pluggable view to render and instance of a db model with a template.
    """
    methods = ['GET']

    def __init__(self, model, template, instance_name=None,
                 context_processors=None):
        """
        :param model: db model class.
        :param template: template name.
        :param instance_name: template context name for the instance of model.
        :param context_processors: list of functions that receive the context
                                   dict before handing to template.
        """
        self.model = model
        self.template = template
        self.instance_name = instance_name
        self.context_processors = context_processors

    def dispatch_request(self, **ident):
        instance_name = self.instance_name or 'instance'
        context = {
            instance_name: self.model.query.get_or_404(ident)
        }
        if self.context_processors:
            for context_processor in self.context_processors:
                context_processor(context)
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
    ):
        """
        :param form_class: form class or callable.
        """
        if callable(form_class):
            form_class = form_class()
        self.form_class = form_class
        self.model = model or self.form_class.Meta.model
        self.template = template or self.template
        self.instance_name = instance_name
        self.form_render_kw = form_render_kw
        self.context_processor = context_processor

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
        form = self.form_class()
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
        )
        return render_template(self.template, **context)
