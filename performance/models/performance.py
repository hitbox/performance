from performance.extensions import db

class Performance(db.Model):
    """
    Performance web app metadata.
    """

    id = db.Column(db.Integer, primary_key=True)

    default_flight_type_id = db.Column(
        db.ForeignKey('flight_type.id'),
        doc = 'Default flight type for new scheduled flights.',
    )

    default_flight_type = db.relationship(
        'FlightType',
    )
