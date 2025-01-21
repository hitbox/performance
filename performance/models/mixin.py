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
