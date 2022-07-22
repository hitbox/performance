from flask import abort
from flask import redirect
from flask import render_template
from flask import request

from performance.extensions import db
from performance.utils import get_form_redirect

from .base import BaseEditView

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

            response = get_form_redirect(form)
            if response:
                return response

        context = self.get_context(
            form = form,
            instance = instance,
        )
        return render_template(self.template, **context)
