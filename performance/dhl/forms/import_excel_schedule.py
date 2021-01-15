from flask_wtf.file import FileField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms.validators import DataRequired

from performance.forms.base import BaseFlaskForm

class ImportExcelScheduleForm(BaseFlaskForm):

    excel_path = FileField('Excel schedule file', validators=[DataRequired()])

    save = SubmitField('Import...')
    preview = SubmitField('Preview')
