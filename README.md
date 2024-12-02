[I'll be adding a proper readme/user guide soon!]

This is a replacement for the Logitech Harmony Hub, which has been discontinued.  
It works well and I've retired the original Hub.

I'm using it with a:

- [URC3680](https://www.oneforall.com/en-us/universal-remotes/urc-3680-essential-8-antimicrobial-remote-control) universal remote
- [Kincony KC868-AG](https://www.kincony.com/esp32-rf-ir-gateway.html) RF and IR gateway
- [Nextgen](https://nextgen.us/product/remote-extender-plus-rf-transmitter-433-mhz) 433MHz transmitter

to control:

- Vizio TV
- Denon [AVR-S760H](https://www.denon.com/en-us/product/av-receivers/avr-s760h/300392-new.html) receiver
- Panasonic CD/DVD player
- Apple TV
- Cox Cisco set top box
- [Lyrion Music Server](https://lyrion.org) (formerly Logitech Media Server) as input to the receiver
- activities in [Home Assistant ](https://www.home-assistant.io)

The code runs in [Appdaemon](https://appdaemon.readthedocs.io/en/latest) and the gateway is configured using [ESPHome](https://esphome.io/index.html).  
