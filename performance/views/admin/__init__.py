from flask import Blueprint
from flask import render_template

from performance.authorization import admin_check

from .delay import delay_bp
from .flight_type import flight_type_bp
from .performance_contract import performance_contract_bp
from .performance_tier import performance_tier_bp
from .users import user_bp

admin_bp = Blueprint('admin', __name__)

admin_bp.register_blueprint(delay_bp)
admin_bp.register_blueprint(flight_type_bp)
admin_bp.register_blueprint(performance_contract_bp)
admin_bp.register_blueprint(performance_tier_bp)
admin_bp.register_blueprint(user_bp)

@admin_bp.before_request
@admin_check
def before_request():
    """
    Using decorators to enforce user is logged in as admin for all routes.
    """

@admin_bp.route('/')
def index():
    """
    Admin index page.
    """
    return render_template('admin/index.html')
