from ..extensions import db

from .mixin import UniqueMixin

class Delay(db.Model, UniqueMixin):
    """
    A flight delay with a code and, optionally, minutes and whether it was cancelled.
    """

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String, nullable=False)

    is_controllable = db.Column(
        db.Boolean,
        nullable = False,
        default = False,
        server_default = 'false',
        doc = 'Is controllable delay.'
    )

    is_cancelled_lane = db.Column(
        db.Boolean,
        nullable = False,
        default = False,
        server_default = 'false',
        doc = 'Delay code counts as a lane even if cancelled.',
    )

    is_always_show = db.Column(
        db.Boolean,
        nullable = False,
        default = False,
        server_default = 'false',
        doc = 'Override hiding for LATE_GT threshold.',
    )

    @classmethod
    def unique_hash(cls, code):
        return code

    @classmethod
    def unique_filter(cls, query, code):
        return query.filter(cls.code == code)

    @db.validates('code')
    def uppercase(self, key, value):
        """
        Make code uppercase.
        """
        if isinstance(value, str):
            value = value.upper()
        return value
