from ..extensions import db

from .mixin import AppContextMixin
from .mixin import UniqueMixin

class Delay(
    AppContextMixin,
    UniqueMixin,
    db.Model,
):
    """
    A flight delay with a code and, optionally, minutes and whether it was cancelled.
    """
    class Meta:
        # see AppContextMixin.noapp_pagination
        order_by = 'code'
        paginate_kw = dict(
            per_page = 100,
        )

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String, nullable=False, unique=True)

    description = db.Column(db.String)

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

    as_origin_delay = db.relationship(
        'OriginDelay',
        back_populates = 'delay',
    )

    as_destination_delay = db.relationship(
        'DestinationDelay',
        back_populates = 'delay',
    )

    @classmethod
    def unique_hash(cls, *, code):
        return (code.upper(), )

    @classmethod
    def unique_filter(cls, query, *, code):
        return query.filter(
            db.func.upper(cls.code) == db.func.upper(code)
        )

    @db.validates('code')
    def uppercase(self, key, value):
        """
        Make code uppercase.
        """
        if isinstance(value, str):
            value = value.upper()
        return value
