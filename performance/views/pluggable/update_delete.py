from flask import abort
from flask import redirect
from flask import render_template

from performance.extensions import db

from .base import BaseEditView

class UpdateDeleteView(BaseEditView):
    """
    Update/delete an object instance.
    """

    def dispatch_request(self, **ident):
        if callable(self.disabled) and self.disabled():
            abort(404)
        instance = self.get_instance(ident)
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
