from wtforms.widgets import TextInput
from wtforms_components import TimeField

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
