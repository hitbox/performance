from collections import OrderedDict

from flask import redirect
from flask import request
from flask import url_for
from flask_wtf import FlaskForm
from wtforms import Form
from wtforms_alchemy import model_form_factory

from ..extensions import db
from ..utils import get_form_redirect
from ..utils import sortfunc_by_type

class BaseForm(Form):
    """
    Base form class for all forms to keep things consistent.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        obj = kwargs.get('obj', None)
        self._order_fields()
        self._presentation(obj)
        self._update_from_view_args()

    def _update_from_view_args(self):
        for field in self:
            if (
                field.data is None
                and field.name in request.view_args
            ):
                field.data = request.view_args[field.name]

    def _presentation(self, obj):
        # wtforms is removing "_obj kluge". new strategy seems to be passing it around.
        if (
            not hasattr(self, 'Meta')
            or not getattr(self.Meta, 'presentation', None)
        ):
            return

        # relabeling and button modification
        label_text = 'Create'
        if hasattr(self, 'submit'):
            submit = self.submit
            if obj:
                label_text = 'Update'
            submit.label.text = label_text

        if hasattr(self, 'delete') and not obj:
            # new object form with delete button does not make sense
            del self.delete

    def _order_fields(self):
        """
        If available, apply ordering to form fields.
        """
        if not hasattr(self.Meta, 'fields_order'):
            return
        fields_order = self.Meta.fields_order
        sortkey = sortfunc_by_type(fields_order)
        self._fields = OrderedDict(sorted(self._fields.items(), key=sortkey))

    @property
    def is_delete(self):
        return hasattr(self, 'delete') and self.delete and self.delete.data

    @classmethod
    def standard_submit(cls, form, instance=None):
        """
        Create, edit or edit an instance depending on context. This method
        exists to eliminate doing this same thing all over the place.
        """
        if not form.validate_on_submit():
            return

        if instance:
            if form.is_delete:
                # submitted delete
                db.session.delete(instance)
            else:
                # submitted update
                form.populate_obj(instance)
        else:
            # submitted create
            if not hasattr(form.Meta, 'model'):
                raise ValueError(
                    'No model attribute on Meta to create instance from.')

            instance = form.Meta.model()
            db.session.add(instance)
            form.populate_obj(instance)

        db.session.commit()
        response = get_form_redirect(form)
        if response:
            return response

        url = url_for(request.endpoint, **request.view_args)
        return redirect(url, code=303)


class BaseFlaskForm(
    BaseForm,
    FlaskForm,
):
    """
    Mix `flask_wtf.FlaskForm` with this project's custom base form.
    """


BaseModelForm = model_form_factory(BaseFlaskForm)

class ModelForm(BaseModelForm):

    @classmethod
    def get_session(self):
        return db.session
