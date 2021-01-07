
def import_flights(path):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    rows = iter(ws)

    # skip first row
    next(rows)
    # take next as field name
    row = next(rows)
    # NOTE
    # cells past the right of actual data come in as None
    fields = [cell.value for cell in row if cell.value is not None]

    from pprint import pprint
    for row in rows:
        rowdict = dict(zip(fields, (cell.value for cell in row)))

        for key, func in TYPEMAP.items():
            rowdict[key] = func(rowdict[key])

        pprint(rowdict)
        break

