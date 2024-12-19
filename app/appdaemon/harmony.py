import hassapi as hass

import asyncio, time

from remotes.sony_vl600_8001 import rm_vl600_8001_keys
from remotes.urc3680 import urc3680_rc6_keys

from devices.apple_tv_4k import sony_cmds_for_atv
from devices.cisco_stb_8742 import cisco_stb_8742_cmds
from devices.denon_avr_s760 import denon_avr_s760_cmds
from devices.panasonic_dvd_s700 import panasonic_dvd_s700_cmds
from devices.pioneer_pd_m_6_disc_changer import pioneer_pdm_6_disc_cmds
from devices.pioneer_vsx_4500s import pioneer_vsx_4500s_cmds
from devices.vizio_tv_m656g4 import vizio_tv_m656g4_cmds

LOG_LEVEL = "INFO"

# Kincony
REMOTE = 'a1e13b4a8a46c8c156cdde70ee3be970'
REMNAME = 'web_bda758'

# These (arbitrary) numbers must match the Kincony ESP config volume_up/down buttons
IRprotocols = {
    'pronto': 1,
    'lg': 2,
    'nec': 3,
    'panasonic': 4,
    'pioneer': 5,
    'rc5': 6,
    'rc6': 7,
    'samsung': 8,
    'samsung36': 9,
    'sony': 10,
}


class RemoteControl(object):
    def __init__(self, appdaemon, name, **kwargs):
        self.appdaemon = appdaemon
        self.log = appdaemon.log
        self.name = name
        self.__dict__.update(kwargs)

    def key(self, k):
        return self.keys.get(k)


class Key(object):
    """
    Representation of a device key line.

    The format is "(descr, IRcode)" where descr is a short free-form text
    describing the function as it is known on the device (for e.g. tools
    that link remote buttons to functions to use as help text), and IRcode
    is what to send to the device.

    The format of IRcode is "command" or "(command, args)" where command
    is an int, a string, or a 2-item tuple for 2-part Pioneer commands,
    as required by the relevant ESP transmit function.  The args field is a
    dict with extra parameters (e.g. "{ 'nbits': 12 }" for proto "sony").

    Command can be a string in Pronto format to override the native command
    or if the native one is unknown, in which case proto is set to "pronto".

    If command is a string but not in Pronto format it is kept as-is and
    proto is set to None so a higher-level can deal with it (e.g. call it
    if it's a method name).
    """
    def __init__(self, proto, code):
        self.proto = proto

        self.descr, code = code[0], code[1]

        if isinstance(code, str):
            if code.startswith('0000 '):
                # if code in Pronto format override native proto
                self.proto = 'pronto'
            else:
                # code may be a method name
                self.proto = None

        if isinstance(code, (list, tuple)):
            self.command = code[0]
            self.args = code[1]
        else:
            self.command = code
            self.args = {}

    def gen_tx_args(self):
        """ Generate key data formatted for ESP transmit. """
        if self.proto == None:
            return None, self.command

        proto = self.proto
        if proto in ('jvc', 'lg', 'pronto', 'samsung', 'sony'):
            cmdname = 'data'
        elif proto in ('nec', 'panasonic', 'rc5', 'rc6', 'samsung36'):
            cmdname = 'command'
        elif proto == 'pioneer':
            cmdname = 'rc_code_1'
            self.args['repeat'] = 3
            if isinstance(self.command, (list, tuple)):
                self.command, command2 = self.command
                self.args['rc_code_2'] = command2
                proto = 'pioneer2'
        rv = { cmdname: self.command }
        rv.update(self.args)
        return proto, rv


class Device(object):
    def __init__(self, appdaemon, name, address, instance):
        self.appdaemon = appdaemon
        self.name = name
        self.address = address
        self.instance = instance
        self.vol_repeats = 1
        self.vol_repeat_wait = 0
        self.keys = {}
        for k, v in self.commands.items():
            self.keys[k] = Key(self.proto, v)

    def send_key(self, key, repcnt=0, **kwargs):
        if key not in self.keys:
            return
        proto, args = self.keys[key].gen_tx_args()
        if proto == 'pronto':
            # drop any opt. args from a native proto (e.g. sony/wait)
            kwargs = {}
        elif proto == None:
            f = getattr(self, args, None)
            if f != None and callable(f):
                # args is a method, call it
                f(key, repcnt)
                return

        if proto in ('nec', 'panasonic', 'rc5', 'rc6', 'samsung36'):
            args['address'] = self.address
        args.update(kwargs)

        svc = 'esphome/esphome_%s_tx_%s' % (REMNAME, proto)
        p = args.copy()
        if proto == 'pronto':
            p['data'] = '...'
        self.appdaemon.log("SEND %s %s %s" % (key, svc, p))
        self.appdaemon.call_service(svc, **args)

    def power_on(self, key, repcnt):
        self.send_key('KEY_POWERON')

    def power_off(self, key, repcnt):
        self.send_key('KEY_POWEROFF')

class Vizio_TV_M656G4(Device):
    def __init__(self, appdaemon, name, address, instance=0):
        self.proto = 'nec'
        self.commands = vizio_tv_m656g4_cmds
        super().__init__(appdaemon, name, address, instance)

class Apple_TV_4K(Device):
    key_map = {
            'KEY_BACK': 'menu',
            'KEY_DOWN': 'down',
            'KEY_GUIDE': 'top_menu',
            'KEY_HOME': 'home',
            'KEY_LEFT': 'left',
            'KEY_MENU': 'menu',
            'KEY_NEXT': 'skip_forward',
            'KEY_OK': 'select',
            'KEY_POWEROFF': 'suspend',
            'KEY_POWERON': 'wakeup',
            'KEY_PREVIOUS': 'skip_backward',
            'KEY_RIGHT': 'right',
            'KEY_SLEEP': 'suspend',
            'KEY_UP': 'up',
            'KEY_VOLUMEDOWN': 'volume_down',
            'KEY_VOLUMEUP': 'volume_up',
    }

    def __init__(self, appdaemon, name, address, instance=0):
        self.proto = 'sony'
        self.commands = sony_cmds_for_atv
        super().__init__(appdaemon, name, address, instance)

    def atv_send(self, key, repcnt):
        if key == 'KEY_OK' and self.appdaemon.get_state('media_player.upper_living_room') not in ('idle', 'standby'):
            # if playing/paused override OK key to toggle play/pause
            self.send_key('KEY_PLAY', repcnt)
            return
        cmd = self.key_map.get(key)
        if not cmd:
            return
        print('atv_send CALLED', cmd, 'FROM', key)
        self.appdaemon.call_service("remote/send_command", entity_id=self.address, command=cmd)

    def send_key(self, key, repcnt=0, **kwargs):
        # 'wait' empirically determined for urc3680...
        if repcnt:
            super().send_key(key, wait=115)
        else:
            super().send_key(key, wait=10)

class Cisco_STB_8742(Device):
    def __init__(self, appdaemon, name, address, instance=0):
        self.proto = 'pronto'
        self.commands = cisco_stb_8742_cmds
        super().__init__(appdaemon, name, address, instance)

class Denon_AVR_S760(Device):
    def __init__(self, appdaemon, name, address, instance=0):
        self.proto = 'panasonic'
        self.commands = denon_avr_s760_cmds
        super().__init__(appdaemon, name, address, instance)
        self.vol_repeats = 2
        self.vol_repeat_wait = 5

class Panasonic_DVD_S700(Device):
    def __init__(self, appdaemon, name, address, instance=0):
        self.proto = 'panasonic'
        self.commands = panasonic_dvd_s700_cmds
        super().__init__(appdaemon, name, address, instance)

    # The S700 is a TOAD, these emulate the missing power funcs
    def power_on(self, key, repcnt):
        # Eject is not perfect but mostly does the right thing
        self.send_key('KEY_EJECT')

    def power_off(self, key, repcnt):
        if 'KEY_PLAY' in self.keys and 'KEY_POWER' in self.keys:
            self.send_key('KEY_PLAY')
            # need to use asyncio for this eventually
            time.sleep(.4)
            self.send_key('KEY_POWER')

class Pioneer_PD_M_6_Disc_Changer(Device):
    def __init__(self, appdaemon, name, address, instance=0):
        self.proto = 'pioneer'
        self.commands = pioneer_pdm_6_disc_cmds
        super().__init__(appdaemon, name, address, instance)

class Pioneer_VSX_4500S(Device):
    def __init__(self, appdaemon, name, address, instance=0):
        self.proto = 'pioneer'
        self.commands = pioneer_vsx_4500s_cmds
        super().__init__(appdaemon, name, address, instance)
        self.vol_repeats = 2
        self.vol_repeat_wait = 10


class Activity(object):
    def __init__(self, appdaemon, name, **kwargs):
        self.appdaemon = appdaemon
        self.name = name
        self.__dict__.update(kwargs)

    def start(self, cur_activity=None):
        to_start = set(i[0] for i in self.devices)
        if cur_activity:
            running = set(i[0] for i in cur_activity.devices)
            to_stop = running - to_start
            to_start = to_start - running
            cur_activity.stop(to_stop)

        voldev = self.__dict__.get('volume_device')
        for device, _ in self.devices:
            if device in to_start:
                print("START %s" % device.name)
                device.power_on(None, 1)
            if device.name == voldev:
                self.set_volume_control(device)

        for device, input in self.devices:
            if input:
                print("SET %s INPUT TO %s" % (device.name, input))
                device.send_key(input)

    def stop(self, to_stop=None):
        for device, _ in reversed(self.devices):
            if to_stop == None or device in to_stop:
                print("STOP %s" % device.name)
                device.power_off(None, 1)

    def set_volume_control(self, device):
        vol_up = device.keys['KEY_VOLUMEUP']
        vol_down = device.keys['KEY_VOLUMEDOWN']
        if vol_up.proto != vol_down.proto:
            self.log("Proto mismatch between volume UP and DOWN")
            return
        if vol_up.proto == None:
            self.log("Volume command cannot be method in set_volume_control()")
            return
        settings = {
            'proto': IRprotocols[vol_up.proto],
            'address': device.address,
            'up_int': 0,
            'down_int': 0,
            'up_str': '',
            'down_str': '',
            'len': 0,
            'repeats': device.vol_repeats,
            'repeat_wait': device.vol_repeat_wait,
        }
        settings[isinstance(vol_up.command, str) and 'up_str' or 'up_int'] = vol_up.command
        settings[isinstance(vol_down.command, str) and 'down_str' or 'down_int'] = vol_down.command
        svc = 'esphome/esphome_%s_set_volume_control' % REMNAME
        print('SET VOLUME DEVICE TO', device.name, svc, settings)
        self.appdaemon.call_service(svc, **settings)


config = {
    'devices': {
        'TV': (Vizio_TV_M656G4, 0xFB04),
        'Apple TV': (Apple_TV_4K, "remote.upper_living_room"),
        'Set Top Box': (Cisco_STB_8742, 0),
        'Receiver': (Denon_AVR_S760, 0x2A4C),
        'DVD Player': (Panasonic_DVD_S700, 0x4004),
        'CD Player': (Pioneer_PD_M_6_Disc_Changer, 0),
    },
    'remotes': {
        'Living Room': {
            'type': 'urc3680',
            'keys': urc3680_rc6_keys,
            'devices': (
                (1, 'TV'),
                (2, 'Apple TV'),
                (3, 'Set Top Box'),
                (5, 'Receiver'),
                (6, 'CD Player'),
                (7, 'DVD Player'),
            )
        },
    },
    'activities': {
        'KEY_WATCHTV': {
            'main_device': 'Apple TV',
            'volume_device': 'Receiver',
            'devices': (
                ('TV', 'INPUT_HDMI_1'),
                ('Receiver', 'INPUT_4'),
                ('Apple TV', ''),
            )
        },
        'KEY_WATCHTVHELD': {
            'main_device': 'Set Top Box',
            'volume_device': 'Receiver',
            'devices': (
                ('TV', 'INPUT_HDMI_1'),
                ('Receiver', 'INPUT_3'),
                ('Set Top Box', ''),
            )
        },
        'KEY_LISTENTOMUSIC': {
            'main_device': 'Receiver',
            'volume_device': 'Receiver',
            'devices': (
                ('Receiver', 'INPUT_1'),
            )
        },
        'KEY_LISTENTOMUSICHELD': {
            'main_device': 'Receiver',
            'volume_device': 'Receiver',
            'devices': (
                ('Receiver', 'INPUT_9'),
            )
        },
        'KEY_WATCHMOVIES': {
            'main_device': 'DVD Player',
            'volume_device': 'Receiver',
            'devices': (
                ('TV', 'INPUT_HDMI_1'),
                ('Receiver', 'INPUT_2'),
                ('DVD Player', ''),
            )
        },
        'KEY_WATCHMOVIESHELD': {
            'main_device': 'DVD Player',
            'volume_device': 'Receiver',
            'devices': (
                ('Receiver', 'INPUT_2'),
                ('DVD Player', ''),
            )
        },
    },
}

class Harmony(hass.Hass):

    def initialize(self):
        self.log("Starting Harmony app")

        self.last_event = None
        self.repcnt = 0
        self.devices = {}
        self.device_addrs = {}
        self.remotes = {}
        self.activities = {}
        self.in_device_mode = False
        self.cur_device = None
        self.cur_activity = None

        self.read_config()

        self.listen_event(self.handle_rc6_event, 'esphome.receiver_rf', device_id=REMOTE)
        self.listen_event(self.handle_rc6_event, 'esphome.receiver_ir', device_id=REMOTE)

    def read_config(self):
        for name, (cls, addr) in config['devices'].items():
            self.devices[name] = cls(self, name, addr)
        #self.log('DEVinit done')
        #self.log(self.devices['Receiver'].keys['KEY_1'])
        #self.devices['DVD Player'].send_key('KEY_POWEROFF')

        for name, conf in config['remotes'].items():
            remote = RemoteControl(self, name, **conf)
            for addr, devname in conf['devices']:
                device = self.devices.get(devname)
                if device:
                    if addr in self.device_addrs:
                        self.log("Address %d already in use, skipping %s" % (addr, devname))
                    else:
                        self.device_addrs[addr] = (remote, device)
            self.remotes[name] = remote

        for name, conf in config['activities'].items():
            conf['devices'] = [(self.devices[name], input) for name, input in
                                    conf['devices'] if name in self.devices]
            self.activities[name] = Activity(self, name, **conf)

    def handle_rc6_event(self, event_name, data, kwargs):
        a = data.get('address')
        c = data.get('command')
        m = data.get('mode')
        t = data.get('toggle')

        #self.log("%s %s %s %s" % (a, c, m, t))
        if m != 0:
            self.log("Unexpected mode %s, expected 0" % m)
            return

        if not a in self.device_addrs:
            return
        remote, device = self.device_addrs[a]

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

        if key == 'KEY_POWERSHIFT':
            self.in_device_mode = True
            self.cur_device = a
            self.cur_activity = None
            return

        if key in self.activities:
            if self.in_device_mode:
                self.in_device_mode = False
                self.cur_device = None
            if self.cur_activity != key:
                self.log("STARTING ACTIVITY %s" % key)
                self.activities[key].start(self.activities.get(self.cur_activity))
                self.cur_activity = key
            return

        if not (self.cur_activity or self.cur_device):
            return

        if self.in_device_mode:
            #if key.startswith('KEY_') and key[4] in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0'):
            #    key = 'INPUT_' + key[4]
            #self.log("SEND %s to device %s" % (key, self.cur_device))
            device.send_key(key, self.repcnt)
            return

        curact = self.activities[self.cur_activity]
        if key == 'KEY_POWER':
            curact.stop()
            self.cur_activity = None
            return

        if key == 'KEY_MUTE':
            device = curact.volume_device
        else:
            device = curact.main_device
        self.log("SEND %s to %s in %s" % (key, device, self.cur_activity))
        self.devices[device].send_key(key, self.repcnt)
