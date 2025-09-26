from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import DateField
from wtforms import DateTimeField
from wtforms import FieldList
from wtforms import FloatField
from wtforms import Form
from wtforms import FormField
from wtforms import IntegerField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import TimeField
from wtforms.validators import Optional
from wtforms.widgets import HiddenInput

from performance import models

from .base import BaseForm
from .model_converter import model_form

class QueryParametersForm(Form):
    """
    External query form. Simply a submit button for GET.
    """

    submit = SubmitField(
        label = 'Query...',
        name = 's',
    )


class ResultRowForm(BaseForm):
    """
    Form for rows of results from external database.
    """

    fn_number = StringField()
    dep_dt = DateTimeField()
    arr_dt = DateTimeField()
    baggage_weight_kg = IntegerField()
    baggage_weight_lbs = IntegerField()


class ResultsForm(
    BaseForm,
    FlaskForm,
):
    """
    Form for all the result of the external database query.
    """

    rows = FieldList(
        FormField(ResultRowForm),
    )

    submit = SubmitField(
        label = 'Import...',
    )


class InternalFlightForm(
    BaseForm,
    FlaskForm,
):
    """
    Internal flight data matching some data from external database.
    """

    id = IntegerField(
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    tail_number = StringField()

    origin_departure_actual_date = DateField(
        validators = [
            Optional(),
        ],
        render_kw = dict(
            class_ = 'hidden',
        )
    )

    origin_departure_actual_time = TimeField(
        validators = [
            Optional(),
        ],
        render_kw = dict(
            class_ = 'hidden',
        )
    )

    destination_arrival_actual_date = DateField(
        validators = [
            Optional(),
        ],
        render_kw = dict(
            class_ = 'hidden',
        )
    )

    destination_arrival_actual_time = TimeField(
        validators = [
            Optional(),
        ],
        render_kw = dict(
            class_ = 'hidden',
        )
    )

    # Has to be nullable for updates to null fields.
    weight = IntegerField(
        validators = [
            Optional(),
        ],
        render_kw = dict(
            class_ = 'hidden',
        )
    )


class ExternalFlightForm(
    BaseForm,
    FlaskForm,
):

    dep_dt_date = DateField(
        validators = [Optional()],
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    dep_dt_time = TimeField(
        validators = [Optional()],
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    arr_dt_date = DateField(
        validators = [Optional()],
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    arr_dt_time = TimeField(
        validators = [Optional()],
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    baggage_weight_kg = IntegerField(
        validators = [Optional()],
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    baggage_weight_lbs = IntegerField(
        validators = [Optional()],
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    tail_number = StringField()
    origin_departure_actual_date = DateField()
    origin_departure_actual_time = TimeField()

    destination_arrival_actual_date = DateField()
    destination_arrival_actual_time = TimeField()

    # Has to be nullable for updates to null fields.
    weight = IntegerField(validators=[Optional()])


class DiffForm(
    BaseForm,
    FlaskForm,
):
    """
    Single difference between flights.
    """

    internal_attr = StringField()
    internal_label = StringField()

    external_attr = StringField()
    external_label = StringField()

    do_update = BooleanField(
        # user checkbox to choose to do this update
        default = True,
        render_kw = dict(
            class_ = 'flight-changes',
        ),
    )


class FlightChangesForm(
    BaseForm,
    FlaskForm,
):
    """
    Contain a list of diffs between internal and external flights.
    """

    internal_flight = FormField(InternalFlightForm)

    external_flight = FormField(ExternalFlightForm)

    diffs = FieldList(FormField(DiffForm))

    # - {internal,external}_field methods serve to remind us that only the
    #   fields off the two flight forms, that are being changed, can be
    #   rendered.
    # - If we render them all, they are sent back and fail validation.
    # - Also they must be rendered.

    def internal_field(self, attrname):
        if attrname:
            return getattr(self.internal_flight, attrname)

    def external_field(self, attrname):
        if attrname:
            return getattr(self.external_flight, attrname)


class ChangesForm(
    BaseForm,
    FlaskForm,
):

    flight_changes = FieldList(FormField(FlightChangesForm))

    clear = SubmitField()

    submit = SubmitField(
        label = 'Import...',
    )

    def _all_do_updates(self):
        checkboxes = []
        for flight_changes_form in self.flight_changes:
            for diff_form in flight_changes_form.diffs:
                checkboxes.append(diff_form.do_update)
        return checkboxes

