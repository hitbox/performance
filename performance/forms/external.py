import wtforms

from flask_wtf import FlaskForm
from wtforms.validators import Optional
from wtforms.widgets import HiddenInput

from performance import models

from .base import BaseForm
from .model_converter import model_form

class QueryParametersForm(wtforms.Form):
    """
    User controlled parameters for the external query. Used for the parameters
    of imports and updates.
    """

    show_kg = wtforms.BooleanField(
        label = 'Show kg Column?',
    )

    show_all_fields = wtforms.BooleanField(
        label = 'Show All Fields?',
        default = False,
    )

    submit = wtforms.SubmitField(
        label = 'Query...',
        name = 's',
    )


class LegPaxFormBase(
    BaseForm,
    FlaskForm,
):
    """
    Form for LegPax objects from external database.
    """

    baggage_weight_lbs = wtforms.FloatField(
        widget = HiddenInput(),
    )


LegPaxForm = model_form(
    model = models.LegPax,
    base_class = LegPaxFormBase,
    field_args = dict(
        baggage_weight = dict(
            widget = HiddenInput(),
        ),
    ),
)


class LegFormBase(
    BaseForm,
    FlaskForm,
):
    """
    Form for Leg objects from external database.
    """


LegForm = model_form(
    model = models.Leg,
    base_class = LegFormBase,
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
    ),
)


class ResultRowForm(BaseForm):
    """
    Form for rows of results from external database.
    """

    fn_number = wtforms.StringField()
    dep_dt = wtforms.DateTimeField()
    arr_dt = wtforms.DateTimeField()
    baggage_weight_kg = wtforms.IntegerField()
    baggage_weight_lbs = wtforms.IntegerField()


class ResultsForm(
    BaseForm,
    FlaskForm,
):
    """
    Form for all the result of the external database query.
    """

    rows = wtforms.FieldList(
        wtforms.FormField(ResultRowForm),
    )

    submit = wtforms.SubmitField(
        label = 'Import...',
    )


class InternalFlightForm(
    BaseForm,
    FlaskForm,
):
    """
    Internal flight data matching some data from external database.
    """

    id = wtforms.IntegerField(
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    origin_departure_actual_date = wtforms.DateField(
        validators = [
            Optional(),
        ],
        render_kw = dict(
            class_ = 'hidden',
        )
    )

    origin_departure_actual_time = wtforms.TimeField(
        validators = [
            Optional(),
        ],
        render_kw = dict(
            class_ = 'hidden',
        )
    )

    destination_arrival_actual_date = wtforms.DateField(
        validators = [
            Optional(),
        ],
        render_kw = dict(
            class_ = 'hidden',
        )
    )

    destination_arrival_actual_time = wtforms.TimeField(
        validators = [
            Optional(),
        ],
        render_kw = dict(
            class_ = 'hidden',
        )
    )

    weight = wtforms.IntegerField(
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

    dep_dt_date = wtforms.DateField(
        validators = [Optional()],
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    dep_dt_time = wtforms.TimeField(
        validators = [Optional()],
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    arr_dt_date = wtforms.DateField(
        validators = [Optional()],
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    arr_dt_time = wtforms.TimeField(
        validators = [Optional()],
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    baggage_weight_kg = wtforms.IntegerField(
        validators = [Optional()],
        render_kw = dict(
            class_ = 'hidden',
        ),
    )

    baggage_weight_lbs = wtforms.IntegerField(
        validators = [Optional()],
        render_kw = dict(
            class_ = 'hidden',
        ),
    )


class DiffForm(
    BaseForm,
    FlaskForm,
):
    """
    Single difference between flights.
    """

    internal_attr = wtforms.StringField()
    internal_label = wtforms.StringField()

    external_attr = wtforms.StringField()
    external_label = wtforms.StringField()

    do_update = wtforms.BooleanField(
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

    internal_flight = wtforms.FormField(
        InternalFlightForm,
    )

    external_flight = wtforms.FormField(
        ExternalFlightForm,
    )

    diffs = wtforms.FieldList(
        wtforms.FormField(
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


class ChangesForm(
    BaseForm,
    FlaskForm,
):

    flight_changes = wtforms.FieldList(
        wtforms.FormField(
            FlightChangesForm,
        ),
    )

    clear = wtforms.SubmitField()

    submit = wtforms.SubmitField(
        label = 'Import...',
    )

    def _all_do_updates(self):
        checkboxes = []
        for flight_changes_form in self.flight_changes:
            for diff_form in flight_changes_form.diffs:
                checkboxes.append(diff_form.do_update)
        return checkboxes

