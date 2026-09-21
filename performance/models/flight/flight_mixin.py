import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from performance.extensions import db

class FlightMixin:
    """
    Columns shared by report flights and scheduled flights.
    """

    @db.declared_attr
    def flight_number(cls):
        return db.Column(
            db.String,
            info = dict(
                label = 'Flight',
            ),
        )

    @hybrid_property
    def normalized_flight_number(self):
        """
        Flight numebr as string, removing leading zeros.
        """
        if self.flight_number:
            try:
                return str(int(self.flight_number))
            except ValueError:
                return self.flight_number

    @hybrid_property
    def flight_number_as_integer(self):
        if self.flight_number:
            try:
                return int(self.flight_number)
            except ValueError:
                return self.flight_number

    @flight_number_as_integer.expression
    def flight_number_as_integer(cls):
        column = cls.flight_number
        expr = db.case(
            (
                column.regexp_match(r'^[0-9]+$'),
                db.func.cast(column, db.Integer)
            ),
        )
        return expr

    @db.declared_attr
    def leg(cls):
        return db.Column(
            db.Integer,
            server_default = db.text('1'),
            info = dict(
                label = 'Leg',
            ),
        )

    @db.declared_attr
    def tail_number(cls):
        return db.Column(
            db.String,
            info = dict(
                label = 'Tail',
            ),
        )

    @db.declared_attr
    def weight(cls):
        return db.Column(
            db.Integer,
            info = dict(
                label = 'Weight',
            ),
        )

    @db.declared_attr
    def comment(cls):
        return db.Column(
            db.Text,
            info = dict(
                label = 'Comment',
                render_kw = dict(
                    cols = 80,
                    rows = 8,
                ),
            ),
        )

    @db.declared_attr
    def origin_station(cls):
        return db.Column(
            db.String,
            index = True,
            info = dict(
                label = 'Orig. Station',
            ),
        )

    @db.declared_attr
    def origin_departure_estimated_date(cls):
        return db.Column(
            db.Date,
            info = dict(
                label = 'ETD',
                render_kw = dict(
                    class_ = 'date-entry',
                    placeholder = 'optional date',
                ),
            ),
        )

    @db.declared_attr
    def origin_departure_estimated_time(cls):
        return db.Column(
            db.Time,
            info = dict(
                label = '',
                render_kw = dict(
                    class_ = 'time-entry',
                ),
            ),
        )

    @hybrid_property
    def origin_departure_estimated_time_or_midnight(self):
        if self.origin_departure_estimated_time:
            return self.origin_departure_estimated_time
        else:
            return datetime.time(0,0)

    @origin_departure_estimated_time_or_midnight.expression
    def origin_departure_estimated_time_or_midnight(cls):
        expr = db.func.coalesce(
            cls.origin_departure_estimated_time,
            datetime.time(0,0),
        )
        return expr

    @db.declared_attr
    def destination_station(cls):
        return db.Column(
            db.String,
            index = True,
            info = dict(
                label = 'Dest. Station',
            ),
        )

    @db.declared_attr
    def destination_arrival_estimated_date(cls):
        return db.Column(
            db.Date,
            info = dict(
                label = 'ETA',
                render_kw = dict(
                    class_ = 'date-entry',
                ),
            ),
        )

    @db.declared_attr
    def destination_arrival_estimated_time(cls):
        return db.Column(
            db.Time,
            info = dict(
                label = '',
                render_kw = dict(
                    class_ = 'time-entry',
                ),
            ),
        )

    @db.validates('tail_number', 'origin_station', 'destination_station')
    def uppercase(self, key, value):
        """
        Ensure fields are uppercase.
        """
        if isinstance(value, str):
            value = value.upper()
        return value
