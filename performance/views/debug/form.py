from flask import Blueprint
from flask import abort
from flask import flash
from flask import render_template
from werkzeug.datastructures import MultiDict
from wtforms import BooleanField
from wtforms import Form
from wtforms import FormField
from wtforms import IntegerField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import validators

from performance.extensions import db
from performance.models import Flight
from performance.models import Report

debugform_bp = Blueprint('debugform', __name__, url_prefix='/form')

class DebugFieldForm(Form):

    string_field = StringField()
    very_long = StringField(
        validators = [
            validators.Length(min=99),
        ],
    )
    fifty_to_onehundred = IntegerField(
        validators = [
            validators.NumberRange(min=50, max=100),
            validators.NoneOf([55, 60, 150]),
        ],
    )


class DebugForm(Form):
    """
    Simple form to debug rendering forms.
    """

    name = StringField('Name')
    onoff = BooleanField('On/off')
    number = IntegerField('Number')

    subform = FormField(DebugFieldForm)

    submit = SubmitField('Submit')
    delete = SubmitField('Delete', render_kw={'class': 'danger'})


def get_form_instance():
    formdata = MultiDict([
        ('name', 'This is my name'),
        ('onoff', 'yes'),
        ('number', 'invalid'),
        ('subform-a', 'subform-a'),
        ('subform-fifty_to_onehundred', '150'),
    ])
    form = DebugForm(formdata)
    form.validate()
    return form

@debugform_bp.route('/')
def index():
    context = dict(
        form = get_form_instance(),
    )
    return render_template('debug/form.html', **context)


