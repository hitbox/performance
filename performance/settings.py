from flask import current_app

def datefmt():
    key = 'DATEFMT'
    return current_app.config.get(key, '%Y-%m-%d')

def external_import():
    key = 'PERFORMANCE_EXTERNAL_IMPORT'
    return current_app.config.get(key, False)

def external_fn_carrier():
    key = 'PERFORMANCE_EXTERNAL_QUERY_CARRIER'
    return current_app.config[key]

def external_usage():
    key = 'PERFORMANCE_EXTERNAL_QUERY_USAGE'
    return current_app.config[key]

def kilogram_conversion_factor():
    key = 'KG_CONVERSION_FACTOR'
    return current_app.config[key]

def scheduled_reports_onlyone():
    """
    Enforce at the app level, only one scheduled report.
    """
    key = 'SCHEDULED_REPORTS_ONLYONE'
    return current_app.config.get(key, False)
