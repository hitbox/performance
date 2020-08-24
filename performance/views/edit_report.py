import datetime as dt

from flask import Blueprint
from flask import render_template
from flask_login import login_required

from ..api.viewmodel import get_viewmodel_for_report
from ..flight.model import flight_sort_key
from ..report.model import Report

editor_bp = Blueprint('editor', __name__, url_prefix='/editor',
                      template_folder='templates', static_folder='static')

