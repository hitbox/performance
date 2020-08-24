from flask import Blueprint
from flask import request
from flask import render_template
from flask import redirect

from ...authorization import edit_check
from ...extensions import db
from ...models import FlightType
from ...views.pluggable import CreateView
from ...views.pluggable import UpdateDeleteView

from ..forms import ScheduledFlightForm

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


scheduled_flight_bp.add_url_rule(
    '/create/<int:scheduled_report_id>',
    view_func = edit_check(
        CreateScheduledFlightView.as_view(
            'create',
            ScheduledFlightForm,
        )))

scheduled_flight_bp.add_url_rule(
    '/edit/<int:id>',
    view_func = edit_check(
        UpdateDeleteView.as_view(
            'edit',
            ScheduledFlightForm,
        )))
