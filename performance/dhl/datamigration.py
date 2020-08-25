import datetime as dt
import re

from collections import defaultdict
from operator import itemgetter
from pathlib import Path

from ..extensions import db
from ..mdbreader import mdbreader
from ..models import FlightType
from ..utils import datefromiso
from ..utils import float_or_none
from ..utils import int_or_none
from ..utils import str_or_none
from ..utils import timefromiso

from .models import Bound
from .models import Flight
from .models import Operation
from .models import Report
from .models import ScheduledFlight
from .models import ScheduledReport

class Migrator:
    """
    DHL Performance MDB Data Migration
    """

    def __init__(self, mdbpath):
        self.mdbpath = Path(mdbpath)
        if not self.mdbpath.exists():
            raise RuntimeError(f'Database not found, "{self.mdbpath}"')
        self.reader = mdbreader(self.mdbpath)

    def migrate(self):
        """
        Migrate data from the old Amazon MDB.
        """
        legacy = self._legacy()

        cache = {
            'bounds': {},
            'codes': {},
            'comments': defaultdict(list),
            'details_abx_amazon_performance': {},
            'details_aircraft_spares': {},
            'details_crew_info': {},
            'details_dhl_performance': {},
            'flight_types': {},
            'flights': defaultdict(list),
            'flights_delaycodes_by_flight_id': defaultdict(list),
            'operations': {},
        }

        for rowdict in legacy['flight_types'].values():
            name = rowdict['name']
            if name not in cache['flight_types']:
                flight_type = cache['flight_types'][name] = FlightType(name=name)
                if name.lower() == 'scheduled':
                    flight_type.report_order = 0
                elif name.lower() == 'extra':
                    flight_type.report_order = 1
                elif name.lower() == 'extra cmi':
                    flight_type.report_order = 2
                elif name.lower() == 'extra non-cmi':
                    flight_type.report_order = 3
                db.session.add(flight_type)

        for rowdict in legacy['flights_delaycodes'].values():
            cache['flights_delaycodes_by_flight_id'][rowdict['flight_id']].append(rowdict)

        for rowdict in legacy['bounds'].values():
            name = rowdict['name']
            if name not in cache['bounds']:
                bound = cache['bounds'][name] = Bound(name=name)
                if name.lower() == 'inbound':
                    bound.altname = 'Front Half'
                    bound.report_order = 0
                else:
                    bound.altname = 'Back Half'
                    bound.report_order = 1
                db.session.add(bound)

        for data in legacy['operations'].values():
            name = data['name']
            if name not in cache['operations']:
                operation = cache['operations'][name] = Operation(name = name)
                db.session.add(operation)

        pkitems = ('operation_id', 'date')
        getpk = itemgetter(*pkitems)

        for table in ['comments', 'flights']:
            for data in legacy[table]:
                cache[table][getpk(data)].append(data)

        for table in ['details_abx_amazon_performance',
                      'details_aircraft_spares', 'details_crew_info',
                      'details_dhl_performance']:
            for data in legacy[table]:
                cache[table][getpk(data)] = data

        def value2attribute(s):
            return s.lower().replace(' ', '_')

        for detaildict in legacy['details']:
            pk = operation_id, date = getpk(detaildict)

            report = Report(
                date = date,
            )

            # operation
            # XXX: dirty data, some operations are referenced that do not exist
            if operation_id in legacy['operations']:
                operation_name = legacy['operations'][operation_id]['name']
                operation = cache['operations'][operation_name]
                report.operation = operation

            # details
            # convert comments from table rows to fields in report table
            if pk in cache['comments']:
                for commentdict in cache['comments'][pk]:
                    key = value2attribute(commentdict['key'])
                    setattr(report, key, commentdict['value'])

            # ABX/Amazon performance
            if pk in cache['details_abx_amazon_performance']:
                for key, value in cache['details_abx_amazon_performance'][pk].items():
                    if key not in pkitems:
                        setattr(report, f'abx_amazon_{key}', value)

            # aircraft spares
            if pk in cache['details_aircraft_spares']:
                data = cache['details_aircraft_spares'][pk]
                report.aircraft_spares_1200 = data['1200']
                report.aircraft_spares_1800 = data['1800']
                report.aircraft_spares_2000 = data['2000']
                report.aircraft_spares_0300 = data['0300']

            # crew info
            if pk in cache['details_crew_info']:
                data = cache['details_crew_info'][pk]
                report.crew_info_1200 = data['1200']
                report.crew_info_1800 = data['1800']
                report.crew_info_2000 = data['2000']
                report.crew_info_0300 = data['0300']

            # DHL performance
            if pk in cache['details_dhl_performance']:
                for key, value in cache['details_dhl_performance'][pk].items():
                    if key not in pkitems:
                        setattr(report, f'dhl_{key}', value)

            for data in cache['flights'][pk]:
                bound_name = legacy['bounds'][data['bound_id']]['name']
                bound = cache['bounds'][bound_name]
                flight_type_name = legacy['flight_types'][data['flight_type_id']]['name']
                flight_type = cache['flight_types'][flight_type_name]
                origin = legacy['stations'][data['origin_station_id']]['name']
                destination = legacy['stations'][data['destination_station_id']]['name']
                report.flights.append(
                    Flight(
                        bound = bound,
                        flight_number = data['flight_number'],
                        leg = data['leg'],
                        flight_type = flight_type,
                        tail_number = data['tail'],
                        weight = data['weight'],
                        comment = data['comment'],
                        origin_station = origin,
                        origin_departure_estimated_date = data['departure_date_estimated'],
                        origin_departure_estimated_time = data['departure_time_estimated'],
                        origin_departure_actual_date = data['departure_date_actual'],
                        origin_departure_actual_time = data['departure_time_actual'],
                        destination_station = destination,
                        destination_arrival_estimated_date = data['arrival_date_estimated'],
                        destination_arrival_estimated_time = data['arrival_time_estimated'],
                        destination_arrival_actual_date = data['arrival_date_actual'],
                        destination_arrival_actual_time = data['arrival_time_actual'],
                        origin_delays = data['optimization_origin_delaycodes'],
                        destination_delays = data['optimization_destination_delaycodes'],
                    )
                )

            db.session.add(report)

        for scheduledata in legacy['schedules']:
            operation_id = scheduledata['operation_id']
            operation_name = legacy['operations'][operation_id]['name']
            operation = cache['operations'][operation_name]
            scheduled_report = ScheduledReport(
                name = scheduledata['name'],
                operation = operation,
            )
            for flightdata in legacy['schedules_flights']:
                bound_name = legacy['bounds'][flightdata['bound_id']]['name']
                flight_type_name = legacy['flight_types'][flightdata['flight_type_id']]['name']
                flight_type = cache['flight_types'][flight_type_name]
                origin = legacy['stations'][flightdata['origin_station_id']]['name']
                destination = legacy['stations'][flightdata['destination_station_id']]['name']
                scheduled_flight = ScheduledFlight(
                    flight_number = flightdata['flight_number'],
                    leg = flightdata['leg'],
                    flight_type = flight_type,
                    tail_number = flightdata['tail'],
                    weight = flightdata['weight'],
                    comment = flightdata['comment'],
                    origin_station = origin,
                    origin_departure_estimated_date = flightdata['departure_date_estimated'],
                    origin_departure_estimated_time = flightdata['departure_time_estimated'],
                    destination_station = destination,
                    destination_arrival_estimated_date = flightdata['arrival_date_estimated'],
                    destination_arrival_estimated_time = flightdata['arrival_time_estimated'],
                )
                if flightdata['bound_id'] in legacy['bounds']:
                    bound_name = legacy['bounds'][flightdata['bound_id']]['name']
                    bound = cache['bounds'][bound_name]
                    scheduled_flight.bound = bound
                if operation_id in legacy['operations']:
                    operation_name = legacy['operations'][operation_id]['name']
                    operation = cache['operations'][operation_name]
                    scheduled_flight.operation = operation
                scheduled_report.scheduled_flights.append(scheduled_flight)
            db.session.add(scheduled_report)

    def _legacy(self):
        """
        Return the legacy database inside a dict.
        """
        legacy = defaultdict(dict)

        def convert(table, conv, pk=None, src=None):
            """
            :param table: mdb table name
            :param conv: dict of (field name, convert functon)
            :param pk: primary key name. if given the data is indexed by this
                       key. otherwise it is just appended in a list.
            :param src: dict to lookup source key.
            """
            if pk is None:
                legacy[table] = list()
            for rowdict in self.reader.read_table(table):
                for key, func in conv.items():
                    if src and key in src:
                        value = rowdict[src[key]]
                    else:
                        value = rowdict[key]
                    rowdict[key] = func(value)
                if pk is None:
                    legacy[table].append(rowdict)
                else:
                    legacy[table][rowdict[pk]] = rowdict

        convert('bounds', {'id': int, 'name': str}, pk='id')
        convert('flight_types', {'id': int, 'name': str}, pk='id')
        convert('operations', {'id': int, 'name': str}, pk='id')
        convert('stations', {'id': int, 'name': str}, pk='id')
        # details (reports)
        convert('details',
            {
                'operation_id': int,
                'date': datefromiso,
            },
            src = {
                'date': 'operation_date',
            })
        convert('comments',
            {
                'operation_id': int,
                'date': datefromiso,
                'order': int,
                'key': str,
                'value': str,
            },
            src = {
                'date': 'operation_date',
            })
        convert(
            'details_abx_amazon_performance',
            {
                'operation_id': int,
                'date': datefromiso,
                'previous_days_performance_percent': float_or_none,
                'previous_days_performance_lanes': int_or_none,
                'previous_days_performance_late': int_or_none,
                'arrival_performance_mtd_percent': float_or_none,
                'arrival_performance_mtd_lanes': int_or_none,
                'arrival_performance_mtd_late': int_or_none,
                'days_at_100_percent': int_or_none,
                'qtd_performance_percent': float_or_none,
                'qtd_performance_lanes': int_or_none,
                'qtd_performance_late': int_or_none,
            },
            src = {
                'date': 'operation_date',
            })
        convert(
            'details_aircraft_spares',
            {
                'operation_id': int,
                'date': datefromiso,
                '1200': int_or_none,
                '1800': int_or_none,
                '2000': int_or_none,
                '0300': int_or_none,
            },
            src = {
                'date': 'operation_date',
            })
        convert(
            'details_crew_info',
            {
                'operation_id': int,
                'date': datefromiso,
                '1200': int_or_none,
                '1800': int_or_none,
                '2000': int_or_none,
                '0300': int_or_none,
            },
            src = {
                'date': 'operation_date',
            }
        )
        convert(
            'details_dhl_performance',
            {
                'operation_id': int,
                'date': datefromiso,
                'previous_overall_performance': float_or_none,
                'previous_overall_performance_lanes': int_or_none,
                'previous_overall_performance_late': int_or_none,
                'todays_arrival_performance_front_half': float_or_none,
                'todays_arrival_performance_front_half_lanes': int_or_none,
                'todays_arrival_performance_front_half_late': int_or_none,
                'arrival_performance_mtd': float_or_none,
                'arrival_performance_mtd_lanes': int_or_none,
                'arrival_performance_mtd_late': int_or_none,
                'assumed_best_arrival_performance_for_month': float_or_none,
                'assumed_best_arrival_performance_for_month_lanes': int_or_none,
                'assumed_best_arrival_performance_for_month_late': int_or_none,
                'qtd_performance': float_or_none,
                'qtd_performance_lanes': int_or_none,
                'qtd_performance_late': int_or_none,
                'arrival_performance_wtd': float_or_none,
                'arrival_performance_wtd_lanes': int_or_none,
                'arrival_performance_wtd_late': int_or_none,
                'days_at_100_percent': int_or_none,
                'arrival_performance_mtd_30_percent': float_or_none,
                'arrival_performance_mtd_30_lanes': int_or_none,
                'arrival_performance_mtd_30_late': int_or_none,
            },
            src = {
                'date': 'operation_date',
            }
        )
        convert(
            'flights',
            {
                'operation_id': int,
                'date': datefromiso,
                'bound_id': int,
                'flight_number': str_or_none,
                'leg': int_or_none,
                'flight_type_id': int,
                'tail': str_or_none,
                'weight': int_or_none,
                'comment': str_or_none,
                'origin_station_id': int,
                'departure_date_estimated': datefromiso,
                'departure_time_estimated': timefromiso,
                'departure_date_actual': datefromiso,
                'departure_time_actual': timefromiso,
                'destination_station_id': int,
                'arrival_date_estimated': datefromiso,
                'arrival_time_estimated': timefromiso,
                'arrival_date_actual': datefromiso,
                'arrival_time_actual': timefromiso,
                'optimization_origin_delaycodes': str_or_none,
                'optimization_destination_delaycodes': str_or_none,
            },
            src = {
                'date': 'operation_date',
            }
        )
        # schedules (reports)
        convert('schedules', {'id': int, 'name': str, 'operation_id': int})
        # scheduled flights
        convert(
            'schedules_flights',
            {
                'schedule_id': int,
                'leg': int,
                'flight_type_id': int,
                'tail': str_or_none,
                'bound_id': int,
                'weight': int_or_none,
                'comment': str,
                'origin_station_id': int,
                'departure_date_estimated': datefromiso,
                'departure_time_estimated': timefromiso,
                'departure_date_actual': datefromiso,
                'departure_time_actual': timefromiso,
                'destination_station_id': int,
                'arrival_date_estimated': datefromiso,
                'arrival_time_estimated': timefromiso,
                'arrival_date_actual': datefromiso,
                'arrival_time_actual': timefromiso,
            },
        )

        return legacy
