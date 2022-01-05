import calendar

from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for

from performance.authorization import edit_check
from performance.extensions import db

from ..models import AssumedBest

assumed_best_bp = Blueprint('assumed_best', __name__, template_folder='../templates')

@assumed_best_bp.context_processor
def context_processor():
    return dict(calendar=calendar)

@assumed_best_bp.route('/edit/',
    defaults={'year': None, 'month': None},
    methods=['GET', 'POST'])
@assumed_best_bp.route('/edit/<int:year>/<int:month>', methods=['GET', 'POST'])
@edit_check
def edit(year, month):
    # NOTE: wtforms-alchemy is too aggressive
    from ..forms import AssumedBestForm

    if year is None or month is None:
        assumed_best = None
    else:
        assumed_best = AssumedBest.query.filter(
            AssumedBest.year == year,
            AssumedBest.month == month,
        ).one_or_none()
    form = AssumedBestForm(obj=assumed_best)

    if form.validate_on_submit():
        # add if None
        if assumed_best is None:
            assumed_best = AssumedBest()
            db.session.add(assumed_best)
        # update
        assumed_best.year = year
        assumed_best.month = month
        form.populate_obj(assumed_best)
        db.session.commit()
        if hasattr(form, 'backurl') and form.backurl.data:
            return redirect(form.backurl.data)
        else:
            return redirect(url_for('select_date.goto_today'))

    context = dict(
        form = form,
    )
    return render_template('assumed_best/edit.html', **context)
