from ..extensions import db

class MetaMixin:

    created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())


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
        return query.paginate()


class UniqueMixin:

    @classmethod
    def unique_hash(cls, *args, **kwargs):
        """
        Return the hash value used for caching and avoid database hits.
        """
        raise NotImplementedError

    @classmethod
    def unique_filter(cls, query, *args, **kwargs):
        """
        Fixup query to lookup instance from database.
        """
        raise NotImplementedError

    @classmethod
    def as_unique(cls, session, *args, **kwargs):
        return unique(
            session = session,
            cls = cls,
            hashfunc = cls.unique_hash,
            queryfunc = cls.unique_filter,
            constructor = cls,
            args = args,
            kwargs = kwargs
        )


def unique(session, cls, hashfunc, queryfunc, constructor, args, kwargs):
    """
    Return a cached instance if possible. If not, then from database. Finally,
    by creator if necessary.
    """
    # https://github.com/sqlalchemy/sqlalchemy/wiki/UniqueObject
    cache = getattr(session, '_unique_cache', None)
    if cache is None:
        session._unique_cache = {}
        cache = session._unique_cache

    key = (cls, hashfunc(*args, **kwargs))

    if key not in cache:
        with session.no_autoflush:
            query = session.query(cls)
            query = queryfunc(query, *args, **kwargs)
            instance = query.first()
            if not instance:
                instance = constructor(*args, **kwargs)
                session.add(instance)
        cache[key] = instance

    return cache[key]
