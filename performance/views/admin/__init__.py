from flask import Blueprint
from flask import render_template

from .delay import delay_bp
from .flight_type import flight_type_bp
from .performance_contract import performance_contract_bp
from .performance_tier import performance_tier_bp
from .settings import settings_bp
from .users import user_bp

admin_bp = Blueprint('admin', __name__)

admin_bp.register_blueprint(delay_bp)
admin_bp.register_blueprint(flight_type_bp)
admin_bp.register_blueprint(performance_contract_bp)
admin_bp.register_blueprint(performance_tier_bp)
admin_bp.register_blueprint(settings_bp)
admin_bp.register_blueprint(user_bp)

@admin_bp.route('/')
def index():
    """
    Admin index page.
    """
    return render_template('admin/index.html')
