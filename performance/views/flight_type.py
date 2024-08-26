import click

from flask import Blueprint

from performance.extensions import db
from performance.models import FlightType

flight_type_bp = Blueprint('flight_type', __name__)

name_option = click.option('--name')

report_order_option = click.option(
    '--report-order',
    type = click.INT,
    help = FlightType.report_order.doc,
)

is_controllable_option = click.option(
    '--is-controllable',
    type = click.BOOL,
    help = FlightType.is_controllable.doc,
)

is_lane_option = click.option(
    '--is-lane',
    type = click.BOOL,
    help = FlightType.is_lane.doc,
)

is_active_option = click.option(
    '--is-active',
    type = click.BOOL,
    help = FlightType.is_active.doc,
)

@flight_type_bp.cli.command()
def list():
    """
    List FlightType objects.
    """
    stmt = db.select(FlightType).order_by(FlightType.id)
    for flight_type in db.session.scalars(stmt):
        click.echo(f'{flight_type.id}. {flight_type.name}')


@flight_type_bp.cli.command()
@click.argument('id')
@name_option
@report_order_option
@is_controllable_option
@is_lane_option
@is_active_option
def update(id, name, report_order, is_controllable, is_lane, is_active):
    """
    Update a FlightType object.
    """
    names = ['name', 'report_order', 'is_controllable', 'is_lane', 'is_active']
    options = [name, report_order, is_controllable, is_lane, is_active]
    if not any(filter(None, options)):
        click.echo('At least one option is required.')
        return

    flight_type = db.session.get(FlightType, id)
    for name, value in zip(names, options):
        if value is not None:
            setattr(flight_type, name, value)

    db.session.commit()


@flight_type_bp.cli.command('add', help='Add flight type.')
@name_option
@report_order_option
@is_controllable_option
@is_lane_option
@is_active_option
def add(name, report_order, is_controllable, is_lane, is_active):
    """
    Add FlightType object.
    """
    flight_type = FlightType(
        name = name,
        report_order = report_order,
        is_controllable = is_controllable,
        is_lane = is_lane,
        is_active = is_active,
    )
    db.session.add(flight_type)
    db.session.commit()
