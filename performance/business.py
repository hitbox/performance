from .models import Contract

def performance_contract_for_report(report):
    """
    The first contract object where the report date is between the contract's
    date range.
    """
    contract = Contract.query.filter(
        Contract.date_range_start <= report.date,
        Contract.date_range_end >= report.date,
    ).first()
    return contract

def performance_details(reports):
    """
    Return performance numbers (lanes, chargeable delays, and over-30 count).

    :param reports: list of reports.
    """
    lanes = [flight for report in reports for flight in report.lane_flights()]
    controllable_destination_delays_over15 = [
        delay
        for report in reports
        for delay
        in report.controllable_destination_delays(over_minutes=15)
    ]
    controllable_destination_delays_over30 = [
        delay
        for report in reports
        for delay
        in report.controllable_destination_delays(over_minutes=30)
    ]
    flights_with_controllable_destination_delays_over15 = [
        flight
        for report in reports
        for flight
        in report.flights_with_controllable_destination_delays(over_minutes=15)
    ]
    flights_with_controllable_destination_delays_over30 = [
        flight
        for report in reports
        for flight
        in report.flights_with_controllable_destination_delays(over_minutes=30)
    ]
    result = dict(
        lanes = lanes,
        controllable_destination_delays_over15
            = controllable_destination_delays_over15,
        controllable_destination_delays_over30
            = controllable_destination_delays_over30,
        flights_with_controllable_destination_delays_over15
            = flights_with_controllable_destination_delays_over15,
        flights_with_controllable_destination_delays_over30
            = flights_with_controllable_destination_delays_over30,
    )
    return result
