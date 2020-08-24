from datetime import date

from werkzeug.routing import BaseConverter

class DateConverter(BaseConverter):
    """
    URL parameter converter for ISO dates.
    """

    def to_python(self, value):
        return date.fromisoformat(value)

    def to_url(self, value):
        return date.isoformat(value)


def init_app(app):
    app.url_map.converters['date'] = DateConverter
