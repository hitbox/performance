from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .models import Flight
from .models import Report

class FlightSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Flight
        include_relationships = False


class ReportSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Report
