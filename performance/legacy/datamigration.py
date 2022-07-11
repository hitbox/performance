from collections import defaultdict
from pathlib import Path

from performance.extensions import db
from performance.models import Flight
from performance.models import FlightType
from performance.models import Report
from performance.models import ScheduledFlight
from performance.models import ScheduledReport

from .mdbreader import mdbreader

class Migrator:
    """
    Amazon Performance MDB Data Migration
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
            'codes': {},
            'flight_types': {},
            'flights_delaycodes_by_flight_id': defaultdict(list),
            'stations': {},
        }

        for rowdict in legacy['flight_types'].values():
            name = rowdict['name']
            if name not in cache['flight_types']:
                flight_type = cache['flight_types'][name] = FlightType(name=name)
                if name.lower() == 'scheduled':
                    flight_type.report_order = 0
                elif name.lower() == 'extra-cmi amz':
                    flight_type.report_order = 1
                elif name.lower() == 'extra non-cmi amz':
                    flight_type.report_order = 2
                db.session.add(flight_type)

        for rowdict in legacy['flights_delaycodes'].values():
            cache['flights_delaycodes_by_flight_id'][rowdict['flight_id']].append(rowdict)

        for reportdict in legacy['reports'].values():
            report = Report(
                date = reportdict['report_date'],
                system_detail = reportdict['system_detail'],
                previous_days_performance_percent = reportdict['previous_days_performance_percent'],
                previous_days_performance_lanes = reportdict['previous_days_performance_lanes'],
                previous_days_performance_late = reportdict['previous_days_performance_late'],
                arrival_performance_mtd_percent = reportdict['arrival_performance_mtd_percent'],
                arrival_performance_mtd_lanes = reportdict['arrival_performance_mtd_lanes'],
                arrival_performance_mtd_late = reportdict['arrival_performance_mtd_late'],
                days_at_100_percent = reportdict['days_at_100_percent'],
                qtd_performance_percent = reportdict['qtd_performance_percent'],
                qtd_performance_lanes = reportdict['qtd_performance_lanes'],
                qtd_performance_late = reportdict['qtd_performance_late'],
                assumed_best_arrival_performance_for_month_percent = reportdict['assumed_best_arrival_performance_for_month_percent'],
                assumed_best_arrival_performance_for_month_lanes = reportdict['assumed_best_arrival_performance_for_month_lanes'],
                assumed_best_arrival_performance_for_month_late = reportdict['assumed_best_arrival_performance_for_month_late'],
                arrival_performance_mtd_30_percent = reportdict['arrival_performance_mtd_30_percent'],
                arrival_performance_mtd_30_lanes = reportdict['arrival_performance_mtd_30_lanes'],
                arrival_performance_mtd_30_late = reportdict['arrival_performance_mtd_30_late'],
            )
            db.session.add(report)

            for flightdict in legacy['flights'].values():
                if flightdict['report_id'] != reportdict['id']:
                    continue
                flight_type_name = legacy['flight_types'][flightdict['flight_type_id']]['name']
                flight_type = cache['flight_types'][flight_type_name]
                flight = Flight(
                    flight_type = flight_type,
                    flight_number = flightdict['flight_number'],
                    leg = flightdict['leg'],
                    tail_number = flightdict['tail'],
                    weight = flightdict['weight'],
                    comment = flightdict['comment'],
                    origin_station = legacy['stations'][flightdict['origin_station_id']]['name'],
                    origin_departure_estimated_date = flightdict['departure_date_estimated'],
                    origin_departure_estimated_time = flightdict['departure_time_estimated'],
                    origin_departure_actual_date = flightdict['departure_date_actual'],
                    origin_departure_actual_time = flightdict['departure_time_actual'],
                    origin_delays = flightdict['optimization_origin_delaycodes'],
                    destination_station = legacy['stations'][flightdict['destination_station_id']]['name'],
                    destination_arrival_estimated_date = flightdict['arrival_date_estimated'],
                    destination_arrival_estimated_time = flightdict['arrival_time_estimated'],
                    destination_arrival_actual_date = flightdict['arrival_date_actual'],
                    destination_arrival_actual_time = flightdict['arrival_time_actual'],
                    destination_delays = flightdict['optimization_destination_delaycodes'],
                )
                report.flights.append(flight)

        for scheduledreportdict in legacy['schedules'].values():
            scheduled_report = ScheduledReport(**scheduledreportdict)
            db.session.add(scheduled_report)

            # 'schedules_flights' has no pk from source
            for scheduledflightdict in legacy['schedules_flights']:
                if scheduledflightdict['schedule_id'] != scheduledreportdict['id']:
                    continue
                flight_type_name = legacy['flight_types'][scheduledflightdict['flight_type_id']]['name']
                flight_type = cache['flight_types'][flight_type_name]
                scheduled_flight = ScheduledFlight(
                    flight_type = flight_type,
                    flight_number = scheduledflightdict['flight_number'],
                    leg = scheduledflightdict['leg'],
                    tail_number = scheduledflightdict['tail'],
                    weight = scheduledflightdict['weight'],
                    comment = scheduledflightdict['comment'],
                    origin_station = legacy['stations'][scheduledflightdict['origin_station_id']]['name'],
                    origin_departure_estimated_date = scheduledflightdict['departure_date_estimated'],
                    origin_departure_estimated_time = scheduledflightdict['departure_time_estimated'],
                    destination_station = legacy['stations'][scheduledflightdict['destination_station_id']]['name'],
                    destination_arrival_estimated_date = scheduledflightdict['arrival_date_estimated'],
                    destination_arrival_estimated_time = scheduledflightdict['arrival_time_estimated'],
                )
                scheduled_report.scheduled_flights.append(scheduled_flight)


    def _legacy(self):
        """
        Return the legacy database inside a dict.
        """
        legacy = defaultdict(dict)

        # flight types
        for rowdict in self.reader.read_table('flight_types'):
            rowdict['id'] = int(rowdict['id'])
            legacy['flight_types'][rowdict['id']] = rowdict

        # delay codes
        for rowdict in self.reader.read_table('codes'):
            rowdict['id'] = int(rowdict['id'])
            legacy['codes'][rowdict['id']] = rowdict

        # stations
        for rowdict in self.reader.read_table('stations'):
            rowdict['id'] = int(rowdict['id'])
            legacy['stations'][rowdict['id']] = rowdict

        # station_types
        for rowdict in self.reader.read_table('station_types'):
            rowdict['id'] = int(rowdict['id'])
            legacy['station_types'][rowdict['id']] = rowdict

        # NOTE
        # Commented out for now just using the optimization fields.
        # # flights_delaycodes
        # for rowdict in self.reader.read_table('flights_delaycodes'):
        #     rowdict['id'] = int(rowdict['id'])
        #     rowdict['flight_id'] = int_or_none(rowdict['flight_id'])
        #     rowdict['station_type_id'] = int(rowdict['station_type_id'])
        #     rowdict['order'] = int(rowdict['order'])
        #     rowdict['code_id'] = int_or_none(rowdict['code_id'])
        #     rowdict['minutes'] = int_or_none(rowdict['minutes'])
        #     legacy['flights_delaycodes'][rowdict['id']] = rowdict

        # flights
        for rowdict in self.reader.read_table('flights'):
            rowdict['report_id'] = int_or_none(rowdict['report_id'])
            rowdict['id'] = int(rowdict['id'])
            rowdict['tail'] = str_or_none(rowdict['tail'])
            rowdict['leg'] = int_or_none(rowdict['leg'])
            rowdict['comment'] = str_or_none(rowdict['comment'])
            rowdict['flight_type_id'] = int(rowdict['flight_type_id'])
            rowdict['weight'] = int_or_none(rowdict['weight'])
            rowdict['origin_station_id'] = int(rowdict['origin_station_id'])
            rowdict['departure_date_estimated'] = datefromiso(rowdict['departure_date_estimated'])
            rowdict['departure_time_estimated'] = timefromiso(rowdict['departure_time_estimated'])
            rowdict['departure_date_actual'] = datefromiso(rowdict['departure_date_actual'])
            rowdict['departure_time_actual'] = timefromiso(rowdict['departure_time_actual'])
            rowdict['destination_station_id'] = int(rowdict['destination_station_id'])
            rowdict['arrival_date_estimated'] = datefromiso(rowdict['arrival_date_estimated'])
            rowdict['arrival_time_estimated'] = timefromiso(rowdict['arrival_time_estimated'])
            rowdict['arrival_date_actual'] = datefromiso(rowdict['arrival_date_actual'])
            rowdict['arrival_time_actual'] = timefromiso(rowdict['arrival_time_actual'])
            rowdict['optimization_origin_delaycodes'] = str_or_none(rowdict['optimization_origin_delaycodes'])
            rowdict['optimization_destination_delaycodes'] = str_or_none(rowdict['optimization_destination_delaycodes'])
            legacy['flights'][rowdict['id']] = rowdict

        # reports
        for rowdict in self.reader.read_table('reports'):
            rowdict['id'] = int(rowdict['id'])
            rowdict['report_date'] = datefromiso(rowdict['report_date'])
            rowdict['system_detail'] = rowdict['system_detail']
            rowdict['previous_days_performance_percent'] = float_or_none(rowdict['previous_days_performance_percent'])
            rowdict['previous_days_performance_lanes'] = int_or_none(rowdict['previous_days_performance_lanes'])
            rowdict['previous_days_performance_late'] = int_or_none(rowdict['previous_days_performance_late'])
            rowdict['arrival_performance_mtd_percent'] = float_or_none(rowdict['arrival_performance_mtd_percent'])
            rowdict['arrival_performance_mtd_lanes'] = int_or_none(rowdict['arrival_performance_mtd_lanes'])
            rowdict['arrival_performance_mtd_late'] = int_or_none(rowdict['arrival_performance_mtd_late'])
            rowdict['days_at_100_percent'] = float_or_none(rowdict['days_at_100_percent'])
            rowdict['qtd_performance_percent'] = float_or_none(rowdict['qtd_performance_percent'])
            rowdict['qtd_performance_lanes'] = int_or_none(rowdict['qtd_performance_lanes'])
            rowdict['qtd_performance_late'] = int_or_none(rowdict['qtd_performance_late'])
            rowdict['assumed_best_arrival_performance_for_month_percent'] = float_or_none(rowdict['assumed_best_arrival_performance_for_month_percent'])
            rowdict['assumed_best_arrival_performance_for_month_lanes'] = int_or_none(rowdict['assumed_best_arrival_performance_for_month_lanes'])
            rowdict['assumed_best_arrival_performance_for_month_late'] = int_or_none(rowdict['assumed_best_arrival_performance_for_month_late'])
            rowdict['arrival_performance_mtd_30_percent'] = float_or_none(rowdict['arrival_performance_mtd_30_percent'])
            rowdict['arrival_performance_mtd_30_lanes'] = int_or_none(rowdict['arrival_performance_mtd_30_lanes'])
            rowdict['arrival_performance_mtd_30_late'] = int_or_none(rowdict['arrival_performance_mtd_30_late'])
            legacy['reports'][rowdict['id']] = rowdict

        # scheduled reports
        for rowdict in self.reader.read_table('schedules'):
            rowdict['id'] = int(rowdict['id'])
            rowdict['name'] = rowdict['name']
            legacy['schedules'][rowdict['id']] = rowdict

        # scheduled flights
        legacy['schedules_flights'] = list()
        for rowdict in self.reader.read_table('schedules_flights'):
            rowdict['schedule_id'] = int(rowdict['schedule_id'])
            rowdict['leg'] = int(rowdict['leg'])
            rowdict['flight_type_id'] = int(rowdict['flight_type_id'])
            rowdict['tail'] = str_or_none(rowdict['tail'])
            rowdict['weight'] = int_or_none(rowdict['weight'])
            rowdict['comment'] = rowdict['comment']
            rowdict['origin_station_id'] = int(rowdict['origin_station_id'])
            rowdict['departure_date_estimated'] = datefromiso(rowdict['departure_date_estimated'])
            rowdict['departure_time_estimated'] = timefromiso(rowdict['departure_time_estimated'])
            rowdict['departure_date_actual'] = datefromiso(rowdict['departure_date_actual'])
            rowdict['departure_time_actual'] = timefromiso(rowdict['departure_time_actual'])
            rowdict['destination_station_id'] = int(rowdict['destination_station_id'])
            rowdict['arrival_date_estimated'] = datefromiso(rowdict['arrival_date_estimated'])
            rowdict['arrival_time_estimated'] = timefromiso(rowdict['arrival_time_estimated'])
            rowdict['arrival_date_actual'] = datefromiso(rowdict['arrival_date_actual'])
            rowdict['arrival_time_actual'] = timefromiso(rowdict['arrival_time_actual'])
            legacy['schedules_flights'].append(rowdict)

        return legacy


def datefromiso(s):
    """
    Assumes the full ISO date/time format
    """
    return None if not s else dt.date.fromisoformat(s[:10])

def int_or_none(value):
    return int(value) if value else None

def float_or_none(value):
    return float(value) if value else None

def str_or_none(value):
    return str(value) if value else None

def timefromiso(s):
    if not s or len(s) < 19:
        return None
    if re.search('\+\d\d:\d\d$', s):
        # when you str() the datetime fields, using DAO, they come with a
        # +00:00 at the end; slice that off
        s = s[:-6]
    return dt.time.fromisoformat(s[-8:])
