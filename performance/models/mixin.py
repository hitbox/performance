from markupsafe import Markup

from ..extensions import db

class MetaMixin:
    """
    Common attributes for all models.
    """

    @db.declared_attr
    def created(cls):
        return db.Column(
            db.DateTime(timezone = True),
            server_default = db.func.now()
        )

    @db.declared_attr
    def updated(cls):
        return db.Column(
            db.DateTime(timezone = True),
            onupdate = db.func.now()
        )


class AppContextMixin:
    """
    Provide callables for import-time use that do not require application context.
    """

    @classmethod
    def noapp_get_or_404(cls, identity, description=None):
        return cls.query.get_or_404(identity, description)

    @classmethod
    def noapp_pagination(cls):
        query = cls.query
        if hasattr(cls, 'Meta') and hasattr(cls.Meta, 'order_by'):
            attr = getattr(cls, cls.Meta.order_by)
            query = query.order_by(attr)
        # keyword args for paginate
        paginate_kw = {}
        if hasattr(cls, 'Meta'):
            paginate_kw = getattr(cls.Meta, 'paginate_kw', {})
        return query.paginate(**paginate_kw)


class UniqueMixin:

    @classmethod
    def unique_hash(cls, **kwargs):
        """
        Return the hash value used for caching and avoid database hits.
        """
        raise NotImplementedError

    @classmethod
    def unique_filter(cls, query, **kwargs):
        """
        Fixup query to lookup instance from database.
        """
        raise NotImplementedError

    @classmethod
    def as_unique(cls, session, **kwargs):
        return unique(
            session = session,
            cls = cls,
            unique_hash = cls.unique_hash,
            unique_filter = cls.unique_filter,
            constructor = cls,
            **kwargs,
        )


class VisibilityMixin:
    """
    Mixin options for whether to show or hide attributes.
    """

    @db.declared_attr
    def show_lanes(cls):
        return db.Column(
            db.Boolean,
            default = True,
            nullable = False,
            doc =
                'Show the daily, month-to-date, and quarter-to-date'
                ' number of lanes.',
            info = dict(
                form_label =  'Show lanes?',
            ),
        )

    @db.declared_attr
    def show_chargeable_delays(cls):
        return db.Column(
            db.Boolean,
            default = True,
            nullable = False,
            doc =
                'Show the daily, month-to-date, and quarter-to-date'
                ' number of chargeable delays.',
            info = dict(
                form_label = 'Show chargeable delays?',
            ),
        )

    @db.declared_attr
    def show_delays_gt_30_count(cls):
        return db.Column(
            db.Boolean,
            default = True,
            nullable = False,
            doc =
                'Show the daily, month-to-date, and quarter-to-date'
                ' number of delays over 30 minutes.',
            info = dict(
                form_label = 'Show delays > 30 count?',
            ),
        )

    @db.declared_attr
    def show_on_time_performance_gt_15(cls):
        return db.Column(
            db.Boolean,
            default = True,
            nullable = False,
            doc =
                'Show the daily, month-to-date, and quarter-to-date'
                ' on-time performance percentage over 15 minutes.',
            info = dict(
                form_label = 'Show on-time performance > 15?',
            ),
        )

    @db.declared_attr
    def show_on_time_performance_gt_30(cls):
        return db.Column(
            db.Boolean,
            default = True,
            nullable = False,
            doc =
                'Show the daily, month-to-date, and quarter-to-date'
                ' on-time performance percentage over 30 minutes.',
            info = dict(
                form_label = 'Show on-time performance > 30?',
            ),
        )

    @db.declared_attr
    def show_on_time_performance_gt_30(cls):
        return db.Column(
            db.Boolean,
            default = True,
            nullable = False,
            doc =
                'Show the daily, month-to-date, and quarter-to-date'
                ' on-time performance percentage over 30 minutes.',
            info = dict(
                form_label = 'Show on-time performance > 30?',
            ),
        )

    @db.declared_attr
    def show_flights_controllable_over_15(cls):
        return db.Column(
            db.Boolean,
            default = True,
            nullable = False,
            doc =
                'Show the controllable over 15 minutes count column'
                ' for flights.',
            info = dict(
                form_label = 'Show controllable > 15 column for flights?',
                table_header = Markup('&gt;&nbsp;15'),
            ),
        )

    @db.declared_attr
    def show_flights_controllable_over_30(cls):
        return db.Column(
            db.Boolean,
            default = True,
            nullable = False,
            doc =
                'Show the controllable over 30 minutes count column'
                ' for flights.',
            info = dict(
                form_label = 'Show controllable > 30 column for flights?',
                table_header = Markup('&gt;&nbsp;30'),
            ),
        )


def unique(
    *, # keyword only
    session,
    cls,
    unique_hash,
    unique_filter,
    constructor,
    **kwargs,
):
    """
    Return a cached instance if possible. If not, then from database. Finally,
    by creator if necessary.
    """
    # https://github.com/sqlalchemy/sqlalchemy/wiki/UniqueObject
    cache = getattr(session, '_unique_cache', None)
    if cache is None:
        session._unique_cache = {}
        cache = session._unique_cache

    key = (cls, unique_hash(**kwargs))

    if key not in cache:
        # update cache...
        with session.no_autoflush:
            # ...from database
            query = session.query(cls)
            query = unique_filter(query, **kwargs)
            instance = query.first()
            if not instance:
                # ...create new
                instance = constructor(**kwargs)
                session.add(instance)
        cache[key] = instance

    return cache[key]
