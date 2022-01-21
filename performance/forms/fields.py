from wtforms import Field
from wtforms.widgets import TextInput
from wtforms_components import TimeField

from .. import parse
from ..utils import massage_time

class StringTimeField(TimeField):
    """
    String input time field that automatically inserts the colon
    """
    # browser time inputs are unsatisfactory
    widget = TextInput()

    def process_formdata(self, valuelist):
        """
        Allow four digits number interpretation as time.
        """
        if valuelist:
            # doing this like wtforms TimeField
            time_str = ' '.join(valuelist)
            try:
                time_str = massage_time(time_str)
            except ValueError:
                pass
            else:
                # insert the implicit colon and update list for super
                time_str = f'{time_str[:2]}:{time_str[2:]}'
                valuelist[0] = time_str
        super().process_formdata(valuelist)


class PercentField(Field):
    """
    Allow user to enter percent values in a whole number.
    """
    widget = TextInput()

    def _value(self):
        if self.data:
            return f'{self.data*100:.2f}'
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = float(valuelist[0])/100
        else:
            self.data = float()


class DelayCodesField(Field):
    """
    Delay codes field.
    """
    widget = TextInput()

    def _value(self):
        if self.data:
            return parse.formatdelays(self.data)
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = parse.delaystring(valuelist[0])
        else:
            self.data = []
