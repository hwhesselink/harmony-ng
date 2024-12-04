# Architecture

The overall configuration is:

```

    remote ----+                                                +---- Apple TV
               |                                                |
    remote ----+---> 433MHz RF ---- Kincony gateway ---> IR ----+---- receiver
               |                           |^                   |
    remote ----+                           ||                   +---- DVD, etc
                                          wifi
                                           ||
                                           v|
                                       harmony-ng
                                           |^
                                           ||
                                           v|
                                     Home Assistant (optional)

```

One or more remotes send 433MHz RF codes.  The gateway receives the codes and (except for [volume](#volume)) sends them to the harmony-ng app over wifi.  The app replies to the gateway with commands to send to the devices, which the gateway then sends out over IR.  If configured with Home Assistant the app can also execute Home Assistant actions.

Any remote that uses AA or AAA batteries can send 433MHz RF codes by replacing one of the batteries with a [Nextgen transmitter](https://nextgen.us/product/remote-extender-plus-rf-transmitter-433-mhz/).  The remote's IR LED needs to be blocked so it doesn't interfere with the signals the gateway is sending.  Multiple remotes can be used, either the same, e.g. one for each couch😃, or different, e.g. with large buttons for people with poor sight; with limited buttons to use at parties.

The [Kincony gateway](https://www.kincony.com/esp32-rf-ir-gateway.html) is designed to be configured using [ESPHome](https://esphome.io/index.html).

## Volume

delay too long so vol sent directly in ESP



