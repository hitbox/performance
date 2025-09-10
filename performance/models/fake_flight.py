from collections import namedtuple

FakeFlight = namedtuple(
    'FakeFlight',
    [
        'fn_number_as_string',
        'dep_dt_date',
        'dep_dt_time',
        'dep_ap_actual',
        'arr_dt_date',
        'arr_dt_time',
        'arr_ap_actual',
        'baggage_weight_kg',
        'baggage_weight_lbs',
    ],
)

FakeFlight.__doc__ = """
Lightweight container for flight data used to bridge external and internal
representations.

This object is not persisted in the database; it exists only to normalize
attributes from external sources into a consistent shape before matching or
merging with internal `Flight` objects.

Fields:
    fn_number_as_string (str): Flight number (string form).
    dep_dt_date (str): Departure date string.
    dep_dt_time (str): Departure time string.
    dep_ap_actual (str): Actual departure airport code.
    arr_dt_date (str): Arrival date string.
    arr_dt_time (str): Arrival time string.
    arr_ap_actual (str): Actual arrival airport code.
    baggage_weight_kg (int): Baggage weight in kilograms.
    baggage_weight_lbs (int): Baggage weight in pounds.
"""
