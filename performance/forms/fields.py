from wtforms import Field
from wtforms import HiddenField
from wtforms import IntegerField
from wtforms.validators import ValidationError
from wtforms.widgets import HiddenInput
from wtforms.widgets import TextInput
from wtforms_components import TimeField

from performance import models
from performance import parse
from performance.utils import massage_time

class HiddenIntegerField(HiddenField):

    def pre_validate(form):
        try:
            int(self.data)
        except ValueError:
            raise ValidationError('Field must be an integer')


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


class HiddenIntegerField(IntegerField):
    widget = HiddenInput()
