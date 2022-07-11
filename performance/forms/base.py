import math

from collections import OrderedDict

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._update_fields_order()

    def _update_fields_order(self):
        if hasattr(self.Meta, 'fields_order'):
            fields_order = self.Meta.fields_order

            if isinstance(fields_order, dict):

                def sortkey(item):
                    name, field = item
                    return fields_order.get(name, math.inf)

            elif isinstance(fields_order, list):

                def sortkey(item):
                    name, field = item
                    if name in fields_order:
                        return fields_order.index(name)
                    else:
                        return math.inf

            self._fields = OrderedDict(
                sorted(self._fields.items(), key=sortkey)
            )


class BaseFlaskForm(BaseForm, FlaskForm):
    pass


BaseModelForm = model_form_factory(BaseFlaskForm)

class ModelForm(BaseModelForm):

    @classmethod
    def get_session(self):
        return db.session
