from flask import abort
from flask import redirect
from flask import render_template
from flask.views import View

from performance.extensions import db
from performance.utils import get_form_redirect

from .base import BaseEditView

class UpdateView(BaseEditView):
    """
    Update/delete an object instance.
    """
    methods = ['GET', 'POST']

    def dispatch_request(self, **ident):
        if callable(self.disabled) and self.disabled():
            abort(404)
        instance = self.get_instance(ident)
        form = self.form_class(obj=instance)
        #form.submit.label.text = 'Update'
        if form.validate_on_submit():
            if instance:
                if form.delete.data:
                    db.session.delete(instance)
                    # TODO: response for delete
                else:
                    form.populate_obj(instance)
            else:
                instance = self.model()
                db.session.add(instance)
                form.populate_obj(instance)
            db.session.commit()

            response = get_form_redirect(form)
            if response:
                return response

        context = self.get_context(
            form = form,
            instance = instance,
        )
        return render_template(self.template, **context)
