from flask import flash
from flask import redirect
from flask import request
from flask import url_for

from performance.extensions import db

class FormSubmitter:
    """
    Encapsulate common form submitting behavior.
    """

    def __init__(self, new_instance, object_name=None):
        self.new_instance = new_instance
        self.object_name = object_name

    def on_updated(self, instance, form):
        pass

    def __call__(self, instance, form):
        if not form.validate_on_submit():
            return

        if instance is None:
            action = 'created'
            instance = self.new_instance()
            db.session.add(instance)
            form.populate_obj(instance)
        else:
            if hasattr(form, 'delete') and form.delete.data:
                action = 'deleted'
                db.session.delete(instance)
            else:
                action = 'updated'
                self.on_updated(instance, form)
                form.populate_obj(instance)
        db.session.commit()

        if self.object_name:
            flash(f'{self.object_name} {action}', 'info')

        # endpoint url stripped of arguments
        url = url_for(request.endpoint)
        return redirect(url, code=303)
