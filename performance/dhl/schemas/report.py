from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from performance.dhl.models import Report

class ReportSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Report
