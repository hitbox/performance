from flask.views import View

# get instance from view args or none
# get form passing instance
# on post, validate

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
        if (
            model is None
            and hasattr(self.form_class, 'Meta')
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
