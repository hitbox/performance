import humanize
import werkzeug

from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for

from .debug import debug_bp
from .user import user_bp

def init_app(app):
    app.register_blueprint(user_bp)

    @app.route('/')
    def index():
        return redirect(url_for('select_date.goto_today'))

    @app.errorhandler(werkzeug.exceptions.HTTPException)
    def error(e):
        """
        HTTP Error Code page to make everything styled consistently.
        """
        return (render_template('error.html', e=e), e.code)

    @app.context_processor
    def inject():
        """
        Inject variables into the templates.
        """
        return {
            # have this be a user preference too
            'datefmt': current_app.config['DATEFMT'],
            'datetimefmt': current_app.config['DATETIMEFMT'],
            'humanize': humanize,
        }

    if app.env == 'development':
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
