=== Pi

Green

or

See https://www.home-assistant.io/installation/raspberrypi, but in short:
- install raspberry pi imager
- write sd card
- start pi (ethernet!)
- access HA at http://homeassistant.local:8123
- wait for "Welcome!"

Then onboard: https://www.home-assistant.io/getting-started/onboarding/
- click "CREATE MY SMART HOME"
- fill in your info (primary user)
- set home location
- select share choices
- click "Finish"

## Install HACS:
## - download: https://www.hacs.xyz/docs/use/download/download
##   - tab OS/Supervised
##   - 1 click "my link" and "OK"
##   - In the Get HACS add-on, click Install
##   - click Start to start the add-on
##   - select the "Log" tab
##   - restart HA: click Settings in left side-panel, click 3 dots menu top right and click "Restart Home Assistant, again click "Restart Home Assistant" and then "RESTART"
##   - wait for restart
##
## Configure HACS, see https://www.hacs.xyz/docs/use/configuration/basic:
## - go to Settings > Devices & services
## - Clear your browser cache
## - click "ADD INTEGRATION" bottom right
## - search for HACS
## - acknowledge all items

Install AppDaemon
- Settings -> Add-ons
- ADD-ON STORE
- Search for "AppDaemon"
- select it
- click "Install" and check the Log tab
