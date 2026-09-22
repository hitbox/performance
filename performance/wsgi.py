from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

from .app import create_app
from .app import init_prefix_middleware

def create_wsgi_app():
    app = create_app()
    app = init_prefix_middleware(app)
    return app
