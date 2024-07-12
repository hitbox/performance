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
from wtforms.widgets import TextInput

from performance import models
from performance.utils import deep_getattr

from .base import BaseFlaskForm
from .base import BaseForm
from .base import ModelForm
from .flight import FlightForm

class QueryParametersForm(Form):
    """
    User controlled parameters for the external query. Used for the parameters
    of imports and updates.
    """

    show_kg = BooleanField(
        label = 'Show kg Column?',
    )

    show_all_fields = BooleanField(
        label = 'Show All Fields?',
        default = False,
    )

    submit = SubmitField(
        label = 'Query...',
        name = 's',
    )


class LegPaxForm(ModelForm):
    """
    Form for LegPax objects from external database.
    """
    class Meta:
        model = models.LegPax
        field_args = dict(
            baggage_weight = dict(
                widget = HiddenInput(),
            ),
        )

    baggage_weight_lbs = FloatField(
        widget = HiddenInput(),
    )


class LegForm(ModelForm):
    """
    Form for Leg objects from external database.
    """
    class Meta:
        model = models.Leg
        field_args = dict(
            fn_number = dict(
                widget = HiddenInput(),
            ),
            dep_dt = dict(
                widget = HiddenInput(),
            ),
            arr_dt = dict(
                widget = HiddenInput(),
            ),
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


class ResultsForm(BaseFlaskForm):
    """
    Form for all the result of the external database query.
    """

    rows = FieldList(
        FormField(ResultRowForm),
    )

    submit = SubmitField(
        label = 'Import...',
    )


class InternalFlightForm(BaseFlaskForm):
    """
    Internal flight data matching some data from external database.
    """

    id = IntegerField(
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

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

    weight = IntegerField(
        validators = [
            Optional(),
        ],
        render_kw = dict(
            class_ = 'hidden',
        )
    )


class ExternalFlightForm(BaseFlaskForm):

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


class DiffForm(BaseFlaskForm):
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


class FlightChangesForm(BaseFlaskForm):
    """
    Contain a list of diffs between internal and external flights.
    """

    internal_flight = FormField(
        InternalFlightForm,
    )

    external_flight = FormField(
        ExternalFlightForm,
    )

    diffs = FieldList(
        FormField(
            DiffForm,
        ),
    )

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


class ChangesForm(BaseFlaskForm):

    flight_changes = FieldList(
        FormField(
            FlightChangesForm,
        ),
    )

    clear = SubmitField()

    submit = SubmitField(
        label = 'Import...',
    )
