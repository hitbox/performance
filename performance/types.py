from enum import Enum

import sqlalchemy as sa

from sqlalchemy.sql import operators

from . import parse

class DelayType(Enum):
    """
    Flight delay applies to origin or destination.
    """
    origin = 1
    destination = 2


class DelayCodesType(sa.types.TypeDecorator):
    # XXX: REMOVE?
    """
    Zero or more delay codes and their, optional, minutes. By default stored as string.
    """
    impl = sa.String

    # False until it is known to be safe. disables warning for now.
    cache_ok = False

    def process_bind_param(self, value, dialect):
        """
        Format delay code objects into a string.
        """
        if value is not None:
            if not isinstance(value, str):
                value = parse.formatdelays(value)
        return value

    def process_result_value(self, value, dialect):
        """
        Parse delay codes string into objects.
        """
        if value is not None:
            value = parse.delaystring(value)
        return value
