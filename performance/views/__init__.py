from flask import current_app
from flask import flash
from flask import redirect
from flask import url_for

from .user import user_bp

def init_app(app):
    app.register_blueprint(user_bp)

    @app.route('/')
    def index():
        return redirect(url_for('select_date.goto_today'))

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
