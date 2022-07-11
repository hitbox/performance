from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask.views import View

from performance.extensions import db

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
