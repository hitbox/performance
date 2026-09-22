import csv
import gzip
import inspect
import os

from datetime import datetime
from pprint import pprint

import click

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from sqlalchemy.dialects import oracle as oracle_dialect

from performance import business
from performance import models
from performance import queries
from performance import settings
from performance.authorization import basic_check
from performance.authorization import edit_check
from performance.extensions import db
from performance.forms import ChangesForm
from performance.forms import QueryParametersForm
from performance.forms import ResultsForm
from performance.html import highlighted_sql
from performance.utils import is_gzip_file

external_bp = Blueprint('external', __name__)

@external_bp.route('/update/<int:report_id>/help', methods=['GET', 'POST'])
@basic_check
def update_report_from_external_help(report_id):
    """
    Helpful information about how the update from external works.
    """
    context = dict(
        kg_conversion_factor = settings.kilogram_conversion_factor(),
        report_id = report_id,
    )
    return render_template('report/import-changes-help.html', **context)

@external_bp.route('/update/<int:report_id>', methods=['GET', 'POST'])
@basic_check
def update_report_from_external(report_id):
    """
    Import external data and match up against this report by id. GET requests
    are used to present user with a form to query the database. POST is used to
    submit a form with selected updates for differences between external
    database and this one.
    """
    report = db.get_or_404(models.Report, report_id)

    results_form = None
    if request.method == 'POST':
        # POST for final import of results
        results_form = ChangesForm(formdata=request.form)
        if results_form.validate():
            # result form is valid
            if results_form.clear.data:
                # user clicked to clear results form
                url = url_for(request.endpoint, report_id=report_id)
                return redirect(url)
            else:
                # user clicked to apply changes
                flight_changes = results_form.data['flight_changes']
                business.external.update_from_flight_changes(flight_changes)
                db.session.commit()
                return redirect(url_for('report.view_report', id=report.id))

    param_form = QueryParametersForm(data=request.args)
    javascript_injection = {}
    context = {}
    if (
        param_form.submit.name in request.args
        and
        results_form is None
    ):
        # user clicked to query external database
        # only create results_form if it has not already been created
        # it may have been created and failed validation
        flight_changes = business.external.get_flight_changes(report.date)

        results_form = ChangesForm(
            data = {
                'flight_changes': flight_changes,
            },
        )
        # push an anchor to javascript
        javascript_injection['anchor'] = 'updates'
        # hide query parameters form
        param_form = None

    if results_form and not results_form.flight_changes:
        del results_form.submit

    context.update({
        'javascript_injection': javascript_injection,
        'kg_conversion_factor': settings.kilogram_conversion_factor(),
        'param_form': param_form,
        'report': report,
        'results_form': results_form,
        'show_param_form_title': False,
    })

    if settings.show_external_query_results():
        # Add external query results list to context.
        results = business.external.external_results(report.date).mappings().all()
        context.update({
            'external_query_results': results,
        })

    if settings.show_external_query_statement():
        # Add compiled, highlighted, external sql to context.
        stmt = queries.get_external_stmt(report.date)
        compiled = stmt.compile(
            dialect = oracle_dialect.dialect(),
            compile_kwargs = {
                'literal_binds': True,
            },
        )
        sql_html = highlighted_sql(compiled)
        context.update({
            'external_flights_stmt': sql_html,
        })

    return render_template('report/import-changes.html', **context)

@external_bp.route('/new/<date:report_date>', methods=['GET', 'POST'])
@edit_check
def import_for_new(report_date):
    """
    Create a new report from the external database.
    """
    if not settings.external_import():
        abort(404)

    if request.method == 'POST':
        results_form = ResultsForm(formdata=request.form)
        if results_form.validate():
            report = business.external.new_report_from_external(
                report_date,
                results_form.data,
            )
            db.session.add(report)
            db.session.commit()
            return redirect(url_for('report.view_report_for_date', report_date=report_date))

    param_form = QueryParametersForm(data=request.args)
    # remove field that makes no sense here
    del param_form.show_all_fields
    if param_form.clear.data:
        # TODO
        # - moved clear to the result form
        # - remove this
        # redirect to clear query args
        return redirect(url_for(request.endpoint, report_date=report_date))

    if param_form.submit.name in request.args:
        # The user has submitted GET method of the query form.
        results = business.external.external_results(report_date).mappings()
        results_form = ResultsForm(data=dict(rows=results))
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

@external_bp.cli.command('query')
@click.argument('report_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option(
    '--changes/--no-changes',
    default = True,
    show_default = True,
    help = 'Show changes against internal flights.',
)
@click.option(
    '--print-query/--no-print-query',
)
def query(report_date, changes, print_query):
    """
    Display the results of the external query for a given report date.
    """
    report_date = report_date.date()
    if print_query:
        engine = db.get_engine(bind='schedops')
        external_query = queries.get_external_stmt(report_date)
        compiled_query = external_query.compile(
            dialect = engine.dialect,
            compile_kwargs = {"literal_binds": True}
        )
        print(compiled_query)
        return

    data = business.external.joined_external_flights(report_date)
    if changes:
        data = business.external.make_diffs(report_date, data)
    pprint(data)

@external_bp.cli.command('load')
@click.argument('file', type=click.File('r'))
@click.argument('class_')
@click.option(
    '--lower-keys/--no-lower-keys',
    default = True,
    show_default = True,
    help = 'Lower case the keys.',
)
@click.option(
    '--ignore-unknown/--no-ignore-unknown',
    default = True,
    show_default = True,
    help = 'Ignore the keys from CSV that the mapper doesn\'t take.',
)
@click.option(
    '--commit/--no--commit',
    help = 'Commit added instances.',
)
@click.option(
    '--compressed/--no--compressed',
    default = None,
    help = 'Read from compressed gzip files.',
)
def load(file, class_, lower_keys, ignore_unknown, commit, compressed):
    """
    Load data from CSV.

    :param file: path to file.
    :param class_: Database model class name.
    """
    if compressed is None:
        compressed = is_gzip_file(file.name)

    if compressed:
        file = gzip.open(file.name, 'rt', encoding='utf8', newline='')

    model = getattr(models, class_, None)
    if model is None:
        raise ValueError(f'Model class name {class_} not found.')

    engine = db.engines['schedops']
    model.__table__.create(bind=engine, checkfirst=True)
    coerce = None
    for data in csv.DictReader(file):
        if lower_keys:
            data = {k.lower(): v for k, v in data.items()}
        if ignore_unknown:
            data = {k: v for k, v in data.items() if k in model.__mapper__.columns}

        if coerce is None:
            coerce = {}
            for key in data:
                attr = getattr(model, key)
                python_type = attr.type.python_type
                if python_type is datetime:
                    python_type = datetime.fromisoformat
                coerce[key] = python_type

        instance = model()
        for key, string_value in data.items():
            try:
                value = coerce[key](string_value)
            except (TypeError, ValueError):
                # TODO
                # - optional None for type conversion failure?
                value = None
            setattr(instance, key, value)
        db.session.add(instance)

    if commit:
        db.session.commit()

def get_external_models():
    return [
        cls for name, cls in inspect.getmembers(models.external)
        if inspect.isclass(cls) and hasattr(cls, '__table__')
    ]

@external_bp.cli.command('dump')
@click.argument('output', type=click.Path(file_okay=False, dir_okay=True, exists=True))
@click.option('--compress/--no-compress', default=True)
def dump(output, compress):
    """
    Dump external tables' data.

    output: OUTPUT directory for CSVs.
    """
    external_models = get_external_models()

    if compress:
        open_func = gzip.open
        open_mode = 'wt'
    else:
        open_func = open
        open_mode = 'w'

    for model in external_models:
        filename = os.path.join(output, f'{model.__tablename__}.csv')
        if compress:
            filename += '.gz'

        columns = [c.name for c in model.__table__.columns]
        objects = db.session.scalars(db.select(model))

        with open_func(filename, open_mode, newline='', encoding='utf8') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(columns)
            for obj in objects:
                writer.writerow([getattr(obj, col) for col in columns])
