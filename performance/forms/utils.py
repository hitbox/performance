from wtforms import BooleanField
from wtforms.fields.core import UnboundField
from wtforms.validators import InputRequired

from performance.models.mixin import VisibilityMixin

def remove_required_from_boolean_fields(form_class):
    """
    Remove the required validator from all boolean fields. This counteracts the
    wtforms_sqlalchemy.orm.model_form's hard-coded adding a required validator
    to any nullable=False field.
    """
    for attrname in dir(form_class):
        field = getattr(form_class, attrname)
        # skip not a form field
        if not isinstance(field, UnboundField):
            continue
        # skip not a boolean form field
        if field.field_class is not BooleanField:
            continue
        validators = field.kwargs.get('validators', [])
        for validator in validators:
            # skip not a required validator
            if not isinstance(validator, InputRequired):
                continue
            # remove required validator
            validators.remove(validator)

def visibility_column_names():
    return [n for n in dir(VisibilityMixin) if not n.startswith('_')]

def visibility_column_field_args(class_name):
    return {
        name: dict(
            label = getattr(class_name, name).info['form_label'],
        )
        for name in visibility_column_names()
    }
