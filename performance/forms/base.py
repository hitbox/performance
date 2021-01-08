from collections import OrderedDict
from math import inf

from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import SubmitField
from wtforms.widgets import HiddenInput
from wtforms.widgets import Input
from wtforms.widgets import SubmitInput
from wtforms_alchemy import model_form_factory

from ..extensions import db

__all__ = ['ModelForm']

class BaseForm(Form):

    def __init__(self, *args, **kwargs):
        """
        Move SubmitField fields to the end. Add field ordering control. Define
        either 'fields_order' or 'only' to activate ordering.
        """
        super().__init__(*args, **kwargs)
        # move SubmitField types to the end
        move2end = []
        for key, field in self._fields.items():
            if field.type == 'SubmitField':
                move2end.append(key)
        for key in move2end:
            self._fields.move_to_end(key)
        # field order from meta
        ordering = getattr(self.meta, 'fields_order',
                           getattr(self.meta, 'only', None))
        if ordering:
            def fields_order_key(item):
                """
                Return field's index in `fields_order` meta value or infinite.
                """
                key, value = item
                try:
                    return ordering.index(key)
                except ValueError:
                    return inf
            self._fields = OrderedDict(sorted(self._fields.items(), key=fields_order_key))

    def is_delete(self):
        return hasattr(self, 'delete') and self.delete.data

    def get_buttons(self):
        return [
            field for field in self if isinstance(field.widget, SubmitInput)
        ]

    def get_non_button_inputs(self):
        return [
            field for field in self
            if not isinstance(field.widget, HiddenInput)
            and not isinstance(field.widget, SubmitInput)
        ]


class BaseFlaskForm(BaseForm, FlaskForm):
    pass


BaseModelForm = model_form_factory(BaseFlaskForm)

class ModelForm(BaseModelForm):

    @classmethod
    def get_session(self):
        return db.session
