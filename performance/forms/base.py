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

    def get_buttons(self):
        # XXX
        # still used by old macro that renders forms
        return [
            field for field in self if isinstance(field.widget, SubmitInput)
        ]

    def get_non_button_inputs(self):
        # XXX
        # still used by old macro that renders forms
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
