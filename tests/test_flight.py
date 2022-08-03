import datetime

import pytest
import sqlalchemy as sa

from performance import parse
from performance.extensions import db
from performance.models import Delay
from performance.models import DestinationDelay
from performance.models import Flight
from performance.models import OriginDelay
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

def check_flight_delays(
    *, # keyword only
    flight,
    attr,
    delays_string,
    expected_delays,
):
    """
    Update flight delays from formatted string and check database objects'
    attributes.
    """
    assert attr in ('origin', 'destination')

    # update flight delays objects through the _string setter and commit
    delays_string_attr = attr + '_delays_string'
    setattr(flight, delays_string_attr, delays_string)
    db.session.commit()

    # check delay attributes match
    flight_delays = getattr(flight, attr + '_delays')

    # length
    assert len(flight_delays) == len(expected_delays)

    items = zip(flight_delays, expected_delays)
    for enumitem in enumerate(items):
        expected_position, delay_item = enumitem
        flight_delay, expected_delay = delay_item
        expected_code, expected_minutes, expected_is_cancelled = expected_delay
        assert flight_delay.code == expected_code
        assert flight_delay.is_cancelled == expected_is_cancelled
        assert flight_delay.minutes == expected_minutes
        assert flight_delay.position == expected_position

    # check that it assembles formatted string correctly
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
        db.session.commit()
        check_flight_delays(
            flight = flight,
            attr = 'origin',
            delays_string = 'ABC DEF GHI(32)',
            expected_delays = [
                ('ABC', None, False),
                ('DEF', None, False),
                ('GHI', 32, False),
            ],
        )
        # change GHI minutes
        check_flight_delays(
            flight = flight,
            attr = 'origin',
            delays_string = 'ABC DEF GHI64',
            expected_delays = [
                ('ABC', None, False),
                ('DEF', None, False),
                ('GHI', 64, False)
            ],
        )
        # the ABC code twice in a row
        check_flight_delays(
            flight = flight,
            attr = 'origin',
            delays_string = 'ABC ABC GHI64',
            expected_delays = [
                ('ABC', None, False),
                ('ABC', None, False),
                ('GHI', 64, False)
            ],
        )

def test_flight_destination_delay_code(app):
    """
    Test adding destination delay codes by parsing a formatted string.
    """
    with app.app_context():
        flight = Flight()
        db.session.add(flight)
        check_flight_delays(
            flight = flight,
            attr = 'destination',
            delays_string = 'JKL MNO PQR(8)',
            expected_delays = [
                ('JKL', None, False),
                ('MNO', None, False),
                ('PQR', 8, False),
            ]
        )
        # remove 8 minutes from PQR, and add 5 minutes to MNO
        check_flight_delays(
            flight = flight,
            attr = 'destination',
            delays_string = 'JKL MNO5 PQR',
            expected_delays = [
                ('JKL', None, False),
                ('MNO', 5, False),
                ('PQR', None, False),
            ]
        )
        # remove JKL from flight
        check_flight_delays(
            flight = flight,
            attr = 'destination',
            delays_string = 'MNO(5) PQR',
            expected_delays = [
                ('MNO', 5, False),
                ('PQR', None, False),
            ]
        )
        # delay object with code should stay in database
        Delay.query.filter(Delay.code == 'JKL').one()
        # but the association object should not
        query = DestinationDelay.query.join(
            Flight,
            Delay,
        ).filter(
            DestinationDelay.code == 'JKL',
            DestinationDelay.minutes == None,
            DestinationDelay.is_cancelled == False,
        )
        assert query.one_or_none() is None

def test_duplicate_delay_codes(app):
    with (
        app.app_context(),
        pytest.raises(sa.exc.IntegrityError)
    ):
        flight = Flight(
            origin_delays = [
                OriginDelay(
                    delay_object = Delay(
                        code = 'abc',
                    )
                )
            ],
            destination_delays = [
                DestinationDelay(
                    delay_object = Delay(
                        code = 'abc',
                    )
                )
            ],
        )
        db.session.add(flight)
        db.session.commit()

def test_manually(app):
    """
    Straight-forward add all at once works.
    """
    with app.app_context():
        db.session.add_all([
            Delay(code='abc'),
            Delay(code='def'),
            Delay(code='ghi'),
        ])
        db.session.commit()
        flight = Flight(
            origin_delays = [
                OriginDelay(
                    # using the normal constructor inside here will duplicate codes
                    delay_object = Delay.as_unique(
                        db.session,
                        code = 'abc',
                    ),
                ),
                OriginDelay(
                    # association_proxy
                    code = 'def',
                    minutes = 12,
                ),
            ],
            destination_delays = [
                DestinationDelay(
                    delay_object = Delay.as_unique(
                        db.session,
                        code = 'abc',
                    ),
                ),
                DestinationDelay(
                    # association_proxy
                    code = 'def',
                    minutes = 12,
                ),
                DestinationDelay(
                    # association_proxy
                    code = 'ghi',
                    minutes = 5,
                ),
            ],
        )
        db.session.add(flight)
        db.session.commit()
        # only one code of each
        Delay.query.filter(Delay.code == 'ABC').one()
        Delay.query.filter(Delay.code == 'DEF').one()
        Delay.query.filter(Delay.code == 'GHI').one()
        # expected length
        assert len(flight.origin_delays) == 2
        assert len(flight.destination_delays) == 3
        # origin delays
        delay = flight.origin_delays[0]
        assert delay.code == 'ABC'
        assert delay.minutes is None
        delay = flight.origin_delays[1]
        assert delay.code == 'DEF'
        assert delay.minutes == 12
        # destination delays
        delay = flight.destination_delays[0]
        assert delay.code == 'ABC'
        assert delay.minutes is None
        delay = flight.destination_delays[1]
        assert delay.code == 'DEF'
        assert delay.minutes == 12
        delay = flight.destination_delays[2]
        assert delay.code == 'GHI'
        assert delay.minutes == 5

def test_delay_objects_normally(app):
    with app.app_context():
        delay_objects = [
            Delay(code='abc'),
            Delay(code='ghi'),
        ]
        db.session.add_all(delay_objects)
        db.session.commit()
        assert Delay.query.count() == 2
        Delay.query.filter(Delay.code == 'ABC').one()
        Delay.query.filter(Delay.code == 'GHI').one()

def test_delay_objects_as_unique(app):
    with app.app_context():
        abc, ghi = delay_objects = [
            Delay.as_unique(db.session, code='abc'),
            Delay.as_unique(db.session, code='ghi'),
        ]
        db.session.add_all(delay_objects)
        db.session.commit()
        assert Delay.query.count() == 2
        assert Delay.as_unique(db.session, code='abc') is abc
        assert Delay.as_unique(db.session, code='ghi') is ghi

def test_flight_origin_and_destination(app):
    with app.app_context():
        flight = Flight()
        flight.origin_delays_string = 'ABC1 ABC GHI3'
        flight.destination_delays_string = 'ABC1 ABC GHI3'
        db.session.add(flight)
        db.session.commit()
        assert Delay.query.count() == 2

def test_flight_updating_like_form(app):
    with app.app_context():
        flight = Flight()
        flight.origin_departure_actual_time = datetime.time(3,0)
        flight.destination_arrival_actual_time = datetime.time(4,0)
        flight.weight = 99_999
        flight.origin_delays_string = 'ABC1 ABC GHI3'
        flight.destination_delays_string = 'ABC1 ABC GHI3'
        db.session.add(flight)
        db.session.commit()
        assert Flight.query.one()
        assert Delay.query.count() == 2
        assert flight.weight == 99_999

    with app.app_context():
        flight = Flight.query.first()
        flight.weight = 88_888
        flight.origin_delays_string = 'ABC1 ABC GHI3'
        flight.destination_delays_string = 'ABC1 ABC GHI3'
        db.session.commit()
        assert flight.weight == 88_888

def test_flight_origin_cancelled(app):
    """
    Reproduce XLD <code><minutes> losing the code.
    """
    # NOTE: is_cancelled was missing from comparisons and updates
    with app.app_context():
        flight = Flight()
        flight.origin_delays_string = f'{parse.CANCELLED} AAA60'
        flight.destination_delays_string = f'{parse.CANCELLED} BBB31'
        db.session.add(flight)
        db.session.commit()

    with app.app_context():
        flight = Flight.query.first()
        assert flight.origin_delays[0].code == 'AAA'
        assert flight.origin_delays[0].minutes == 60
        assert flight.origin_delays[0].is_cancelled
        assert flight.origin_delays_string == f'{parse.CANCELLED} AAA(60)'
        assert flight.destination_delays_string == f'{parse.CANCELLED} BBB(31)'

def test_flight_keeps_placeholder(app):
    """
    Test the placeholder delay code is kept.
    """
    # simply removed list comprehension filter
    with app.app_context():
        flight = Flight()
        flight.origin_delays_string = f'AAA5 BBB10 {parse.PLACEHOLDER_CODE}15'
        flight.destination_delays_string = f'CCC8 DDD6 {parse.PLACEHOLDER_CODE}15'
        db.session.add(flight)
        db.session.commit()

    with app.app_context():
        flight = Flight.query.first()
        assert flight.origin_delays[0].code == 'AAA'
        assert flight.origin_delays[0].minutes == 5
        assert not flight.origin_delays[0].is_cancelled
        assert flight.origin_delays[1].code == 'BBB'
        assert flight.origin_delays[1].minutes == 10
        assert not flight.origin_delays[1].is_cancelled
        assert flight.origin_delays[2].code == parse.PLACEHOLDER_CODE
        assert flight.origin_delays[2].minutes == 15
        assert not flight.origin_delays[2].is_cancelled
        #
        assert flight.destination_delays[0].code == 'CCC'
        assert flight.destination_delays[0].minutes == 8
        assert not flight.destination_delays[0].is_cancelled
        assert flight.destination_delays[1].code == 'DDD'
        assert flight.destination_delays[1].minutes == 6
        assert not flight.destination_delays[1].is_cancelled
        assert flight.destination_delays[2].code == parse.PLACEHOLDER_CODE
        assert flight.destination_delays[2].minutes == 15
        assert not flight.destination_delays[2].is_cancelled

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
