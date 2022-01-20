import sqlalchemy as sa

from . import parse

class DelayCodesType(sa.types.TypeDecorator):
    """
    Zero or more delay codes and their, optional, minutes. By default stored as string.
    """
    impl = sa.String

    def process_bind_param(self, value, dialect):
        """
        Format delay code objects into a string.
        """
        delays_string = parse.formatdelays(value)
        return delays_string

    def process_result_value(self, value, dialect):
        """
        Parse delay codes string into objects.
        """
        delay_objects = parse.delaystring(value)
        return delay_objects
