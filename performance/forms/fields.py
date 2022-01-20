from wtforms import Field
from wtforms.widgets import TextInput
from wtforms_components import TimeField

from .. import parse

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
        if (valuelist and len(valuelist[0]) == 4 and valuelist[0].isnumeric()):
            # insert the implicit colon
            s = valuelist[0]
            valuelist[0] = f'{s[:2]}:{s[2:]}'
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
