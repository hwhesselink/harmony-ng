Overall:

pic

One or more remotes send 433Mhz RF codes.  The gateway receives the codes and (except for *volume*) sends them to the harmony-ng app over wifi.  The app replies to the gateway with commands to send to the devices, which the gateway then sends out over IR.

sends appropriate codes 
The app can also 

_Volume_

delay too long so vol sent directly in ESP



remote -----                                                ----- Apple TV
           |                                                |
remote ----+---> 433MHz RF ---- Kincony Gateway ---- IR ----+---- receiver
           |                           |^                   |
remote -----                           ||                   ----- DVD, etc
                                      wifi
                                       ||
                                       v|
                                   harmony-ng
