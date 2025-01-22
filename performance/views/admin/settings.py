import click

from flask import Blueprint
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from performance.extensions import db
from performance.forms import SettingsForm
from performance.models import FlightType
from performance.models import Performance

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

def _get_performance_object():
    """
    Return the single performance (settings) object.
    """
    stmt = db.select(Performance)
    performance = db.session.scalars(stmt).one()
    return performance

@settings_bp.route('/', methods=['GET', 'POST'])
def edit():
    """
    Edit settings metadata settings.
    """
    performance = _get_performance_object()
    form = SettingsForm(obj=performance)

    if form.validate_on_submit():
        form.populate_obj(performance)
        db.session.commit()
        return redirect(url_for(request.endpoint))

    return render_template('admin/settings.html', form=form)

# using a group so that if other settings are created, they can go under their
# own command group

@settings_bp.cli.group()
def default_flight_type():
    pass

@default_flight_type.command('show')
def show():
    """
    Show currently set default FlightType object.
    """
    performance = _get_performance_object()
    click.echo(performance.default_flight_type.name)

@default_flight_type.command('list')
def list():
    """
    List availble values for default FlightType.
    """
    performance = _get_performance_object()
    stmt = db.select(FlightType)
    for flight_type in db.session.scalars(stmt):
        if flight_type is performance.default_flight_type:
            prefix = '-> '
        else:
            prefix = '   '
        click.echo(f'{prefix}{flight_type.name}')

@default_flight_type.command('set')
@click.argument('flight_type_name')
def show(flight_type_name):
    """
    """
    stmt = db.select(FlightType).where(FlightType.name == flight_type_name)
    flight_type = db.session.scalars(stmt).one()
    performance = _get_performance_object()
    performance.default_flight_type = flight_type
    db.session.commit()
