import pytz

min_temp = 35 # F
max_temp = 95 # F

def c2f(c):
    return 32 + (c * 9 / 5)

def f2c(f):
    return (f - 32) * 5 / 9

class TemperatureList:
    # Higher percentile electricity means cleaner, relative to the last week.
    #   percentile 1.00 -- cleanest electricity observed in last week
    #   percentile 0.50 -- median cleanliness observed in last week
    #   percentile 0.00 -- dirtiest electricity observed in last week
    # 'self.temps' is a list of pairs of percentile and temperature.
    #
    # It is an error to pass an empty temperature list.
    # We assume the list is already sorted suitably from most environmentally
    # friendly to least environmentally friendly temperature.
    def __init__(self, xs):
        if len(xs) == 1 and not isinstance(xs[0], tuple):
            xs = [(xs[0], 1)]

        self.temps = []

        total_weight = 0
        for temp, weight in xs:
            if weight < 0:
                raise ValueError("Can't specify a negative frequency '{!s}'".format(weight))
            total_weight += weight
        if total_weight <= 0:
            raise ValueError("Each temperature list must be nonnempty and have at least one member with a positive frequency.")

        perc = 0
        for temp, weight in xs:
            perc += weight
            self.temps.append((perc / total_weight, temp))

    def convert_from_c(self):
        for i in range(len(self.temps)):
            self.temps[i][1] = c2f(self.temps[i][1])

    # Assumes already converted to F
    def validate(self):
        for perc, temp in self.temps:
            if temp < min_temp or temp > max_temp:
                raise ValueError("Specified temperature {}F is outside permitted range: minimum permitted is {}F ({:.2f} C) and maximum is {}F ({:.2f} C).".format(
                    temp, min_temp, f2c(min_temp), max_temp, f2c(max_temp)))

    def get_temp(self, percentile):
        for i in range(0, len(self.temps)):
            if self.temps[i][0] >= percentile:
                return self.temps[i][1]
        return self.temps[-1][1]

class HeatTo(TemperatureList):
    def __init__(self, *xs):
        xs = list(xs)
        xs.sort()
        TemperatureList.__init__(self, xs)

class CoolTo(TemperatureList):
    def __init__(self, *xs):
        xs = list(xs)
        xs.sort()
        xs.reverse()
        TemperatureList.__init__(self, xs)

class ThermostatSettings:
    def __init__(self,
            ip_address          = None,
            heating             = False,
            cooling             = False,
            fahrenheit          = True,
            schedule            = [(0,)]):
        self.ip_address = ip_address
        self.heating = heating
        self.cooling = cooling
        self.fahrenheit = fahrenheit

        self.schedule = []
        last_hours = -1
        for s in schedule:
            if not isinstance(s, tuple):
                s = (s,)

            hours = s[0]
            if hours < 0:
                raise ValueError("Schedule item scheduled for before midnight.")
            if hours > 24:
                raise ValueError("Schedule item scheduled more than 24 hours after midnight.")
            if hours <= last_hours:
                raise ValueError("Schedule item scheduled for before (or same time as) previous item.")
            last_hours = hours

            heat_to = None
            cool_to = None

            for i in range(1, len(s)):
                if not fahrenheit:
                    s[i].convert_from_c()
                s[i].validate()

                if isinstance(s[i], HeatTo):
                    if heat_to is not None:
                        raise ValueError("Multiple HeatTo targets specified for the same time slot.")
                    heat_to = s[i]
                if isinstance(s[i], CoolTo):
                    if cool_to is not None:
                        raise ValueError("Multiple CoolTo targets specified for the same time slot.")
                    cool_to = s[i]

            if (heat_to is not None) and (cool_to is not None):
                highest = heat_to.temps[-1][1]
                lowest = cool_to.temps[-1][1]
                if lowest - highest < 3:
                    raise ValueError("The highest HeatTo temperature {.2f} must be at least 3F lower than the lowest CoolTo temperature {.2f} in the same time slot.".format(highest, lowest))

            if not self.heating:
                heat_to = None
            if not self.cooling:
                cool_to = None

            self.schedule.append((hours, heat_to, cool_to))

    def get_slot(self, hour):
        n = len(self.schedule)
        for i in range(n):
            if self.schedule[i][0] > hour:
                return (i + n - 1) % n
        return n - 1

supported_isos = ['isone', 'bpa', 'caiso']

class Settings:
    def __init__(self,
            iso                 = 'isone',
            timezone            = 'UTC',
            fahrenheit          = True,
            thermostat          = None):
        if not (iso.lower() in supported_isos):
            raise ValueError("Unknown ISO {}. Supported ISOs are: {}".
                    format(iso, ', '.join(supported_isos)))
        self.iso = iso.lower()
        self.timezone = pytz.timezone(timezone)
        self.thermostat = thermostat
