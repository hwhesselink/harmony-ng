[I'll be adding a proper readme/user guide soon!  In the meantime see the [Architecture](/docs/architecture.md) page]

This is a replacement for the Logitech Harmony Hub, which has been discontinued.  
It works well and I've retired the original Hub.

I'm using it with a:

- [URC 3680](https://www.oneforall.com/en-us/universal-remotes/urc-3680-essential-8-antimicrobial-remote-control) universal remote
- [Kincony KC868-AG](https://www.kincony.com/esp32-rf-ir-gateway.html) RF and IR gateway
- [Nextgen](https://nextgen.us/product/remote-extender-plus-rf-transmitter-433-mhz) 433MHz transmitter

to control:

- Vizio TVs
- Denon [AVR-S760H](https://www.denon.com/en-us/product/av-receivers/avr-s760h/300392-new.html) receiver
- Pioneer Receiver
- Panasonic CD/DVD player
- JVC VHS/DVD player
- Apple TVs
- Cox Cisco set top boxes
- [Lyrion Music Server](https://lyrion.org) (formerly Logitech Media Server)
- automations and scenes in [Home Assistant ](https://www.home-assistant.io)

This setup supports up to 12 activities with up to 256 devices.  For the rare occasion a device needs to be addressed directly the URC 3680 remote can control up to 8 (likely 16 with a bit of code, but not tested).

It is trivial to add a device if its IR codes are known, slightly more work if the codes need to be learned but the Kincony can be used for that.

Any remote that puts out Philips RC-6 IR can be used but the JP1.x programmable universal ones with activity buttons are ideal.

The code runs in [Appdaemon](https://appdaemon.readthedocs.io/en/latest) and the gateway is configured using [ESPHome](https://esphome.io/index.html).  I have Appdaemon and ESPHome running in my Home Assistant which makes integration and interaction a breeze.  If you don't have Home Assistant (you should😃!) both can run standalone.  Alternatively you can install Home Assistant on a RaspberryPi (minimum 3B) just for this.
