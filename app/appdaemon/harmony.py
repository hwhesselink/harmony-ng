import hassapi as hass

import asyncio, time

from devices.apple import sony_cmds_for_atv
from devices.cisco import cisco_stb_8742
from devices.denon import denon_avr_s760
from devices.jvc import jvc_dvd_cmds
from devices.panasonic import panasonic_dvd_s700
from devices.pioneer import pioneer_pdm_6_disc, pioneer_vsx_4500s
from devices.vizio import vizio_tv_m656g4

LOG_LEVEL = "INFO"


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

rc6_button_names = {
    0x00: 'KEY_0',
    0x01: 'KEY_1',
    0x02: 'KEY_2',
    0x03: 'KEY_3',
    0x04: 'KEY_4',
    0x05: 'KEY_5',
    0x06: 'KEY_6',
    0x07: 'KEY_7',
    0x08: 'KEY_8',
    0x09: 'KEY_9',
    0x0A: 'KEY_LAST',
    0x0C: 'KEY_POWER',
    0x0D: 'KEY_MUTE',
    0x0F: 'KEY_INFO',
    0x10: 'KEY_VOLUMEUP',
    0x11: 'KEY_VOLUMEDOWN',
    0x20: 'KEY_CHANNELUP',
    0x21: 'KEY_CHANNELDOWN',
    0x28: 'KEY_NEXT',
    0x2B: 'KEY_PREVIOUS',
    0x2C: 'KEY_PLAY',
    0x30: 'KEY_PAUSE',
    0x31: 'KEY_STOP',
    0x37: 'KEY_RECORD',
    0x38: 'KEY_INPUT',
    0x41: 'KEY_BACK',
    0x42: 'KEY_EJECT',
    0x4B: 'KEY_PREVIOUSHELD',
    0x4C: 'KEY_NEXTHELD',
    0x54: 'KEY_HOME',
    0x57: 'KEY_MENU',
    0x58: 'KEY_UP',
    0x59: 'KEY_DOWN',
    0x5A: 'KEY_LEFT',
    0x5B: 'KEY_RIGHT',
    0x5C: 'KEY_OK',
    0x6D: 'KEY_RED',
    0x6E: 'KEY_GREEN',
    0x6F: 'KEY_YELLOW',
    0x70: 'KEY_BLUE',
    0x71: 'KEY_BACKLIGHT',
    0x76: 'KEY_PROG1',
    0x77: 'KEY_PROG2',
    0x79: 'KEY_PROG3',
    0x92: 'KEY_ENTER',
    0x9F: 'KEY_EXIT',
    0xCC: 'KEY_GUIDE',
    0xD2: 'KEY_LIST',
    0xD9: 'KEY_MINUS',
    0xE0: 'KEY_WATCHTV',
    0xE1: 'KEY_LISTENTOMUSIC',
    0xE2: 'KEY_WATCHMOVIES',
    0xE3: 'KEY_WATCHTVHELD',
    0xE4: 'KEY_LISTENTOMUSICHELD',
    0xE5: 'KEY_WATCHMOVIESHELD',
    0xE6: 'KEY_WATCHTVSHIFT',
    0xE7: 'KEY_LISTENTOMUSICSHIFT',
    0xE8: 'KEY_WATCHMOVIESSHIFT',
    0xF0: 'KEY_POWERSHIFT',
    0xF1: 'KEY_LIVE',
    0xF2: 'KEY_REPLAY',
}

class Room(object):
    def __init__(self, appdaemon, name, **kwargs):
        self.appdaemon = appdaemon
        self.log = appdaemon.log
        self.name = name
        self.gw_id = kwargs['gw_id']
        self.gw_name = kwargs['gw_name']
        self._set_devices(kwargs.get('devices', {}))
        self._set_activities(kwargs.get('activities', {}))

        self.in_device_mode = False
        self.cur_device = None
        self.cur_activity = None

    def _set_devices(self, devices):
        self.devices = {}
        self.device_names = {}
        for ix, (name, cls, addr) in devices.items():
            self.device_names[name] = self.devices[ix] = cls(self, name, addr)

    def _set_activities(self, activities):
        self.activities = {}
        for activity, config in activities.items():
            config['devices'] = [(self.device_names[name], input) for name, input in config['devices'] if name in self.device_names]
            config['main_device'] = self.device_names.get(config['main_device'])
            config['volume_device'] = self.device_names.get(config['volume_device'])
            self.activities[activity] = Activity(self, activity, **config)
            #self.log(self.activities[activity])

    def __str__(self):
        return "Room: %s (gw_id=%s, gw_name=%s)\n  Activities: %s\n  Devices: %s" % (
                    self.name, self.gw_id, self.gw_name,
                    ', '.join(map(str, sorted(self.activities.keys()))),
                    ', '.join(sorted("%s (%d)" % (d.name, i) for (i, d) in self.devices.items()))
                )

    def set_device_mode(self, addr):
        self.in_device_mode = True
        self.cur_activity = None
        self.cur_device = addr

    def set_activity_mode(self, activity):
        if self.in_device_mode:
            self.in_device_mode = False
            self.cur_device = None
        activity = self.activities.get(activity)
        if activity and self.cur_activity != activity:
            self.log("STARTING ACTIVITY %s" % activity.name)
            activity.start(self.cur_activity)
            self.cur_activity = activity

    def active(self):
        return (self.cur_activity != None or self.cur_device != None)

    def send(self, address, key, repcnt):
        #print('SEND IN ROOM:', self)
        if self.in_device_mode:
            device = self.devices.get(address)
            if device:
                device.send_key(key, repcnt)
            return

        if key == 'KEY_POWER':
            self.cur_activity.stop()
            self.cur_activity = None
            return

        if key == 'KEY_MUTE':
            device = self.cur_activity.volume_device
        else:
            device = self.cur_activity.main_device
        #self.log("SEND %s to %s in %s" % (key, device, self.cur_activity))
        device.send_key(key, repcnt)


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
        args = {}

        self.descr, code = code[0], code[1]

        if isinstance(code, str):
            if code.startswith('0000 '):
                # if code in Pronto format override native proto
                proto = 'pronto'
            else:
                # code may be a method name, keep as-is
                proto = None

        if isinstance(code, (list, tuple)) and isinstance(code[1], dict):
            code, args = code[0], code[1]

        cmdname = None
        if proto in ('jvc', 'lg', 'pronto', 'samsung', 'sony'):
            cmdname = 'data'
        elif proto in ('nec', 'panasonic', 'rc5', 'rc6', 'samsung36'):
            cmdname = 'command'
        elif proto == 'pioneer':
            cmdname = 'rc_code_1'
            args['repeat'] = 3
            if isinstance(code, (list, tuple)):
                code, args['rc_code_2'] = code
                proto = 'pioneer2'

        self.proto = proto
        self.command = code
        self.args = args

        self.espcmd = { cmdname: code }
        self.espcmd.update(args)

    def get_esp_cmd(self):
        if self.proto == None:
            return None, self.command
        return self.proto, self.espcmd


class ServiceCallSequence(object):
    def __init__(self, appdaemon):
        self.appdaemon = appdaemon
        self.log = appdaemon.log
        self.power_on_delay = 0
        self.commands = []

    def add(self, svc_data, device=None):
        if not svc_data:
            return
        if not isinstance(svc_data, (list, tuple)):
            # must be one or more instances of (svc, data)
            return
        if not isinstance(svc_data[0], (list, tuple)):
            # if single instance, make list
            svc_data = [svc_data]
        for sa in svc_data:
            svc, args = sa
            self.commands.append({ svc: args })
            if device:
                # keep track of maximum power-on delay
                self.power_on_delay = max(self.power_on_delay, device.power_on_delay)

    def add_wait(self):
        if self.power_on_delay:
            self.commands.append({ 'sleep': self.power_on_delay })
        self.power_on_delay = 0

    def send(self):
        self.log('ServiceCallSequence SEND')
        self.appdaemon.run_sequence(self.commands)


class Device(object):
    def __init__(self, room, name, address, instance):
        self.room = room
        self.appdaemon = room.appdaemon
        self.log = room.appdaemon.log
        self.name = name
        self.address = address
        self.instance = instance
        self.power_on_delay = 0
        self.input_delay = 0
        self.inter_device_delay = 0
        self.vol_repeats = 1
        self.vol_repeat_wait = 0
        self.keys = {}
        for k, v in self.commands.items():
            self.keys[k] = Key(self.proto, v)

    def __str__(self):
        return "Device %s" % self.name

    def gen_key_svc(self, key, repcnt=0, **kwargs):
        if key not in self.keys:
            return None
        proto, args = self.keys[key].get_esp_cmd()
        if proto == 'pronto':
            # drop any opt. args from a native proto (e.g. sony/wait)
            kwargs = {}
        elif proto == None:
            f = getattr(self, args, None)
            if f != None and callable(f):
                # args is a method, call it
                return f(key, repcnt)

        if proto in ('nec', 'panasonic', 'rc5', 'rc6', 'samsung36'):
            args['address'] = self.address
        args.update(kwargs)

        svc = 'esphome/%s_tx_%s' % (self.room.gw_name, proto)
        return svc, args

    def send_key(self, key, repcnt=0, **kwargs):
        svc, args = self.gen_key_svc(key, repcnt, **kwargs)
        if not svc:
            return
        p = args.copy()
        d = p.get('data')
        if isinstance(d, str) and len(d) > 50:
            p['data'] = d[:45].strip() + ' ... '
        #self.log("SEND %s %s %s" % (key, svc, p))
        self.appdaemon.call_service(svc, **args)

    def power_on(self, key, repcnt):
        return self.gen_key_svc('KEY_POWERON')

    def power_off(self, key, repcnt):
        return self.gen_key_svc('KEY_POWEROFF')

class Vizio_TV_M656G4(Device):
    def __init__(self, room, name, address, instance=0):
        self.proto = 'nec'
        self.commands = vizio_tv_m656g4
        super().__init__(room, name, address, instance)
        self.power_on_delay = 8
        self.input_delay = 0
        self.inter_device_delay = 0.5

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
            'KEY_POWEROFF': 'turn_off',
            'KEY_POWERON': 'turn_on',
            'KEY_PREVIOUS': 'skip_backward',
            'KEY_RIGHT': 'right',
            'KEY_SLEEP': 'turn_off',
            'KEY_UP': 'up',
            'KEY_VOLUMEDOWN': 'volume_down',
            'KEY_VOLUMEUP': 'volume_up',
    }

    def __init__(self, room, name, address, instance=0):
        self.proto = 'sony'
        self.commands = sony_cmds_for_atv
        self.remote = 'remote.' + address
        self.player = 'media_player.' + address
        super().__init__(room, name, address, instance)
        self.power_on_delay = 1.5
        self.input_delay = 0
        self.inter_device_delay = 0.5

    def atv_send(self, key, repcnt):
        #self.appdaemon.log("atv_send KEY %s, STATE %s" % (key, self.appdaemon.get_state(self.player)))
        if key == 'KEY_OK' and self.appdaemon.get_state(self.player) not in ('idle', 'standby'):
            # if playing/paused override OK key to toggle play/pause
            return self.gen_key_svc('KEY_PLAY', repcnt)
        cmd = self.key_map.get(key)
        if not cmd:
            return None
        if key == 'KEY_POWERON':
            return [("remote/send_command", { 'entity_id': self.remote, 'command': cmd }),
                   ("homeassistant/reload_config_entry", { 'entity_id': self.player })]
        #self.appdaemon.log("atv_send REMOTE SEND %s to %s" % (cmd, self.remote))
        return "remote/send_command", { 'entity_id': self.remote, 'command': cmd }

    '''
    def send_key(self, key, repcnt=0, **kwargs):
        # 'wait' empirically determined for urc3680...
        if repcnt:
            super().send_key(key, wait=115)
        else:
            super().send_key(key, wait=10)
    '''

class Cisco_STB_8742(Device):
    def __init__(self, room, name, address, instance=0):
        self.proto = 'pronto'
        self.commands = cisco_stb_8742
        super().__init__(room, name, address, instance)
        self.power_on_delay = 1.5
        self.input_delay = 0
        self.inter_device_delay = 0.5

class Denon_AVR_S760(Device):
    def __init__(self, room, name, address, instance=0):
        self.proto = 'panasonic'
        self.commands = denon_avr_s760
        super().__init__(room, name, address, instance)
        self.vol_repeats = 2
        self.vol_repeat_wait = 5

class JVC_DVD(Device):
    def __init__(self, room, name, address, instance=0):
        self.proto = 'jvc'
        self.commands = jvc_dvd_cmds
        super().__init__(room, name, address, instance)

class Panasonic_DVD_S700(Device):
    def __init__(self, room, name, address, instance=0):
        self.proto = 'panasonic'
        self.commands = panasonic_dvd_s700
        super().__init__(room, name, address, instance)

    # The S700 is a TOAD, these emulate the missing power funcs
    def power_on(self, key, repcnt):
        # Eject is not perfect but mostly does the right thing
        return self.gen_key_svc('KEY_EJECT')

    def power_off(self, key, repcnt):
        if 'KEY_PLAY' in self.keys and 'KEY_POWER' in self.keys:
            return (self.gen_key_svc('KEY_PLAY'), self.gen_key_svc('KEY_POWER'))

class Pioneer_PD_M_6_Disc_Changer(Device):
    def __init__(self, room, name, address, instance=0):
        self.proto = 'pioneer'
        self.commands = pioneer_pdm_6_disc
        super().__init__(room, name, address, instance)

class Pioneer_VSX_4500S(Device):
    def __init__(self, room, name, address, instance=0):
        self.proto = 'pioneer'
        self.commands = pioneer_vsx_4500s
        super().__init__(room, name, address, instance)
        self.vol_repeats = 2
        self.vol_repeat_wait = 10


class Activity(object):
    def __init__(self, room, name, **kwargs):
        self.room = room
        self.appdaemon = room.appdaemon
        self.log = room.appdaemon.log
        self.name = name
        self.main_device = None
        self.volume_device = None
        self.__dict__.update(kwargs)

    def __str__(self):
        return "Activity: %s (main device: %s, volume device: %s)\n  Devices: %s" % (
                    self.name, self.main_device, self.volume_device,
                    ', '.join(sorted("%s[%s]" % (d.name, i) for (d, i) in self.devices))
                )

    def start(self, cur_activity=None):
        to_start = set(i[0] for i in self.devices)
        if cur_activity:
            running = set(i[0] for i in cur_activity.devices)
            to_stop = running - to_start
            to_start = to_start - running
            cur_activity.stop(to_stop)

        start_cmds = ServiceCallSequence(self.appdaemon)

        for device, _ in self.devices:
            if device in to_start:
                self.log("START %s" % device.name)
                start_cmds.add(device.power_on(None, 1), device)
        start_cmds.add(self.set_volume_control())
        start_cmds.add_wait()

        for device, input in self.devices:
            if input:
                print("SET %s INPUT TO %s" % (device.name, input))
                start_cmds.add(device.gen_key_svc(input))

        start_cmds.send()

    def stop(self, to_stop=None):
        stop_cmds = ServiceCallSequence(self.appdaemon)
        for device, _ in reversed(self.devices):
            if to_stop == None or device in to_stop:
                print("STOP %s" % device.name)
                stop_cmds.add(device.power_off(None, 1))
        stop_cmds.send()

    def set_volume_control(self):
        device = self.volume_device
        if not device:
            return None
        vol_up = device.keys['KEY_VOLUMEUP']
        vol_down = device.keys['KEY_VOLUMEDOWN']
        if vol_up.proto != vol_down.proto:
            self.log("Proto mismatch between volume UP and DOWN")
            return None
        if vol_up.proto == None:
            self.log("Volume command cannot be method in set_volume_control()")
            return None
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
        svc = 'esphome/%s_set_volume_control' % self.room.gw_name
        self.appdaemon.log("SET VOLUME DEVICE TO %s %s %s" % (device.name, svc, settings))
        return svc, settings


# The 'devices' number must match the RC-6 address sent by the remote(s)
config = {
    'rooms': {
        'Upper Living Room': {
            'gw_id': 'a1e13b4a8a46c8c156cdde70ee3be970',
            'gw_name': 'esphome_web_bda758',
            'devices': {
                1: ('TV', Vizio_TV_M656G4, 0xFB04),
                2: ('Apple TV', Apple_TV_4K, "upper_living_room"),
                3: ('Set Top Box', Cisco_STB_8742, 0),
                5: ('Receiver', Denon_AVR_S760, 0x2A4C),
                7: ('DVD Player', Panasonic_DVD_S700, 0x4004),
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
        },
        'TV Room': {
            'gw_id': '9d97667d41c1264f6e794b3a96af88e6',
            'gw_name': 'tv_room',
            'devices': {
                9: ('TV', Vizio_TV_M656G4, 0xFB04),
                10: ('Apple TV', Apple_TV_4K, "tv_room"),
                11: ('Set Top Box', Cisco_STB_8742, 0),
                13: ('Receiver', Pioneer_VSX_4500S, 0),
                14: ('CD Player', Pioneer_PD_M_6_Disc_Changer, 0),
                15: ('DVD Player', JVC_DVD, 0),
            },
            'activities': {
                'KEY_WATCHTV': {
                    'main_device': 'Apple TV',
                    'volume_device': 'TV',
                    'devices': (
                        ('TV', 'INPUT_HDMI_2'),
                        ('Apple TV', ''),
                    )
                },
                'KEY_WATCHTVHELD': {
                    'main_device': 'Set Top Box',
                    'volume_device': 'TV',
                    'devices': (
                        ('TV', 'INPUT_HDMI_1'),
                        ('Set Top Box', ''),
                    )
                },
                'KEY_LISTENTOMUSIC': {
                    'main_device': 'CD Player',
                    'volume_device': 'Receiver',
                    'devices': (
                        ('Receiver', 'INPUT_CD'),
                        ('CD Player', ''),
                    )
                },
                'KEY_LISTENTOMUSICHELD': {
                    'main_device': 'Receiver',
                    'volume_device': 'Receiver',
                    'devices': (
                        ('Receiver', 'INPUT_TUNER'),
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
        },
    },
}

class Harmony(hass.Hass):

    def initialize(self):
        self.log("Starting Harmony app")

        self.last_event = None
        self.repcnt = 0
        self.room_addrs = {}

        self.read_config()

    def read_config(self):
        for name, conf in config['rooms'].items():
            room = Room(self, name, **conf)
            for addr in room.devices:
                if addr in self.room_addrs:
                    self.log("%s: address %d already in use in room %s, ignoring" % (name, addr, self.room_addrs[addr].name))
                else:
                    self.room_addrs[addr] = room
            self.listen_event(self.handle_rc6_event, 'esphome.receiver_rf', device_id=room.gw_id)
            self.listen_event(self.handle_rc6_event, 'esphome.receiver_ir', device_id=room.gw_id)
            #self.log(room)

    def handle_rc6_event(self, event_name, data, kwargs):
        a = data.get('address')
        c = data.get('command')
        m = data.get('mode')
        t = data.get('toggle')
        #self.log("EVENT %s %s %s %s" % (a, c, m, t))

        if m != 0:
            self.log("Unexpected mode %s, expected 0" % m)
            return

        # IF SAME EVENT BUT DIFFERENT KINCONY, DROP.  NOTE may miss if intermingled with other remote?
        # something here

        key = rc6_button_names.get(c)
        #self.log("KEY %s" % key)

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

        room = self.room_addrs.get(a)
        if not room:
            return
        #self.log("ROOM %s" % room.name)

        if key == 'KEY_POWERSHIFT':
            room.set_device_mode(a)
            return

        if key in room.activities:
            room.set_activity_mode(key)
            return

        if not room.active():
            return

        room.send(a, key, self.repcnt)
