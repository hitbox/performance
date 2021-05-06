from flask import Blueprint

from performance.authorization import edit_check

from performance.dhl.models import Flight
from performance.dhl.models import Report
from performance.dhl.schemas import FlightSchema
from performance.dhl.schemas import ReportSchema

xhr_bp = Blueprint('xhr', __name__)

flight_schema = FlightSchema()

@xhr_bp.route('/<report_id>')
@edit_check
def test(report_id):
    report = Report.query.get(report_id)
    data = flight_schema.dump(report.flights, many=True)
    # left off here. just got a list of flights to go through.
    return {'data': data}
