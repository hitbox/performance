import datetime

from decimal import Decimal
from types import SimpleNamespace

import click
import sqlalchemy as sa

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
from performance.forms import ReportForm

report_bp = Blueprint('report', __name__)

@report_bp.context_processor
def context_processor():
    return dict(
        Decimal = Decimal,
    )

def get_report_form_class():
    """
    Wrap in function to avoid the aggressiveness of wtforms_alchemy.
    """
    from performance.forms import ReportForm
    return ReportForm

def get_context(report):
    """
    Context data for viewing report.
    """
    context = dict(report=report)

    contract = business.summary.performance_contract_for_date(report.date)
    context['contract'] = contract

    context['controllable_delay_codes'] = models.Delay.query.filter(
        models.Delay.is_controllable,
    ).order_by(
        models.Delay.code,
    ).all()

    context.update(business.summary.performance_summary(report.date, contract))
    return context

def get_prev_next_context(report_date):
    return dict(
        prev_date = report_date - datetime.timedelta(days=1),
        next_date = report_date + datetime.timedelta(days=1),
    )

@report_bp.route('/<date:report_date>')
@basic_check
def view_report_for_date(report_date):
    """
    Redirect from report date to id.
    """
    report = models.Report.query.filter(models.Report.date == report_date).one_or_none()

    if report is None:
        # Alert and redirect to new report
        date_str = report_date.strftime(settings.datefmt())
        return redirect(url_for('.prompt_new', report_date=report_date))

    return redirect(url_for('.view_report', id=report.id))

@report_bp.route('/<int:id>', methods=['GET', 'POST'])
@basic_check
def view_report(id):
    """
    View Report object.
    """
    #ReportForm = get_report_form_class()
    report = models.Report.query.get_or_404(id)
    form = ReportForm(obj=report)

    # only updating the comments (system detail)
    form.submit.label.text = 'Update System Detail'
    if form.validate_on_submit():
        report.system_detail = form.system_detail.data
        db.session.commit()
        response = redirect(
            url_for(
                request.endpoint,
                _anchor = 'system-detail',
                **request.view_args
            )
        )
        return response

    context = get_context(report)
    context.update(get_prev_next_context(report.date))
    context.setdefault('form', form)
    context['performance_stats'] = current_app.config['PERFORMANCE_STATS']
    return render_template('report/print-with-edit.html', **context)

@report_bp.route('/delete/<int:report_id>')
@edit_check
def delete_report(report_id):
    """
    Delete Report
    """
    # confirm through javascript baked into template
    report = models.Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    return redirect(url_for('select_date.goto_today'))

@report_bp.route('/create_from_schedule/<date:report_date>/<schedule_id>')
@edit_check
def create_report_from_schedule(report_date, schedule_id):
    """
    Create new report from scheduled report.
    """
    scheduled_report = models.ScheduledReport.query.get_or_404(schedule_id)
    report = scheduled_report.as_report(report_date)
    db.session.add(report)
    db.session.commit()
    return redirect(url_for('.view_report', id=report.id))

@report_bp.route('/create_blank_report/<date:report_date>')
@edit_check
def create_report_blank(report_date):
    """
    Create a new blank report.
    """
    report = models.Report(date=report_date)
    db.session.add(report)
    db.session.commit()
    return redirect(url_for('.view_report', id=report.id))

@report_bp.route('/new/<date:report_date>')
@edit_check
def prompt_new(report_date):
    """
    Prompt to create new report.
    """
    if settings.scheduled_reports_onlyone():
        scheduled_report = models.ScheduledReport.query.one()
        context = dict(
            scheduled_report = scheduled_report
        )
    else:
        # all scheduled reports
        scheduled_reports = models.ScheduledReport.query.order_by(
                models.ScheduledReport.display_order
            ).all()
        context = dict(
            scheduled_reports = scheduled_reports,
        )

    context['report_date'] = report_date
    context.update(get_prev_next_context(report_date))
    template = 'report/prompt-new.html'
    return render_template(template, **context)

@report_bp.cli.command('performance_summary')
@click.argument('start', type=click.DateTime(['%Y-%m-%d']))
@click.argument('end', type=click.DateTime(['%Y-%m-%d']))
def performance_summary(start, end):
    """
    Performance summary for the command line.
    """
    start = start.date()
    end = end.date()
    date_criteria = models.Report.date.between(start, end)
    lanes = business.summary.performance_summary(date_criteria, '')
    print(lanes)
