from types import SimpleNamespace

from flask import current_app

from . import constants

def config_as_obj():
    ns = SimpleNamespace(**current_app.config)
    return ns

def contracts_use_date_range():
    # XXX
    # - not sure what this is anymore
    # - all the contracts should use date ranges
    # - existing production config explicitly set this to false in one place,
    #   for dhl operations
    # - so this is always false as it is now?
    # - macro render_arrival_performance_contract_tier_table is really weird.
    #   it fallsback to this default *AND* it defaults, if not defined, to
    #   true.
    key = constants.PERFORMANCE_CONTRACTS_USE_DATE_RANGE
    return current_app.config.get(key, False)

def datefmt():
    """
    Python side access to date format. Templates just use config context
    variable.
    """
    key = constants.DATEFMT
    return current_app.config.get(key, '%Y-%m-%d')

def timefmt():
    """
    Python side access to time format. Templates just use config context
    variable.
    """
    key = constants.TIMEFMT
    return current_app.config.get(key, '%H:%M')

def external_import():
    """
    Enable external importing for new reports.
    """
    key = constants.PERFORMANCE_EXTERNAL_IMPORT
    return current_app.config.get(key, False)

def external_update():
    """
    Enable external update existing report.
    """
    key = constants.PERFORMANCE_EXTERNAL_UPDATE
    return current_app.config.get(key, False)

def external_fn_carrier():
    """
    Query value required for external importing.
    """
    key = constants.PERFORMANCE_EXTERNAL_QUERY_CARRIER
    return current_app.config[key]

def external_usage():
    """
    Query value for external importing. See
    performance.models.external:LegPax.usage
    """
    key = constants.PERFORMANCE_EXTERNAL_QUERY_USAGE
    return current_app.config[key]

def kilogram_conversion_factor():
    """
    Conversion factor taking lbs to kg.
    """
    key = constants.KG_CONVERSION_FACTOR
    return current_app.config[key]

def scheduled_reports_onlyone():
    """
    Enforce at the app level, only one scheduled report.
    """
    key = constants.SCHEDULED_REPORTS_ONLYONE
    return current_app.config.get(key, False)

def performance_report_title():
    key = constants.PERFORMANCE_REPORT_TITLE
    return current_app.config.get(key, False)
