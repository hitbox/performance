from wtforms import fields as wtforms_fields
from wtforms_sqlalchemy.orm import ModelConverter
from wtforms_sqlalchemy.orm import converts
from wtforms_sqlalchemy.orm import model_form as wtforms_sqlalchemy_orm_model_form

from performance.extensions import db

from .fields import StringTimeField
from .base import ModelForm

class PerformanceModelConverter(ModelConverter):
    """
    Convert SQLAlchemy types to wtforms fields.
    """

    @converts('Time')
    def conv_Time(self, field_args, **extra):
        return StringTimeField(**field_args)


def model_form(model, **kwargs):
    kwargs.setdefault('db_session', db.session)
    kwargs.setdefault('base_class', ModelForm)
    kwargs.setdefault('converter', PerformanceModelConverter)
    return wtforms_sqlalchemy_orm_model_form(model, **kwargs)
