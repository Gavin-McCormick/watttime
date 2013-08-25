import json
import datetime
import pytz
import time
import requests
import socket
import struct

# Returns a list of Thermostat objects
def find_thermostat_ips():
    # These parameters are described in the docs:
    # https://radiothermostat.com/documents/RTCOAWiFIAPIV1_3.pdf
    discover_ip = '239.255.255.250'
    discover_port = 1900
    discover_message = '\r\n'.join([
            'TYPE: WM-DISCOVER',
            'VERSION: 1.0',
            '',
            'services: com.marvell.wm.system*',
            '', '']).encode('utf-8')

    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        s.settimeout(1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.sendto(discover_message, (discover_ip, discover_port))
        m = struct.pack('=4sl', socket.inet_aton(discover_ip), socket.INADDR_ANY)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, m)

        ips = []
        while True:
            try:
                a, b = s.recvfrom(4096)
                ips.append(b[0])
            except socket.timeout:
                break

        return ips

    finally:
        if s is not None:
            try:
                s.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP,
                        socket.inet_aton(discover_ip) + socket.inet_aton('0.0.0.0'))
            except socket.error:
                pass

class Thermostat:
    def __init__(self, ip):
        self.ip = ip
        self.last_message = None
        self.last_left_mode = {}
        # 'last_left_mode' is a dictionary that maps each mode to the last
        # time that we issued a command to leave that mode (as we are not
        # supposed to return to that mode for at least 4 minutes after that
        # point). We only care about modes 1 and 2, as the restriction for
        # mode 0 is not important.

    def url(self, loc):
        return 'http://{}/{}'.format(self.ip, loc)

    # We enforce at least 10 seconds between messages
    # See https://radiothermostat.com/documents/RTCOA%20WiFI%20Application%20Developers%20Guide%20V1_0.pdf
    def throttle_message(self):
        now = time.time()
        if self.last_message is not None:
            wait_for = self.last_message + 10 - now
            if wait_for > 0:
                time.sleep(wait_for)
        self.last_message = now

    def get(self, loc):
        self.throttle_message()
        response = requests.get(self.url(loc))
        return response.json()

    def post(self, loc, data):
        self.throttle_message()
        response = requests.post(self.url(loc), data = json.dumps(data))
        return response.json()

    # Changes thermostat to mode 'mode'. 'payload' specifies other
    # parameters which will be set with the same command.
    #
    # If the list 'okay_modes' is given, then the mode will not be switched
    # if the current mode is in that list.
    #
    # Modes:
    #   0 - off
    #   1 - heat
    #   2 - cool
    #   3 - auto
    # Restrictions: (from above pdf)
    #   never switch directly from 'heat' to 'cool', switch to off first
    #   wait at least 4 minutes between consecutive switches to 'heat' or
    #       consecutive switches to 'cool'
    def set_mode(self, mode, payload = None, okay_modes = []):
        # I don't know what the restrictions do for auto, so we don't support it
        if not (mode in [0, 1, 2]):
            raise ValueError("Invalid mode")

        if payload is None:
            payload = {}
        else:
            payload = dict(payload)

        cur_mode = self.get('tstat')['tmode']
        if cur_mode == mode or (cur_mode in okay_modes):
            self.post('tstat', payload)
        else:
            payload['tmode'] = mode

            # For any mode switch, we first switch to off. 
            if mode == 0:
                self.post('tstat', payload)
            elif cur_mode != 0:
                self.post('tstat', {'tmode' : 0})
            self.last_left_mode[cur_mode] = time.time()

            # Keep going if necessary...
            if mode != 0:
                last = self.last_left_mode.get(mode, None)
                if last is not None:
                    wait = last + (4 * 60) - time.time()
                    if wait > 0:
                        time.sleep(wait)

                self.post('tstat', payload)

    def _get_by(loc, key):
        def getter(self):
            return self.get(loc)[key]
        return getter

    temperature = _get_by('tstat', 'temp')

    def turn_off(self):
        return self.set_mode(0)

    # If neither high nor low is given, then turn the thermostat state to off.
    #
    # Otherwise, set the thermostat of 'heating' if low is given or 'cooling'
    # if high is given. (If both are given, choose according to which point
    # is closer to the current temperature. In this case, we must have
    # high - low >= 3.) However, if the current temperature is at least
    # 1 degree above low (if heating) then leave the thermostat in its present
    # mode, unless that mode is cooling, in which case turn it to 'off'; and
    # similarly if the current temperature is at least 1 degree below high
    # if cooling.
    def set_temperature_range(self, low = None, high = None):
        if low is None and high is None:
            self.set_mode(0)
            return self.temperature()
        else:
            t = self.temperature()

            if high is not None and low is not None:
                if high - low < 3:
                    raise ValueError("Low and high temperature set points are closer than three degrees F apart: low = {!s} and high = {!s}".format(low, high))

                if 2 * t > (low + high):
                    low = None
                else:
                    high = None

            if high is None:
                if t > low + 1:
                    self.set_mode(0, {'it_heat' : low}, [1])
                else:
                    self.set_mode(1, {'it_heat' : low})
            else:
                if t < high - 1:
                    self.set_mode(0, {'it_cool' : high}, [2])
                else:
                    self.set_mode(2, {'it_cool' : high})

            return t
