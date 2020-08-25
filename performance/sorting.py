
def flight_sort_key(flight):
    return (
        flight.flight_type.report_order,
        flight.flight_number,
        flight.tail_number,
        flight.leg,
    )

