import logging

class LoggingMiddleware:
    """
    Access logging middleware
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        args = [
            environ.get('REMOTE_HOST'),
            environ.get('HTTP_USER_AGENT'),
            environ.get('REQUEST_METHOD'),
            environ.get('REQUEST_URI'),
        ]
        fmt = ' '.join('%s' for _ in args)
        logging.info(fmt, *args)
        return self.app(environ, start_response)
