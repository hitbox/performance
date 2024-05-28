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


class PrefixMiddleware:
    """
    Prefix url for running many apps on one machine.
    """

    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].lower().startswith(self.prefix.lower()):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            message = (
                "URL does not belong to the app."
                f" Expected prefix {self.prefix!r} "
                f" but got {environ['PATH_INFO']!r}".encode()
            )
            return [message]
