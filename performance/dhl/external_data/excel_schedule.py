import string

from operator import itemgetter

import click
import openpyxl

from ..models import Flight
from ..models import Report

def dow(value):
    """
    Convert value to a list of integer days of the week.

    The Excel sheet DOW numbers are 1:Monday, 2:Tuesday, etc. This function
    subtracts by one to match the calendar module.
    """
    if value is not None:
        return list(int(c)-1 for c in sorted(str(value)))

def flight(value):
    """
    Strip off letters and spaces from the left side.
    """
    if value is not None:
        return value.lstrip(string.ascii_letters + ' ')

def arrdep(value):
    """
    Keep the time part of arrival and departure datetimes.
    """
    if value is not None:
        return value.time()

# the indexes we want from each row (see green columns in
# file "sample sched file new report.xlsx").
getrow = itemgetter(0, 1, 2, 9, 10, 11)

# Field names have been lower-cased and newlines replaced with underscores by
# the time these are run.
TYPEMAP = {
    # Calendar module days of week: 0 is Monday, 6 is Sunday.
    # The worksheet seems to have 1 is Mon., 7 is Sunday.
    'utc_dow': dow,
    'flight': flight,
    'utc_dep': arrdep,
    'utc_arr': arrdep,
}

def fixfieldname(s):
    return s.replace('\n', '_').lower()

def import_flights(path, date):
    # ? front half is dest = HUB, back half is orig = HUB
    # * NEED HUB config VAR

    wb = openpyxl.load_workbook(path)
    ws = wb.active
    rows = iter(ws)

    # skip first row (merged-cells grouping)
    next(rows)

    # take next as field name
    fields = [fixfieldname(cell.value) for cell in next(rows) if cell.value is not None]
    fields = getrow(fields)

    # NOTE
    # cells past the right of actual data come in as None
    # will blow up if these are ever not strings
    #fields = [fixfieldname(cell.value) for cell in row if cell.value is not None]

    data = []
    for row in rows:
        values = getrow([cell.value for cell in row])
        if all(values):
            rowdict = dict(zip(fields, values))
            # run typemap functions
            for key, func in TYPEMAP.items():
                rowdict[key] = func(rowdict[key])
            data.append(rowdict)

    # filter for weekday
    weekday = date.weekday()
    data = [row for row in data if weekday in row['utc_dow'] ]

    _sortkey = itemgetter('flight', 'utc_dep')
    def sortkey(row):
        flight, utc_dep = _sortkey(row)
        try:
            flight = int(flight)
        except ValueError:
            pass
        return flight, utc_dep

    data = sorted(data, key=sortkey)

    return data
