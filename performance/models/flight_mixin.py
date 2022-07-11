from ..extensions import db

class FlightMixin:
    """
    Columns shared by report flights and scheduled flights.
    """

    flight_number = db.Column(
        db.String,
        info = dict(
            label = 'Flight',
        ),
    )

    leg = db.Column(
        db.Integer,
        server_default = db.text('1'),
        info = dict(
            label = 'Leg',
        ),
    )

    tail_number = db.Column(
        db.String,
        info = dict(
            label = 'Tail',
        ),
    )

    weight = db.Column(
        db.Integer,
        info = dict(
            label = 'Weight',
        ),
    )

    comment = db.Column(
        db.Text,
        info = dict(
            label = 'Comment',
            render_kw = dict(
                cols = 80,
                rows = 8,
            ),
        ),
    )

    origin_station = db.Column(
        db.String,
        index = True,
        info = dict(
            label = 'Orig. Station',
        ),
    )
    origin_departure_estimated_date = db.Column(
        db.Date,
        info = dict(
            label = 'ETD',
            render_kw = dict(
                class_ = 'date-entry',
                placeholder = 'optional date',
            ),
        ),
    )
    origin_departure_estimated_time = db.Column(
        db.Time,
        info = dict(
            label = '',
            render_kw = dict(
                class_ = 'time-entry',
            ),
        ),
    )

    destination_station = db.Column(
        db.String,
        index = True,
        info = dict(
            label = 'Dest. Station',
        ),
    )
    destination_arrival_estimated_date = db.Column(
        db.Date,
        info = dict(
            label = 'ETA',
            render_kw = dict(
                class_ = 'date-entry',
            ),
        ),
    )
    destination_arrival_estimated_time = db.Column(
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
