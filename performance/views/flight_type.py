import click

from flask import Blueprint

from ..authorization import admin_check
from ..extensions import db
from ..models import FlightType

from .pluggable import SimpleListView

flight_type_bp = Blueprint('flight_type', __name__)

# month to date flights with chargeable delays
flight_type_bp.add_url_rule(
    '/list',
    view_func = admin_check(
        SimpleListView.as_view(
            'list',
            template = 'flight_type/list.html',
            items_getter = lambda:
                FlightType.query.order_by(FlightType.report_order).all(),
        )))

@flight_type_bp.cli.command('add', help='Add flight type.')
@click.option('--name')
@click.option('--report-order', type=click.INT, help='Order to display type.')
def add(name, report_order):
    flight_type = FlightType(name=name, report_order=report_order)
    db.session.add(flight_type)
    db.session.commit()
