#
#
#   In this file, define a variable called "config" which should be a Settings
#   object specifying your user settings.
#
#


# Please do not modify the following line, "from settings import *", as it
# is required.
from settings import *


thermostat = ThermostatSettings (

# Specify the IP address of the thermostat you wish to communicate with. If
# omitted or left as 'None', the software will search for thermostats on the
# local network.

        ip_address              = None,

# Set 'heating' to True if you have a heater connected to your thermostat
# and you wish to use it. Similarly set 'cooling' to False if you have an
# air-conditioning unit connected to your thermostat and wish to use it.
# Default is False.

        heating                 = True,
        cooling                 = True,

# Set 'fahrenheit' to True if you want to specify temperatures in Fahrenheit,
# and to False if you wish to specify temperatures in Celcius. This is used
# by the schedule to interpret the temperatures you gave. The radio thermostat
# device internally uses Fahrenheit, so there may be some loss of precision in
# converting from Celcius to Fahrenheit. 
#
# Default is True.

        fahrenheit              = True,

# Specify a schedule of actions you want the thermostat to take.
# The schedule is a list of /schedule items/.
#
# Each schedule item is a tuple. The first element of the tuple is a number,
# representing the number of hours after midnight in your timezone you want
# that item to take effect. The other elements of the tuple are optionally
# a HeatTo object and/or a CoolTo object.
#
# If a HeatTo object is specified and 'heating' is True above, then the
# thermostat will be directed to maintain the specified minimum temperature.
# If a CoolTo object is specified and 'cooling' is True above, then the
# thermostat will be directed to maintain the specified maximum temperature.
# If both are specified, then heating or cooling will be used as necessary;
# if both are omitted, then the thermostat will be left in the 'off' mode.
#
# The HeatTo and CoolTo objects take a list of pairs as arguments. Each
# pair contains a temperature and a frequency. The frequency specifies
# how often you wish that temperature to be used: for example, if you choose
#           HeatTo((50, 0.5), (60, 0.5))
# then the thermostat will heat to 50 the half of the time when electricity
# is worst, and will heat to 60 the half of the time when electricity is best.
# The frequencies are relative and will be re-weighted if they don't add up to 1.
# The order the temperatures are specified in is unimportant. If you wish
# to force a particular temperature regardless of electricity quality, then
# you can use
#           HeatTo((60, 1))
# or just
#           HeatTo(60).
# Temperatures below 35 F or above 95 F should not be used as the radio
# thermostat device will reject those temperatures.
#
# For any fixed time slot, if you specify before HeatTo and CoolTo targets,
# then the highest HeatTo target should be at least 3 F below the lowest
# CoolTo target, due to limitations of the radio thermostat device (which will
# not attempt to maintain an interval smaller than 3 F).
#
# Default is [(0,)], which will leave the thermostat off.
#
# Example:
#   schedule = [(0, CoolTo((73, 0.1), (75, 0.1), (77, 0.5), (79, 0.2), (85, 0.1))]

        schedule                =
            [
            (6, HeatTo((70, 0.05), (65, 0.5), (63, 0.25), (60, 0.2))),
            (9,),
            (16.75, CoolTo((75, 0.1), (80, 0.3), (85, 0.55), (90, 0.05)),
                HeatTo((60, 0.4), (55, 0.5), (50, 0.1))),
            (20, HeatTo((70, 0.2), (65, 0.3), (60, 0.5))),
            (23, HeatTo(60))
            ]
    )

config = Settings(

# The iso specifies where you get your electricity from, and is used by the
# software to determine the quality of your electricity. Where you live
# determines your iso.
# Currently supported ISOs:
#
# isone - New England (Maine, Vermont, New Hampshire, Mass., Conn., Rhode Island)
# caiso - California
# bpa - Oregon and Washington
#
# Default is 'isone'.

        iso                     = 'isone',

# Specify how often, in minutes, you would like the controller to check the
# status of the electric grid at the WattTime website and update the current
# thermostat temperature setting. The frequency with which the website updates
# varies from region to region:
#
# isone - updates every 10 minutes
# caiso - updates every hour
# bpa - updates every hour
#
# Default is 5 minutes.

        update_frequency        = 5,

# 'timezone' should be the name of a time zone in the IANA time zone database
# https://en.wikipedia.org/wiki/IANA_time_zone_database
# Examples:
#   'America/Los_Angeles'       Pacific
#   'America/Denver'            Mountain
#   'America/Chicago'           Central
#   'America/New_York'          Eastern
#   'Europe/London'
#   'Europe/Rome'
# The timezone is used by the thermostat schedule to determine your local time.
#
# Default is 'UTC'.

        timezone                = 'America/New_York',

# Pass a thermostat settings object to specify what heating and cooling
# actions you wish to take. If omitted or 'None', the software will not
# attempt to find or interface with your thermostat.

        thermostat              = thermostat
    )
