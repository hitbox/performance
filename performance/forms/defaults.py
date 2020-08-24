from flask import request

from ..models import FlightType

def flight_type():
    if 'flight_type_id' in request.args:
        try:
            flight_type_id = int(request.args['flight_type_id'])
        except ValueError:
            pass
        else:
            return FlightType.query.get(flight_type_id)
