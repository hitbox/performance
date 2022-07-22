from flask import Blueprint

from performance.authorization import admin_check
from performance.models import Delay
from performance.pluggable import ListView

delay_bp = Blueprint('delay', __name__)

delay_bp.add_url_rule(
    '/',
    view_func = admin_check(
        ListView.as_view(
            'list',
            template = 'delay/list.html',
            items_getter = lambda: Delay.query.order_by(Delay.code).all()
        )))

@delay_bp.cli.command('list')
def delay_list():
    """
    List delay objects
    """
    for delay in Delay.query.order_by(Delay.code):
        print(delay)
