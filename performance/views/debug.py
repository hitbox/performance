from flask import Blueprint
from flask import abort
from flask import flash
from flask import render_template

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug')
def index():
    """
    Hidden route for developing the flash messages.
    """
    flash('Info Message', 'info')
    flash('Success Message', 'success')
    flash('Warning Message', 'warning')
    flash('Error Message', 'error')
    flash('Multiline flash message\nLine 1\nLine 2', 'info')
    flash('TODO message only for development', 'todo')
    return render_template('debug.html')

@debug_bp.route('/return-abort/<int:error>')
def return_abort(error):
    abort(error)
