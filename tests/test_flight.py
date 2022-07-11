import datetime

from performance import parse
from performance.extensions import db
from performance.models import Delay
from performance.models import Flight
from performance.models import Report

datetime_attrmap = {
    'origin': [
        'origin_departure_estimated_date',
        'origin_departure_estimated_time',
        'origin_departure_actual_date',
        'origin_departure_actual_time',
    ],
    'destination': [
        'destination_arrival_estimated_date',
        'destination_arrival_estimated_time',
        'destination_arrival_actual_date',
        'destination_arrival_actual_time',
    ],
}

def test_flights_empty(app):
    """
    Test that we start with an empty database.
    """
    with app.app_context():
        flights = Flight.query.all()
        assert len(flights) == 0

def check_flight_delays(flight, attr, delays_string, *expected_delays):
    """
    Update flight delays from formatted string and check database objects'
    attributes.
    """
    assert attr in ('origin', 'destination')

    delays_string_attr = attr + '_delays_string'
    setattr(flight, delays_string_attr, delays_string)
    db.session.commit()

    # check delay attributes match
    flight_delays = getattr(flight, attr + '_delays')
    items = zip(flight_delays, expected_delays)
    for enumitem in enumerate(items):
        expected_position, delay_item = enumitem
        flight_delay, expected_delay = delay_item
        expected_code, expected_minutes, expected_is_cancelled = expected_delay
        assert flight_delay.code == expected_code
        assert flight_delay.is_cancelled == expected_is_cancelled
        assert flight_delay.minutes == expected_minutes
        assert flight_delay.position == expected_position

    # check assembles formatted string correctly
    flight_delays_string = getattr(flight, delays_string_attr)
    delay_fields = ['code', 'minutes', 'is_cancelled']
    expected_delays_as_data = [
        dict(zip(delay_fields, delay_tuple)) for delay_tuple in expected_delays
    ]
    formatted_delays = parse.formatdelays(expected_delays_as_data)
    assert flight_delays_string == formatted_delays

    # try setting the attribute
    setattr(flight, delays_string_attr, formatted_delays)
    db.session.commit()
    assert getattr(flight, delays_string_attr) == formatted_delays

def test_flight_origin_delay_codes(app):
    """
    Test adding origin delay codes by parsing the formatted string.
    """
    with app.app_context():
        flight = Flight()
        db.session.add(flight)
        check_flight_delays(
            flight,
            'origin',
            'ABC DEF GHI(32)',
            ('ABC', None, False),
            ('DEF', None, False),
            ('GHI', 32, False),
        )
        check_flight_delays(
            flight,
            'origin',
            'ABC DEF GHI64',
            ('ABC', None, False),
            ('DEF', None, False),
            ('GHI', 64, False)
        )

def test_flight_destination_delay_code(app):
    """
    Test adding destination delay codes by parsing a formatted string.
    """
    with app.app_context():
        flight = Flight()
        db.session.add(flight)
        check_flight_delays(
            flight,
            'destination',
            'JKL MNO PQR(8)',
            ('JKL', None, False),
            ('MNO', None, False),
            ('PQR', 8, False),
        )
        # removed 8 minutes for PQR, added 5 minutes to MNO
        check_flight_delays(
            flight,
            'destination',
            'JKL MNO5 PQR',
            ('JKL', None, False),
            ('MNO', 5, False),
            ('PQR', None, False),
        )
        # removed JKL
        check_flight_delays(
            flight,
            'destination',
            'MNO(5) PQR',
            ('MNO', 5, False),
            ('PQR', None, False),
        )
        Delay.query.filter(Delay.code == 'JKL').one()

def create_flight(est, act, origdest, est_date=None, act_date=None):
    """
    Convenience function for populating date and time fields of a new flight.
    """
    if origdest not in ('origin', 'destination'):
        raise ValueError('Invalid origdest value %r.' % origdest)

    report = Report(date=datetime.date(2000, 1, 1))
    attrnames = datetime_attrmap[origdest]
    kwargs = dict(zip(attrnames, [est_date, est, act_date, act]))
    flight = Flight(report=report, **kwargs)
    return flight

def check_estimated_actual_diff(est, act, expected, est_date=None, act_date=None):
    """
    Assert time diff minutes for origin and destination.
    """
    # origin
    flight = create_flight(est, act, 'origin', est_date, act_date)
    assert flight.origin_diff_minutes_value() == expected
    # destination
    flight = create_flight(est, act, 'destination', est_date, act_date)
    assert flight.destination_diff_minutes_value() == expected

def test_flight_diff_minutes():
    """
    Test that difference in minutes for estimated and actual times are
    calculated as expected.
    """
    # 0100 -> None = 0m
    check_estimated_actual_diff(datetime.time(1,0), None, 0)
    # None -> 0100 = 0m
    check_estimated_actual_diff(None, datetime.time(1,0), 0)
    # 0000 -> 0100 = 60m
    check_estimated_actual_diff(datetime.time(0,0), datetime.time(1,0), 60)
    # Jan. 1, 0000 -> Jan. 2, 0000
    check_estimated_actual_diff(
        datetime.time(0,0),
        datetime.time(0,0),
        60*24, # expected
        act_date = datetime.date(2000,1,2),
    )
    # NOTE: just asserting for what this will do in a time traveling
    #       backwards situation.
    # Jan. 1, 0000 -> Dec. 31 1999, 0000
    check_estimated_actual_diff(
        datetime.time(0,0),
        datetime.time(0,0),
        -60*24, # expected
        act_date = datetime.date(1999,12,31),
    )
