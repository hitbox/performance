from ..extensions import db

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
