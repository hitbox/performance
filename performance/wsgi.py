from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

from .app import create_app

def create_wsgi_app():
    app = create_app()

    if 'PREFIX' in app.config:
        # Overwrite app name with dispatch middleware for prefixing the url
        prefix = app.config['PREFIX']
        print(f'Using prefix: {prefix}')
        app = DispatcherMiddleware(
            Response('Not Found', status=404), {
                prefix: app
        })

    return app
