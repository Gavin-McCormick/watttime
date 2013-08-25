from .thermostat import Thermostat, CommonThermostat, CT50v194
from . import discover
from . import fields

THERMOSTATS = (CT50v194,)

def get_thermostat_class(model):
    """
    :param model:   string representation of the thermostat's model, in
                    whatever format the thermostat itself returns.
    :type model:    str

    :returns:       subclass of CommonThermostat, or None if there is not a
                    matching subclass found in THERMOSTATS.
    """
    for thermostat in THERMOSTATS:
        if issubclass(thermostat, Thermostat) and thermostat.MODEL == model:
            return thermostat

def get_thermostat(host_address=None):
    """
    If a host_address is not passed, auto-discovery will happen. Auto-discovery
    will only succeed then exactly 1 thermostat is on your network.

    :param host_address:    optional address for a thermostat. This can be an
                            IP address or domain name.

    :returns:   instance of a CommonThermostat subclass, or None if a matching
                subclass cannot be found.
    """
    if host_address is None:
        host_address = discover.discover_address()
    initial = CommonThermostat(host_address)
    model = initial.model.get('raw')
    thermostat_class = get_thermostat_class(model)
    if thermostat_class is not None:
        return thermostat_class(host_address)
