from flask import Blueprint
from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

# amazon/dhl shared
from performance.authorization import basic_check
from performance.authorization import development_only
from performance.authorization import edit_check
from performance.extensions import db
from performance.models import FlightType
from performance.views.pluggable import ModelView
from performance.views.pluggable import UpdateDeleteView

# dhl specific
from performance.dhl import randomdata
from performance.dhl.external_data.excel_schedule import import_flights
from performance.dhl.forms import ImportExcelScheduleForm
from performance.dhl.forms import ReportForm
from performance.dhl.models import Bound
from performance.dhl.models import Flight
from performance.dhl.models import Operation
from performance.dhl.models import Report
from performance.dhl.models import ScheduledReport

from .utils import convert_excel_schedule_flights
from .utils import grouped_flights
from .utils import sort_scheduled_flights_from_excel

report_bp = Blueprint('report', __name__, template_folder='templates')

@report_bp.route('/<int:id>')
@basic_check
def view(id):
    """
    View DHL Report object with links to edit if current_user is an editor.

    :param id: Report.id
    """
    report = Report.query.get_or_404(id)
    context = dict(
        report = report,
        grouped_flights = grouped_flights(report),
    )
    return render_template('report/printable.html', **context)

@report_bp.route('/edit/<int:id>/details/<attrname>', methods=['GET', 'POST'])
@edit_check
def edit_details(id, attrname):
    """
    Edit free form comments/details.

    :param id: Report.id
    :param attrname: name of one of the Report.details_attrs comment fields.
    """
    if attrname not in Report.details_attrs:
        abort(404)
    report = Report.query.get_or_404(id)
    form = ReportForm(obj=report)
    form.submit.label.text = 'Update'
    if form.validate_on_submit():
        setattr(report, attrname, getattr(getattr(form, attrname), 'data'))
        db.session.commit()
        return redirect(url_for('.view', id=id))
    context = dict(
        form = form,
    )
    return render_template('report/edit-details.html', **context)

@report_bp.route('/edit/performance-stats/<int:id>', methods=['GET', 'POST'])
@edit_check
def edit_performance_stats(id):
    """
    Crosstab performance stats one-page editor.

    :param id: Report.id
    """
    report = Report.query.get_or_404(id)
    form = ReportForm(obj=report)
    if form.validate_on_submit():
        if form.delete.data:
            db.session.delete(report)
        elif form.submit.data:
            form.populate_obj(report)
        db.session.commit()
        if hasattr(form, 'backurl') and form.backurl.data:
            return redirect(form.backurl.data)
    elif request.method == 'GET':
        form.submit.label.text = 'Update'
    context = dict(
        form = form,
        grouped = grouped_flights(report),
        report = report,
    )
    return render_template('report/edit-performance-stats.html', **context)

@report_bp.route('/edit/<int:id>/flights-by-category/<int:flight_type>/<int:bound>')
@edit_check
def edit_flights_by_category(id, flight_type, bound):
    """
    One page of edit links for one category of flights.

    :param id: Report.id
    :param flight_type: Flight.flight_type_id
    :param bound: Flight.bound_id
    """
    query = (
        Flight.query
        .join(Bound, Bound.id == Flight.bound_id)
        .join(FlightType, FlightType.id == Flight.flight_type_id)
        .join(Report, Report.id == Flight.report_id)
        .filter(
            Flight.bound_id == bound,
            Flight.flight_type_id == flight_type,
            Report.id == id,
        ).order_by(
            Bound.report_order,
            FlightType.report_order,
        )
    )
    context = dict(
        # queries executed here to avoid overwriting this namespace.
        report = Report.query.get_or_404(id),
        flight_type = FlightType.query.get_or_404(flight_type),
        bound = Bound.query.get_or_404(bound),
        flights = query.all(),
    )
    return render_template('report/flight-by-category.html', **context)

@report_bp.route('/prompt-new/<date:report_date>')
@edit_check
def prompt_new(report_date):
    """
    Prompt for new report with options to create or import.

    :param report_date: wanted date for new report.
    """
    # keep endpoint name the same as Amazon so that select_date will enter
    # here.
    context = {
        'report_date': report_date,
        'scheduled_reports': ScheduledReport.query.all(),
    }
    return render_template('report/prompt-new.html', **context)

@report_bp.route('/create-blank-report/<date:report_date>')
@edit_check
def create_report_blank(report_date):
    """
    Create a new blank report.

    :param report_date: wanted date for new, blank report.
    """
    report = Report(date=report_date)
    db.session.add(report)
    db.session.commit()
    return redirect(url_for('.view', id=report.id))

@report_bp.route('/import-excel-schedule/<date:report_date>', methods=['GET', 'POST'])
@edit_check
def import_excel_schedule(report_date):
    """
    Import Excel Schedule File

    :param report_date: wanted report date to import to.
    """
    form = ImportExcelScheduleForm()
    preview = None
    if form.validate_on_submit():
        file = request.files[form.excel_path.name]
        preview = import_flights(form.excel_path.data, report_date)
        # filter for weekday
        preview = [row for row in preview if report_date.weekday() in row['utc_dow']]
        if form.save.data:
            # User click "Import..." otherwise assume they clicked "Preview"
            # and let the value of `preview` fall through.
            flights = convert_excel_schedule_flights(preview)
            report = Report(date=report_date, flights=flights)
            db.session.add(report)
            db.session.commit()
            return redirect(url_for('.view', id=report.id))
        else:
            # "Preview"
            preview = sort_scheduled_flights_from_excel(preview)
    context = dict(
        form = form,
        preview = preview,
    )
    return render_template('report/import-excel-schedule.html', **context)

@report_bp.route('/create-random-report/<date:report_date>')
@edit_check
@development_only
def create_random_report(report_date):
    """
    Create random report.
    """
    report = randomdata.random_report(report_date)
    db.session.add(report)
    db.session.commit()
    return redirect(url_for('.view', id=report.id))

def trash():
    @report_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
    @edit_check
    def edit(id):
        report = Report.query.get_or_404(id)
        form = ReportForm(obj=report)
        if form.validate_on_submit():
            if form.delete.data:
                db.session.delete(report)
            elif form.submit.data:
                form.populate_obj(report)
            db.session.commit()
            if hasattr(form, 'backurl') and form.backurl.data:
                return redirect(form.backurl.data)
        elif request.method == 'GET':
            form.submit.label.text = 'Update'
        context = dict(
            form = form,
            grouped = grouped_flights(report),
            report = report,
        )
        return render_template('report/edit.html', **context)

