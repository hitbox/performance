"""
DHL specific configuration
"""
from performance.config import raise_config

# add dhl specific required config
raise_config.required_truthy.extend([
    # station name to consider as the hub
    'PERFORMANCE_HUB_STATION_NAME',
    # name of FlightType to use for importing scheduled excel files
    'PERFORMANCE_SCHEDULED_FLIGHT_TYPE_NAME',
    # Bound object name for in/out-bound.
    'PERFORMANCE_INBOUND_NAME',
    'PERFORMANCE_OUTBOUND_NAME',
])
