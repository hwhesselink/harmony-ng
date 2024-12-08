# Architecture

A minimal configuration consists of 1 remote controlling 1 device via 1 gateway.  For example:

```

  remote ---> 433MHz RF ---- KC868-AG gateway ----> IR ---- mini stereo set
                                    |^
                                    ||
                                   wifi
                                    ||
                                    v|
                                harmony-ng <--> Home Assistant (optional)

```

A maximal configuration has multiple remotes in multiple rooms and multiple gateways.  For example:

```

                                                                        +---- Apple TV
                                                                        |
                      +---> 433MHz RF ---- KC868-AG gateway ---> IR ----+---- receiver (room 1 devices)
                      |                           |^                    |
  room 1 remote(s) ---+                           ||                    +---- TV, DVD, etc
                      |                          wifi
                      |                           ||
  room 2 remote(s) ---+                           v|
                      |                       harmony-ng <--> Home Assistant
                      |                           |^
  etc. ---------------+                           ||
                      |                          wifi
                      |                           ||
                      |                           v|
                      +---> 433MHz RF --- KC868-AG gateway(s) --> IR --------- room 2, etc. devices

```

A remote sends IR codes over 433MHz RF (see below and [Hardware](docs/hardware.md)).  A gateway receives the codes and (except for [volume](#volume)) sends them to the harmony-ng app over wifi.  The app replies to the gateway with commands to send to the devices, which the gateway then sends out over IR.  Activities and button presses can send events to Home Assistant to trigger automations and scenes, and Home Assistant can send commands to the gateway(s) to control devices.

Any remote that uses AA or AAA batteries can send 433MHz RF codes by replacing one of the batteries with a [Nextgen transmitter](https://nextgen.us/product/remote-extender-plus-rf-transmitter-433-mhz/).  The remote's IR LED needs to be blocked so it doesn't interfere with the signals the gateway is sending.  Multiple remotes can be used, either the same, e.g. one for each couch😃, or different, e.g. with large buttons for people with poor sight or with limited buttons for use at parties.

The code is written for the Philips RC-6 IR protocol.  In theory any protocol could be used but RC-6 has a toggle bit that makes it possible to quickly distinguish between a long key hold and multiple key presses.  Harmony-ng remaps the remote's keys, so any remote that sends RC-6 can be used, but a remote that has activity keys is obviously to be preferred.  For the ultimate in configurability get a [JP1.x remote](http://www.hifi-remote.com/wiki/index.php/JP1_-_Just_How_Easy_Is_It) and use [RemoteMaster](https://sourceforge.net/projects/controlremote) to set it up as you like.  The [URC 3680 remote](https://www.oneforall.com/en-us/universal-remotes/urc-3680-essential-8-antimicrobial-remote-control) has all the buttons of the Harmony Companion plus some extra
and with this RemoteMaster [configuration](/remotemaster) is optimized for Harmony-ng and supports up to 12 activities (out-of-the-box supports 3).  The config also supports direct control of up to 8 devices in case that's ever needed.

The [Kincony KC868-AG gateway](https://www.kincony.com/esp32-rf-ir-gateway.html) is a box about the size of a Harmony Hub that connects via Wifi.  It can send and receive IR and 433MHz RF.  It has 7 IR transmitter LEDs so it works as a 360&deg; IR blaster.
It is designed to be configured using [ESPHome](https://esphome.io/index.html).

## Volume

delay too long so vol sent directly in ESP



