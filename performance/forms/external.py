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
from wtforms.widgets import HiddenInput
from wtforms.widgets import TextInput

from performance import models

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

    clear = SubmitField()


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


class PartialFlightForm(Form):
    """
    Internal flight data matching some data from external database.
    """

    id = IntegerField()
    flight_number = StringField()
    origin_departure_actual_date = DateField()
    origin_departure_actual_time = TimeField()
    destination_arrival_actual_date = DateField()
    destination_arrival_actual_time = TimeField()
    weight = IntegerField()


class FlightChangesForm(Form):
    """
    Some fields for flights that match against an external database showing the
    internal value against the external. Also giving an *_update checkbox for
    selecting which changes to keep.
    """

    dep_dt_date = DateField()
    dep_dt_date_is_diff = BooleanField()
    dep_dt_date_update = BooleanField(
        default = True,
    )

    dep_dt_time = TimeField()
    dep_dt_time_is_diff = BooleanField()
    dep_dt_time_update = BooleanField(
        default = True,
    )

    arr_dt_date = DateField()
    arr_dt_date_is_diff = BooleanField()
    arr_dt_date_update = BooleanField(
        default = True,
    )

    arr_dt_time = TimeField()
    arr_dt_time_is_diff = BooleanField()
    arr_dt_time_update = BooleanField(
        default = True,
    )

    baggage_weight_kg = IntegerField()

    baggage_weight_lbs = IntegerField()
    baggage_weight_lbs_is_diff = BooleanField()
    baggage_weight_lbs_update = BooleanField(
        default = True,
    )

    flight = FormField(
        PartialFlightForm,
    )

    def _matched_fields(self, param_form):
        """
        Generate field data tuples which relate data from external to internal
        database.
        """
        # NOTE
        # - passing param_form for option to show all
        show_all_fields = param_form.show_all_fields.data
        if show_all_fields or self.dep_dt_date_is_diff.data:
            yield (
                'ATD Date',
                bool(self.dep_dt_date_is_diff.data),
                self.dep_dt_date,
                self.flight.origin_departure_actual_date,
                self.dep_dt_date_update,
            )
        if show_all_fields or self.dep_dt_time_is_diff.data:
            yield (
                'ATD Time',
                bool(self.dep_dt_time_is_diff.data),
                self.dep_dt_time,
                self.flight.origin_departure_actual_time,
                self.dep_dt_time_update,
            )
        if show_all_fields or self.arr_dt_date_is_diff.data:
            yield (
                'ATA Date',
                bool(self.arr_dt_date_is_diff),
                self.arr_dt_date,
                self.flight.destination_arrival_actual_date,
                self.arr_dt_date_update,
            )
        if show_all_fields or self.arr_dt_date_is_diff.data:
            yield (
                'ATA Time',
                bool(self.arr_dt_time_is_diff),
                self.arr_dt_time,
                self.flight.destination_arrival_actual_time,
                self.arr_dt_time_update,
            )
        if show_all_fields or self.baggage_weight_lbs_is_diff.data:
            yield (
                'Weight (lbs)',
                bool(self.baggage_weight_lbs_is_diff),
                self.baggage_weight_lbs,
                self.flight.weight,
                self.baggage_weight_lbs_update,
            )


class ChangesForm(BaseFlaskForm):

    flight_changes = FieldList(
        FormField(FlightChangesForm),
    )

    submit = SubmitField(
        label = 'Import...',
    )
