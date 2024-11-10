import hassapi as hass

import asyncio, time

LOG_LEVEL = "INFO"

# Kincony
REMOTE = 'a1e13b4a8a46c8c156cdde70ee3be970'

LONG_PRESS_COUNT = 4


'''
event_type: esphome.receiver_rf
data:
  device_id: a1e13b4a8a46c8c156cdde70ee3be970

        cmd = pan_cmds.get(key)
        if cmd:
            self.call_service('esphome/esphome_web_bda758_tx_panasonic', address=0x4004, command=cmd)
'''

urc3680_rc6_keys = {
    (0, 0, 0): { 'press': 'KEY_0' },
    (0, 0, 1): { 'press': 'KEY_1' },
    (0, 0, 2): { 'press': 'KEY_2' },
    (0, 0, 3): { 'press': 'KEY_3' },
    (0, 0, 4): { 'press': 'KEY_4' },
    (0, 0, 5): { 'press': 'KEY_5' },
    (0, 0, 6): { 'press': 'KEY_6' },
    (0, 0, 7): { 'press': 'KEY_7' },
    (0, 0, 8): { 'press': 'KEY_8' },
    (0, 0, 9): { 'press': 'KEY_9' },
    (0, 0, 10): { 'press': 'KEY_AGAIN' },
    (0, 0, 12): { 'press': 'KEY_POWER' },
    (0, 0, 13): { 'press': 'KEY_MUTE' },
    (0, 0, 15): { 'press': 'KEY_INFO' },
    (0, 0, 16): { 'press': 'KEY_VOLUMEUP' },
    (0, 0, 17): { 'press': 'KEY_VOLUMEDOWN' },
    (0, 0, 32): { 'press': 'KEY_CHANNELUP' },
    (0, 0, 33): { 'press': 'KEY_CHANNELDOWN' },
    (0, 0, 40): { 'press': 'KEY_NEXT' },
    (0, 0, 43): { 'press': 'KEY_PREVIOUS' },
    (0, 0, 44): { 'press': 'KEY_PLAYPAUSE' },
    (0, 0, 49): { 'press': 'KEY_STOP' },
    (0, 0, 55): { 'press': 'KEY_RECORD' },
    (0, 0, 56): { 'press': 'KEY_SELECT (or KEY_MODE)' },
    (0, 0, 65): { 'press': 'KEY_EXIT or KEY_BACK' },
    (0, 0, 66): { 'press': 'KEY_EJECT' },
    (0, 0, 75): { 'press': 'KEY_PRVHELD' },
    (0, 0, 76): { 'press': 'KEY_FWDHELD' },
    (0, 0, 84): { 'press': 'KEY_HOME or KEY_MENU' },
    (0, 0, 88): { 'press': 'KEY_UP' },
    (0, 0, 89): { 'press': 'KEY_DOWN' },
    (0, 0, 90): { 'press': 'KEY_LEFT' },
    (0, 0, 91): { 'press': 'KEY_RIGHT' },
    (0, 0, 92): { 'press': 'KEY_OK' },
    (0, 0, 109): { 'press': 'KEY_RED' },
    (0, 0, 110): { 'press': 'KEY_GREEN' },
    (0, 0, 111): { 'press': 'KEY_YELLOW' },
    (0, 0, 112): { 'press': 'KEY_BLUE' },
    (0, 0, 118): { 'press': 'KEY_PROG1' },
    (0, 0, 119): { 'press': 'KEY_PROG2' },
    (0, 0, 121): { 'press': 'KEY_PROG3' },
    (0, 0, 204): { 'press': 'KEY_EPG' },
    (0, 0, 217): { 'press': 'KEY_MINUS' }
}

pan_cmds = {
    'KEY_STOP': 0x0D00808D,
    'KEY_1': 0x0D000805,
    'KEY_2': 0x0D008885,
    'KEY_3': 0x0D004845,
    'KEY_4': 0x0D00C8C5,
    'KEY_5': 0x0D002825,
    'KEY_6': 0x0D00A8A5,
    'KEY_7': 0x0D006865,
    'KEY_8': 0x0D00E8E5,
    'KEY_9': 0x0D001815,
    'KEY_0': 0x0D009895,
    'KEY_MINUS': 0x0D00919C,
    'KEY_MENU': 0x0D00D9D4,
    'KEY_UP': 0x0D00A1AC,
    'KEY_LEFT': 0x0D00E1EC,
    'KEY_OK': 0x0D00414C,
    'KEY_RIGHT': 0x0D00111C,
    'KEY_DOWN': 0x0D00616C,
    'KEY_BACK': 0x0D00818C,
    'KEY_PREVIOUS': 0x0D00202D,
    'KEY_NEXT': 0x0D00A0AD,
    'KEY_PLAYPAUSE': 0x0D00505D,
    'KEY_AGAIN': 0x0D00313C,
    'KEY_EXIT': 0x0D00C1CC,
    'KEY_POWER': 0x0D00BCB1
}

class Activity(object):
    def __init__(self):
        pass

class Device(object):
    def __init__(self):
        pass

class RemoteControl(object):
    def __init__(self):
        pass

class Harmony(hass.Hass):

    def initialize(self):
        self.log("Starting Harmony app")

        self.cur_toggle = -1
        self.cur_event = None
        self.cur_keys = {}
        self.event_occurred = 0
        self.long_press = False
        self.long_press_key = None
        self.repcnt = 0
        self.rephandle = None

        self.listen_event(self.handle_remote_event, 'esphome.receiver_rf', device_id=REMOTE)

    def do_keypress(self, kwargs):
        self.cur_event = None
        self.repcnt = 0
        self.log("%s (%d)" % (kwargs['keypress'], self.repcnt))
        self.set_textvalue("input_text.remote_command", "%s (%d)" % (kwargs['keypress'], self.repcnt))

    def handle_remote_event(self, event_name, data, kwargs):
        a = data.get('address', 0)
        c = data.get('command', 0)
        m = data.get('mode', 0)
        t = data.get('toggle')

        if c == 32:
            #self.log('PV+')
            self.call_service('esphome/esphome_web_bda758_tx_panasonic_x2', address=0x2A4C, command=0x0280E86A)
            #self.call_service('button/press', entity_id='button.esphome_web_bda758_denon_paup')
        return

        self.log("%s %s %s %s" % (m, a, c, t))
        # we got a key press, cancel an outstanding timer
        if self.rephandle:
            if self.timer_running(self.rephandle):
                self.log("CANCEL TIMER")
                self.cancel_timer(self.rephandle)
            self.rephandle = None

        # unknown keypress, ignore
        k = self.cur_keys = urc3680_rc6_keys.get((m, a, c), {})
        if not k:
            self.set_textvalue("input_text.remote_command", '')
            return

        pressed = k['press']

        self.log("%s %s %s %s %s" % (m, a, c, t, k))

        # no long press value, process immediately
        if k.get('long_press') == None:
            self.log('PRESSED ' + pressed)
            self.set_textvalue("input_text.remote_command", pressed)
            return

        # track repeating key
        if (m, a, c, t) == self.cur_event:
            self.repcnt += 1
            #if self.repcnt > LONG_PRESS_COUNT:
            #    return
            if self.repcnt >= LONG_PRESS_COUNT:
                self.log('LONG PRESSED ' + k['long_press'])
                self.set_textvalue("input_text.remote_command", k['long_press'])
            return

        self.cur_event = (m, a, c, t)
        self.repcnt = 0
        self.log("WAIT IF REPEAT " + pressed)
        self.rephandle = self.run_in(self.do_keypress, 0.15, keypress=pressed)
