from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from werkzeug.exceptions import HTTPException

from ..month import Weekday

from .user import user_bp

def init_app(app):
    """
    Initialize generic shared app views.
    """
    app.register_blueprint(user_bp)

    @app.context_processor
    def inject():
        return dict(
            weekday = {n:Weekday(n) for n in range(7)},
        )


    @app.route('/')
    def index():
        return redirect(url_for('select_date.goto_today'))

    @app.errorhandler(HTTPException)
    def error(e):
        """
        HTTP Error Code page to make everything styled consistently.
        """
        return (render_template('error.html', e=e), e.code)

    if app.env == 'development':
        init_app_development(app)

def init_app_development(app):
    """
    For development only!
    """
    from .debug import debug_bp
    from .todo import todo_bp

    app.register_blueprint(todo_bp, url_prefix='/todo')

    @app.before_first_request
    def alert_debugging_urls():
        """
        Alert user has debugginig page available.
        """
        debug_url = url_for('debug.index')
        msg = '<a class="flash" href="%s">Debugging available here</a>' % debug_url
        flash(msg, 'info')

    app.register_blueprint(debug_bp)
