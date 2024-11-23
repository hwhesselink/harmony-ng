import hassapi as hass

import asyncio, time

from remotes.sony_vl600_8001 import rm_vl600_8001_keys
from remotes.urc3680 import urc3680_rc6_keys

from devices.apple_tv_4k import sony_cmds_for_atv
from devices.cisco_stb_8742 import cisco_stb_8742_cmds
from devices.denon_avr_s760 import denon_avr_s760_cmds
from devices.panasonic_dvd_s700 import panasonic_dvd_s700_cmds
from devices.vizio_tv_m656g4 import vizio_tv_m656g4_cmds

LOG_LEVEL = "INFO"

# Kincony
REMOTE = 'a1e13b4a8a46c8c156cdde70ee3be970'
REMNAME = 'web_bda758'


class RemoteControl(object):
    def __init__(self, name, keys):
        self.name = name
        self.keys = keys
        self.addresses = {}

    def add_device(self, address, device):
        self.addresses[address] = device

    def has_device(self, address):
        return address in self.addresses

    def get_device(self, address):
        return self.addresses.get(address)

    def key(self, k):
        return self.keys.get(k)

remotes = []

r = RemoteControl('URC3680', urc3680_rc6_keys)
remotes.append(r)

class Device(object):
    def tx_cmd(self, ad, **kwargs):
        svc = 'esphome/esphome_%s_tx_%s' % (REMNAME, self.proto)
        ad.call_service(svc, **kwargs)

class Vizio_TV_M656G4(Device):
    def __init__(self, name, instance=0):
        self.proto = 'nec'
        self.commands = vizio_tv_m656g4_cmds
        self.name = name
        self.instance = instance

    def send_cmd(self, ad, repcnt, key):
        cmd = self.commands.get(key)
        if not cmd:
            return
        name, command = cmd
        self.tx_cmd(ad, address=0xFB04, command=command)

r.add_device(1, Vizio_TV_M656G4('Vizio TV'))

class Apple_TV_4K(Device):
    def __init__(self, name, instance=0):
        self.proto = 'sony'
        self.commands = sony_cmds_for_atv
        self.name = name
        self.instance = instance

    def send_cmd(self, ad, repcnt, key):
        cmd = self.commands.get(key)
        if not cmd:
            return
        name, (data, nbits) = cmd
        # 'wait' empirically determined for urc3680...
        if repcnt:
            self.tx_cmd(ad, data=data, nbits=nbits, wait=115)
        else:
            self.tx_cmd(ad, data=data, nbits=nbits, wait=10)

r.add_device(2, Apple_TV_4K('Apple TV'))

class Cisco_STB_8742(Device):
    def __init__(self, name, instance=0):
        self.proto = 'pronto'
        self.commands = cisco_stb_8742_cmds
        self.name = name
        self.instance = instance

    def send_cmd(self, ad, repcnt, key):
        cmd = self.commands.get(key)
        if not cmd:
            return
        name, data = cmd
        self.tx_cmd(ad, data=data)

r.add_device(3, Cisco_STB_8742('Set Top Box'))

class Denon_AVR_S760(Device):
    def __init__(self, name, instance=0):
        self.proto = 'pronto'
        self.commands = denon_avr_s760_cmds
        self.name = name
        self.instance = instance

    def send_cmd(self, ad, repcnt, key):
        cmd = self.commands.get(key)
        if not cmd:
            return
        name, data = cmd
        self.tx_cmd(ad, data=data)

r.add_device(5, Denon_AVR_S760('Receiver'))

class Panasonic_DVD_S700(Device):
    def __init__(self, name, instance=0):
        self.proto = 'panasonic'
        self.commands = panasonic_dvd_s700_cmds
        self.name = name
        self.instance = instance

    def send_cmd(self, ad, repcnt, key):
        cmd = self.commands.get(key)
        if not cmd:
            return
        name, command = cmd
        self.tx_cmd(ad, address=0x4004, command=command)

r.add_device(7, Panasonic_DVD_S700('DVD Player'))


class Activity(object):
    def __init__(self):
        pass

class Harmony(hass.Hass):

    def initialize(self):
        self.log("Starting Harmony app")

        self.last_event = None
        self.repcnt = 0

        self.listen_event(self.handle_rc6_event, 'esphome.receiver_rf', device_id=REMOTE)
        self.listen_event(self.handle_rc6_event, 'esphome.receiver_ir', device_id=REMOTE)

    def handle_rc6_event(self, event_name, data, kwargs):
        a = data.get('address')
        c = data.get('command')
        m = data.get('mode')
        t = data.get('toggle')

        if m != 0:
            self.log("Unexpected mode %s, expected 0" % m)
            return

        # get remote that handles this address, last added if multiple
        v = [(r, r.get_device(a)) for r in reversed(remotes) if r.has_device(a)]
        if not v:
            return
        remote, device = v[0]

        key = remote.key(c)
        #self.log("%s %s %s" % (remote.name, c, key))

        # ignore unknown keypress
        if not key:
            self.last_event = None
            self.repcnt = 0
            return

        #self.log("%s _ %s" % ((a, c, m, t), self.last_event))
        if (a, c, m, t) == self.last_event:
            # debounce, allow true repeats
            self.repcnt += 1
            if self.repcnt < 5:
                return
        else:
            # remember new key
            self.last_event = (a, c, m, t)
            self.repcnt = 0

        device.send_cmd(self, self.repcnt, key)
