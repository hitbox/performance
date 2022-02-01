from flask import Blueprint
from flask import request
from flask import render_template
from flask import redirect

from ..authorization import admin_check
from ..authorization import edit_check
from ..extensions import db
from ..models import FlightType

from .pluggable import CreateView
from .pluggable import UpdateDeleteView

scheduled_flight_bp = Blueprint('scheduled_flight', __name__)

class CreateScheduledFlightView(CreateView):

    def dispatch_request(self, scheduled_report_id):
        form = self.form_class(scheduled_report_id=scheduled_report_id)
        if form.validate_on_submit():
            flight = self.model()
            db.session.add(flight)
            flight.scheduled_report_id = scheduled_report_id
            form.populate_obj(flight)
            db.session.commit()
            if hasattr(form, 'backurl') and form.backurl.data:
                return redirect(form.backurl.data)
        elif request.method == 'GET':
            form.submit.label.text = 'Create'
            del form.delete
        return render_template(self.template, form=form)


def get_scheduled_flight_form_class():
    # NOTE: must delay importing because wtforms_alchemy is very aggressive
    from ..forms import ScheduledFlightForm
    return ScheduledFlightForm

scheduled_flight_bp.add_url_rule(
    '/create/<int:scheduled_report_id>',
    view_func = admin_check(edit_check(
        CreateScheduledFlightView.as_view(
            'create',
            get_scheduled_flight_form_class,
            template = 'scheduled_flight_edit.html',
        ))))

scheduled_flight_bp.add_url_rule(
    '/edit/<int:id>',
    view_func = admin_check(edit_check(
        UpdateDeleteView.as_view(
            'edit',
            get_scheduled_flight_form_class,
            template = 'scheduled_flight_edit.html',
        ))))
