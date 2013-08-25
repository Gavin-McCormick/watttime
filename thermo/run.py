import traceback
import time
import datetime
import pytz
import requests
import sys

import thermostat
import settings
import datastream

def fail(xs, print_exc = False):
    if print_exc:
        traceback.print_exc()
        print ('')

    for x in xs:
        print (x)

    sys.exit(1)

def convert_tz(time, timezone):
    return timezone.normalize(time.astimezone(timezone))

def get_hour(time):
    x = time.microsecond
    x /= 1000000
    x += time.second
    x /= 60
    x += time.minute
    x /= 60
    x += time.hour
    return x

def run():
    try:
        import config
    except ImportError:
        fail(["Require a configuration file called 'config.py'."], True)

    c = getattr(config, 'config', None)

    if c is None:
        fail(["File 'config.py' does not define a variable called 'config'."])

    if not isinstance(c, settings.Settings):
        fail(["Variable 'config' is not a Settings object."])

    stream = datastream.PercentDirty(c.iso)

    t = None
    if c.thermostat is not None:
        if c.thermostat.ip_address is None:
            print ("Searching for thermostats on the local network.")
            ips = thermostat.find_thermostat_ips()
            if len(ips) == 0:
                fail(["Could not find any radio thermostats on the local network."])
            else:
                print ("Auto-found one or more radio thermostats:")
                for ip in ips:
                    print ("    IP address: {}".format(ip))
                ip = ips[0]
                print ("Using first thermostat, IP {}".format(ip))
        else:
            ip = c.thermostat.ip_address
        t = thermostat.Thermostat(ip)

    oneweek = datetime.timedelta(days = 7)

    while True:
        try:
            stream.refresh()

            cur = stream.cur_value()

            if t is not None:
                now = datetime.datetime.now(pytz.utc)
                now_local = convert_tz(now, c.timezone)
                oneweekago = now - oneweek

                slot = c.thermostat.get_slot(get_hour(now_local))

                i0 = stream.find_index(oneweekago)
                i1 = len(stream.data)
                amount_lower = 0
                amount_greater = 0

                for i in range(i0, i1):
                    j = i + 1
                    then, value = stream.data[i]

                    then_hour = get_hour(convert_tz(then, c.timezone))

                    if slot == c.thermostat.get_slot(then_hour):
                        if j == i1:
                            diff = now - then
                        else:
                            diff = stream.data[j][0] - then

                        # If it's more than an hour between consecutive data
                        # points, then we treat the data as just missing
                        # rather than attempting to extrapolate further.
                        if diff > datetime.timedelta(hours = 1):
                            diff = datetime.timedelta(hours = 1)

                        if value <= cur:
                            amount_lower += diff.total_seconds()
                        else:
                            amount_greater += diff.total_seconds()

                percentile = amount_lower / (amount_lower + amount_greater)

                # print ("     currently {:.3f} badness, {:.3f} percentile".format(cur, percentile))

                heat_to = c.thermostat.schedule[slot][1]
                cool_to = c.thermostat.schedule[slot][2]

                low = None
                high = None
                if heat_to is not None:
                    low = heat_to.get_temp(percentile)
                if cool_to is not None:
                    high = cool_to.get_temp(percentile)

                msg = "[{}] ".format(now_local.strftime('%H.%M'))
                if low is None:
                    if high is None:
                        msg += "setting thermostat to off..."
                    else:
                        msg += "setting maximum temperature {:.2f} F...".format(high)
                else:
                    if high is None:
                        msg += "setting mininum temperature {:.2f} F...".format(low)
                    else:
                        msg += "setting temperature range {:.2f} F - {:.2f} F...".format(low, high)
                sys.stdout.write(msg)
                sys.stdout.flush()
                cur_temp = t.set_temperature_range(low, high)
                sys.stdout.write(" done. Currently {:.2f} F.\n".format(cur_temp))
                sys.stdout.flush()

        except:
            traceback.print_exc()

        time.sleep(c.update_frequency * 60)

if __name__ == "__main__":
    run()
