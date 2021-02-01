# DietPi (Pi Zero W)
- Turn on WiFi for first boot - see https://dietpi.com/phpbb/viewtopic.php?t=9
  Worked OK
- Turn on Ethernet over USB - see https://www.thepolyglotdeveloper.com/2016/06/connect-raspberry-pi-zero-usb-cable-ssh/

  Need another step, not sure what, to get an IP address, maybe manual?
- To get at its console use "ssh root@dietpi" and pwd of "dietpi"
- Install node - see https://www.thepolyglotdeveloper.com/2018/03/install-nodejs-raspberry-pi-zero-w-nodesource/

  last node version for armv6l (as used by Pi zero) is 11

  add /usr/local/node/bin to the global path by editing /etc/profile
