from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from performance.dhl.models import Flight

class FlightSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Flight
        include_relationships = False
