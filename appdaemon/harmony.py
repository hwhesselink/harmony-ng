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
    def __init__(self, appdaemon, name, keys):
        self.appdaemon = appdaemon
        self.log = appdaemon.log
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


class Device(object):
    def tx_cmd(self, cmd, **kwargs):
        proto = self.proto
        if proto != 'pronto' and isinstance(cmd, str) and cmd.startswith('0000 '):
            # if payload looks like Pronto, send it that way
            proto = 'pronto'
            kwargs = {}
        svc = 'esphome/esphome_%s_tx_%s' % (REMNAME, proto)

        if proto in ('nec', 'panasonic'):
            cmdfld = 'command'
        elif proto in ('pronto', 'sony'):
            cmdfld = 'data'
        kwargs[cmdfld] = cmd

        self.appdaemon.call_service(svc, **kwargs)

class Vizio_TV_M656G4(Device):
    def __init__(self, appdaemon, name, instance=0):
        self.proto = 'nec'
        self.commands = vizio_tv_m656g4_cmds
        self.appdaemon = appdaemon
        self.name = name
        self.instance = instance

    def send_cmd(self, repcnt, key):
        cmd = self.commands.get(key)
        if not cmd:
            return
        name, command = cmd
        self.tx_cmd(command, address=0xFB04)

class Apple_TV_4K(Device):
    def __init__(self, appdaemon, name, instance=0):
        self.proto = 'sony'
        self.commands = sony_cmds_for_atv
        self.appdaemon = appdaemon
        self.name = name
        self.instance = instance

    def send_cmd(self, repcnt, key):
        cmd = self.commands.get(key)
        if not cmd:
            return
        name, (data, nbits) = cmd
        # 'wait' empirically determined for urc3680...
        if repcnt:
            self.tx_cmd(data, nbits=nbits, wait=115)
        else:
            self.tx_cmd(data, nbits=nbits, wait=10)

class Cisco_STB_8742(Device):
    def __init__(self, appdaemon, name, instance=0):
        self.proto = 'pronto'
        self.commands = cisco_stb_8742_cmds
        self.appdaemon = appdaemon
        self.name = name
        self.instance = instance

    def send_cmd(self, repcnt, key):
        cmd = self.commands.get(key)
        if not cmd:
            return
        name, data = cmd
        self.tx_cmd(data)

class Denon_AVR_S760(Device):
    def __init__(self, appdaemon, name, instance=0):
        self.proto = 'panasonic'
        self.commands = denon_avr_s760_cmds
        self.appdaemon = appdaemon
        self.name = name
        self.instance = instance

    def send_cmd(self, repcnt, key):
        cmd = self.commands.get(key)
        if not cmd:
            return
        self.tx_cmd(cmd, address=0x2A4C)

class Panasonic_DVD_S700(Device):
    def __init__(self, appdaemon, name, instance=0):
        self.proto = 'panasonic'
        self.commands = panasonic_dvd_s700_cmds
        self.appdaemon = appdaemon
        self.name = name
        self.instance = instance

    def send_cmd(self, repcnt, key):
        cmd = self.commands.get(key)
        if not cmd:
            return
        name, command = cmd
        self.tx_cmd(command, address=0x4004)


class Activity(object):
    def __init__(self):
        pass


config = {
    'remotes': {
        'URC3680': {
            'keys': urc3680_rc6_keys,
            'devices': (
                (1, Vizio_TV_M656G4, 'Vizio TV'),
                (2, Apple_TV_4K, 'Apple TV'),
                (3, Cisco_STB_8742, 'Set Top Box'),
                (5, Denon_AVR_S760, 'Receiver'),
                (7, Panasonic_DVD_S700, 'DVD Player'),
            )
        }
    },
}

class Harmony(hass.Hass):

    def initialize(self):
        self.log("Starting Harmony app")

        self.last_event = None
        self.repcnt = 0
        self.remotes = []

        self.read_config()

        self.listen_event(self.handle_rc6_event, 'esphome.receiver_rf', device_id=REMOTE)
        self.listen_event(self.handle_rc6_event, 'esphome.receiver_ir', device_id=REMOTE)

    def read_config(self):
        for name, remconfig in config['remotes'].items():
            remote = RemoteControl(self, name, remconfig['keys'])
            for ix, devtype, name in remconfig['devices']:
                remote.add_device(ix, devtype(self, name))
            self.remotes.append(remote)

    def handle_rc6_event(self, event_name, data, kwargs):
        a = data.get('address')
        c = data.get('command')
        m = data.get('mode')
        t = data.get('toggle')

        if m != 0:
            self.log("Unexpected mode %s, expected 0" % m)
            return

        # punched-through MUTE, redirect to Audio
        if (a, c) == (1, 0x0D):
            a = 5

        # get remote that handles this address, last added if multiple
        v = [(r, r.get_device(a)) for r in reversed(self.remotes) if r.has_device(a)]
        if not v:
            return
        remote, device = v[0]

        key = remote.key(c)
        #self.log("%s %d %s %s" % (remote.name, a, c, key))

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

        device.send_cmd(self.repcnt, key)
