import datetime as dt

from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import login_required

todo_bp = Blueprint('todo', __name__)

@todo_bp.route('/')
def index():
    return render_template('todo.html')
