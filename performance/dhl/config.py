"""
DHL specific configuration
"""
from performance.config import raise_config

# add dhl specific required config
raise_config.required_truthy.extend([
    # station name to consider as the hub
    'PERFORMANCE_HUB_STATION_NAME',
    # Bound object name for in/out-bound.
    'PERFORMANCE_INBOUND_NAME',
    'PERFORMANCE_OUTBOUND_NAME',
])
