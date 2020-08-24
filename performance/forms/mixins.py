from flask import request
from wtforms import HiddenField
from wtforms import SubmitField

# this exists because of so many forms there were problems keep the field
# declarations consistent.

class BackLinkMixin:
    """
    Add hidden field to form to redirect back to.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'backurl' in request.args:
            self.backurl.data = request.args['backurl']

    backurl = HiddenField()


class DeleteMixin:

    delete = SubmitField('Delete', render_kw=dict(class_='danger'))


class SearchCriteriaMixin:

    def search_criteria(self, model_class):
        """
        Return list of criteria of startswith searches, using SQL LIKE.
        """
        criteria = []
        for field in self:
            if field.type not in ('SubmitField', ):
                criteria.append(getattr(model_class, field.name).ilike(f'{field.data}%'))
        return criteria


class SubmitMixin:

    submit = SubmitField('Create')


class SubmitUpdateDeleteMixin(
    # order matters for button order
    DeleteMixin,
    SubmitMixin,
):
    """
    Add submit and delete buttons. Views handle changing text like 'Create' to 'Update'.
    """
