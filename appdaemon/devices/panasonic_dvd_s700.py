panasonic_dvd_s700_cmds = {
    'KEY_POWER':        ('Power', 0x0D00BCB1),
    'KEY_INFO':         ('Display', 0x0D004944),
    'KEY_EJECT':        ('Open/Close', 0x0D00808D),
    'KEY_1':            ('1', 0x0D000805),
    'KEY_2':            ('2', 0x0D008885),
    'KEY_3':            ('3', 0x0D004845),
    'KEY_4':            ('4', 0x0D00C8C5),
    'KEY_5':            ('5', 0x0D002825),
    'KEY_6':            ('6', 0x0D00A8A5),
    'KEY_7':            ('7', 0x0D006865),
    'KEY_8':            ('8', 0x0D00E8E5),
    'KEY_9':            ('9', 0x0D001815),
    'KEY_0':            ('0', 0x0D009895),
    'KEY_ENTER':        ('>=10', 0x0D00919C),
    'KEY_HOME':         ('Menu Top', 0x0D00D9D4),
    'KEY_UP':           ('Up', 0x0D00A1AC),
    'KEY_MENU':         ('Menu', 0x0D00010C),
    'KEY_LEFT':         ('Left', 0x0D00E1EC),
    'KEY_OK':           ('OK', 0x0D00414C),
    'KEY_RIGHT':        ('Right', 0x0D00111C),
    'KEY_INPUT':        ('Setup', 0x0D002924),
    'KEY_DOWN':         ('Down', 0x0D00616C),
    'KEY_LAST':         ('Return', 0x0D00818C),
    'KEY_PREVIOUS':     ('Skip back', 0x0D00929F),
    'KEY_NEXT':         ('Skip fwd', 0x0D00525F),
    'KEY_PREVIOUSHELD': ('Back', 0x0D00202D),
    'KEY_NEXTHELD':     ('Forward', 0x0D00A0AD),
    'KEY_STOP':         ('Stop', 0x0D00000D),
    'KEY_PLAY':         ('Play/Pause', 0x0D00505D),
    'KEY_PROG1':        ('Frame', 0x0D00303D),
    'KEY_EXIT':         ('Cancel', 0x0D00C1CC),
    'KEY_GREEN':        ('Subtitle', 0x0D008984),
    'KEY_PROGRAM':      ('Program', 0x0D00B2BF),
    'KEY_USB':          ('USB', 0x0D00404D),
    'KEY_REPLAY':       ('Repeat', 0x0D00313C),
    'KEY_BLUE':         ('Audio', 0x0D00CCC1),
    '#Search Mode':     ('Search Mode', 0x0D00676A),
    '#A-B Repeat':      ('A-B Repeat', 0x0D00121F),
    '#Slow':            ('Slow', 0x0D00F0FD),
    '#Random/Angle':    ('Random/Angle', 0x0D000904),
    '#Zoom':            ('Zoom', 0x0D00838E),
    '#USB Rec':         ('USB Rec', 0x0D00515C),
}

'''
Need to merge, from 176,0.csv.
Some (e.g. power on/off) don't work.

Pause	0x0D00606D
Slow <	0x0D00E0ED
Power on	0x0D007C71
Power off	0x0D00FCF1
Hp-v.s.s.	0x0D00A2AF
Play mode	0x0D00B1BC
Marker	0x0D00717C
Subtitle	0x0D00C9C4
Pause	0x0D00A9A4
Down cursor	0x0D006964
Frame <<	0x0D00E9E4
Frame >>	0x0D001914
Fl disp.	0x0D009994
Vss	0x0D007974
Group	0x0D00070A
Audio only	0x0D00878A
Page	0x0D00A7AA
Text	0x0D00171A
'''

'''
POWERON codes that don't work...

"0000 0048 0048 0000 00C1 00C2 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0030 0031 0886 00C1 00C1 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0030 0031 0886 00C1 00C1 0031 0030 0031 0030 0031 0030 0031 0030 0031 0010 0031 0030 0031 0030 0031 0030 0031 0030 0031 0030 0031 0091 0031 0091 0031 0010 0031 0030 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0091 0031 0030 0031 00C2"
"0000 006F 0000 0032 0080 0042 0010 0010 0010 0031 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0031 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0031 0010 0010 0010 0031 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0031 0010 0031 0010 0031 0010 0031 0010 0031 0010 0010 0010 0010 0010 0010 0010 0031 0010 0031 0010 0031 0010 0031 0010 0010 0010 0010 0010 0031 0010 0AE5"
"0000 0070 0000 0032 0080 0040 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0030 0010 0030 0010 0010 0010 0030 0010 0030 0010 0010 0010 0ACE"
"0000 0070 0000 0032 0080 0040 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0030 0010 0030 0010 0ACE"
"0000 0070 0000 0032 0080 0040 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0010 0010 0030 0010 0010 0010 0030 0010 0ACE"
"0000 0070 0000 0032 0080 0040 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0030 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0030 0010 0030 0010 0ACE"
"0000 0070 0000 0032 0080 0040 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0030 0010 0ACE"
"0000 0070 0000 0032 0080 0041 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0AB6"
"0000 0070 0000 0032 0080 0041 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0030 0010 0AB6"
"0000 0070 0000 0032 0082 0041 0011 0010 0011 0030 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0011 0030 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0011 0030 0011 0010 0011 0010 0011 0030 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0011 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0010 0010 0030 0010 0010 0010 0030 0011 0AEC"
"0000 0070 0000 003A 0080 0040 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0ACD"
"0000 0070 0000 003A 0081 0041 000F 000F 000F 0030 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 0030 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 0030 000F 000F 000F 000F 000F 000F 000F 0030 000F 000F 000F 000F 000F 0030 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 000F 0030 000F 0030 000F 0030 000F 0030 000F 0030 000F 000F 000F 000F 000F 000F 000F 0030 000F 0030 000F 000F 000F 0030 000F 0030 000F 0030 000F 0030 000F 0ABD"
"0000 0070 0002 0032 0006 0031 0010 0AB7 0080 0040 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0031 0010 0030 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0031 0010 0010 0010 0010 0010 0010 0010 0031 0010 0AB7"
"0000 0071 0000 0032 0080 003F 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0010 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0030 0010 0A98"
"0000 0071 0000 0032 0080 0040 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0030 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 0030 0010 0010 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0030 0010 0010 0010 0030 0010 0030 0010 0010 0010 0030 0010 0030 0010 0010 0010 0A9C"
"0000 0073 0014 0000 0060 0020 0010 0020 0010 0010 0010 0010 0010 0020 0020 0010 0010 0010 0010 0010 0010 0010 0010 0010 0020 0020 0010 0010 0010 0010 0010 0010 0020 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 09B7"
"0000 0073 0014 0000 0060 0020 0010 0020 0010 0010 0010 0010 0030 0030 0020 0010 0010 0010 0010 0010 0010 0010 0010 0010 0020 0020 0010 0010 0010 0010 0010 0010 0020 0010 0010 0010 0010 0010 0010 0010 0010 0010 0010 09B7"
"0000 006D 0022 0002 0155 00AA 0015 0015 0015 0015 0015 0040 0015 0040 0015 0040 0015 0040 0015 0040 0015 0015 0015 0040 0015 0040 0015 0015 0015 0015 0015 0015 0015 0015 0015 0015 0015 0040 0015 0015 0015 0040 0015 0040 0015 0015 0015 0040 0015 0040 0015 0040 0015 0040 0015 0040 0015 0015 0015 0015 0015 0040 0015 0015 0015 0015 0015 0015 0015 0015 0015 05ED 0155 0055 0015 0E47"
'''
