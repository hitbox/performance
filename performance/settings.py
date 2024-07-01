from flask import current_app

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
    key = 'PERFORMANCE_CONTRACTS_USE_DATE_RANGE'
    return current_app.config.get(key, False)

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
