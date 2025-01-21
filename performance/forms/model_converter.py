from sqlalchemy_utils import ChoiceType
from wtforms import fields as wtforms_fields
from wtforms_sqlalchemy.orm import ModelConverter
from wtforms_sqlalchemy.orm import converts
from wtforms_sqlalchemy.orm import model_form as wtforms_sqlalchemy_orm_model_form

from performance.extensions import db

from .fields import StringTimeField

class coercer:

    def __init__(self, column):
        self.column = column

    def __call__(self, value):
        try:
            return self.column.type._coerce(int(value))
        except:
            return value


class PerformanceModelConverter(ModelConverter):
    """
    Convert SQLAlchemy types to wtforms fields.
    """

    @converts('Time')
    def conv_Time(self, field_args, **extra):
        """
        Time fields as simple, permissive text field.
        """
        return StringTimeField(**field_args)

    @converts('ChoiceType')
    def conv_ChoiceType(self, field_args, **extra):
        column = extra['column']
        field_args.setdefault('coerce', coercer(column))
        return wtforms_fields.SelectField(**field_args)


def model_form(model, **kwargs):
    """
    Create form from model with defaults for the performance reports project.
    """
    kwargs.setdefault('db_session', db.session)
    kwargs.setdefault('converter', PerformanceModelConverter())
    return wtforms_sqlalchemy_orm_model_form(model, **kwargs)
