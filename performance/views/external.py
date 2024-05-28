import datetime

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from performance import business
from performance import forms
from performance import models
from performance import settings
from performance.authorization import basic_check
from performance.authorization import edit_check
from performance.extensions import db

external_bp = Blueprint('external', __name__)

@external_bp.route('/update/<int:report_id>', methods=['GET', 'POST'])
@basic_check
def update_report_from_external(report_id):
    """
    Import external data and match up against this report by id. GET requests
    are used to present user with a form to query the database. POST is used to
    submit a form with selected updates for differences between external
    database and this one.
    """
    report = models.Report.query.get_or_404(report_id)

    param_form = None
    results_form = None
    # XXX
    # - two forms is really hard to manage
    # - maybe just one form with the query params *and* results
    # - and then detect which button pressed

    if request.method == 'POST':
        # POST submit is only for doing final import of results
        results_form = forms.ChangesForm(formdata=request.form)
        if results_form.validate():
            business.update_report_from_external(results_form.data)
            return redirect(url_for('report.view_report', id=report.id))

    param_form = forms.QueryParametersForm(data=request.args)
    if param_form.clear.data:
        # redirect to clear query arguments
        return redirect(url_for(request.endpoint, report_id=report.id))

    if param_form.submit.name not in request.args:
        # initial page load, no query yet, remove clear button
        del param_form.clear
    elif results_form is None:
        # only create results_form if it has not already been created
        # it may have been created and failed validation
        # user clicked to query external database
        results = business.external_results(report.date)
        changes = list(
            business.get_changes_for_report_from_external(report, results)
        )
        results_form = forms.ChangesForm(
            data = dict(
                flight_changes = changes,
            ),
        )

    context = dict(
        kg_conversion_factor = settings.kilogram_conversion_factor(),
        param_form = param_form,
        report = report,
        results_form = results_form,
    )
    return render_template('report/import-changes.html', **context)

@external_bp.route('/new/<date:report_date>', methods=['GET', 'POST'])
@edit_check
def import_for_new(report_date):
    """
    Import flight data from external database and create a new report with it.
    """
    if not settings.external_import():
        abort(404)

    if request.method == 'POST':
        results_form = forms.ResultsForm(formdata=request.form)
        if results_form.validate():
            report = business.new_report_from_external(
                report_date,
                results_form.data,
            )
            db.session.add(report)
            db.session.commit()
            return redirect(url_for('report.view_report_for_date', report_date=report_date))

    param_form = forms.QueryParametersForm(data=request.args)
    # remove field that makes no sense here
    del param_form.show_all_fields
    if param_form.clear.data:
        # redirect to clear query args
        return redirect(url_for(request.endpoint, report_date=report_date))

    if param_form.submit.name in request.args:
        results = business.external_results(report_date).mappings()
        results_form = forms.ResultsForm(data=dict(rows=results))
    else:
        del param_form.clear
        results = None
        results_form = None

    context = dict(
        results = results,
        param_form = param_form,
        kg_conversion_factor = settings.kilogram_conversion_factor(),
        results_form = results_form,
    )
    template = 'report/prompt-new-external.html'
    return render_template(template, **context)
