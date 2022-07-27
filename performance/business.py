from . import queries

def performance_contract_for_date(date):
    """
    Return the performance contract for a (report) date.
    """
    query = queries.performance_contract_query(date)
    contract = query.first()
    return contract

def performance_details(date, contract=None):
    """
    Return performance numbers.

    :param reports: list of reports.
    """
    daily_criteria = queries.date_criteria(date)
    mtd_criteria = queries.month_to_date_criteria(date)
    qtd_criteria = queries.quarter_to_date_criteria(date)

    result = dict()
    keys = ['daily', 'month_to_date', 'quarter_to_date']
    criterias = [daily_criteria, mtd_criteria, qtd_criteria]
    for key, criteria in zip(keys, criterias):
        subdict = result[key] = dict()
        subdict['lanes'] = queries.lanes(criteria).count()
        subdict['flights_with_controllable_destination_delays_over15'] = (
            queries.flights_with_controllable_destination_delays(criteria, 15).count()
        )
        subdict['flights_with_controllable_destination_delays_over30'] = (
            queries.flights_with_controllable_destination_delays(criteria, 30).count()
        )

    if contract:
        criteria = queries.contract_range_criteria(date, contract)
        subdict = result['contract_range'] = dict()
        subdict['lanes'] = queries.lanes(criteria).count()
        subdict['flights_with_controllable_destination_delays_over15'] = (
            queries.flights_with_controllable_destination_delays(criteria, 15).count()
        )

    return result
