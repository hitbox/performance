from flask import request
from wtforms import HiddenField
from wtforms import SubmitField

from ..utils import get_thisurl

# this exists because of so many forms there were problems keep the field
# declarations consistent.

class BackLinkMixin:
    """
    Add hidden field to form to redirect back to.
    """

    backurl = HiddenField(
        default = lambda: request.args.get('backurl', get_thisurl()),
    )


class DeleteMixin:

    delete = SubmitField(
        'Delete',
        render_kw = dict(
            class_ = 'danger',
            tabindex = '-1',
        )
    )

    delete_url = HiddenField()


class SubmitMixin:
    """
    Mixin a standard attribute name for a submit button.
    """

    submit = SubmitField()


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


class SubmitUpdateDeleteMixin(
    # order matters for button order
    DeleteMixin,
    SubmitMixin,
):
    """
    Add submit and delete buttons. Views handle changing text like 'Create' to 'Update'.
    """
