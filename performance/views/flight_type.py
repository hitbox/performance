import click

from flask import Blueprint

from ..extensions import db
from ..models import FlightType

flight_type_bp = Blueprint('flight_type', __name__)

@flight_type_bp.cli.command('add', help='Add flight type.')
@click.option('--name')
@click.option('--report-order', type=click.INT, help='Order to display type.')
def add(name, report_order):
    flight_type = FlightType(name=name, report_order=report_order)
    db.session.add(flight_type)
    db.session.commit()
