# fellsafe-uhf

## What is it?
An open-source hardware and software solution to running club level fell racing events safely and accurately.

## Why?
There are many commercial and DIY systems around, so why create yet another?

Simple: convienence and low cost.

Convienence comes from zero maintanence, zero setup, and ease of use through only requiring any modern web browser on any device to use it.
Low cost comes from using readily available industry standard hardware modules that are glued together using free open source software.

## The vision
To produce a stand-alone device that can be used for all, or any, of:
 - competitor registration (pre-entry or on-the-day)
 - start confirmation
 - check point visit confirmation (CP self configures via GPS)
 - finish registration
 - lost/late competitor alerts
 - automatic results publication
 - self powered for at least 24 hours
 
And all of this with real-time feedback from CPs on the course to the race organisers HQ (or anywhere else), even in mountainous terrain with no mobile phone coverage.
 
## The technology
The main component is the use of UHF RFID readers/tags. These are the type of RFID systems typically used for auto entry car parks and road tolls. They have the advantage of very low cost tags (10p each if bought in bulk) and long range reading (3 metres or more) which means competitors do not have to stop at CPs. As long as they get within range of the reader they'll be recorded. The disadvantage of UHF is the higher cost of the readers (compared with for e.g. NFC, as found in modern smartphones), but if carefully sourced (i.e. China!) the cost is not prohibitive. Another disadvantage is the comparatively high power requirement (you don't get long range without broadcasting a lot of power!), but intelligent power management can mitigate this.

On top of the UHF tag readers is the use of *all* the modern comms capbilities to ensure a connection back to HQ, and/or the internet, can always be achieved. The comms include: Wifi, Bluetooth, LTE (mobiles) and LoRa (long range low power radio).

And finally, to allow the device to self configure from its location, a GPS module so it knows where it is and can behave accordingly.

The glue for all this is a low cost compute module, the Raspberry Pi Zero W. That will provide the interface to everything via an embeded web server that can be accessed through any web browser on any device via WiFi. So the only other equipment required to run this system is any phone, tablet, laptop, desktop PC with WiFi. Where the internet is visible, this will also provide access to that. In particular, there will be no software downlaod/install required, it all comes embedded in the stabd-alone device. That will auto update itself everytime it can see the internet.

## Typical hardware components and costings

 - UHF readers (with circulary polarised antennas), there are lots on alibaba.com (the Chinese equivalent of Amazon), ranging from $68 (US) upwards, plus shipping/tax, allow £80 per reader
 - Pi Zero W, about £12, provides the web server software platform and the 'glue' and the WiFI AP (Access Point) for external devices
 - SD card, 32GB, about £10 with NOOBS pre-installed from PiHut
 - Pycom Fipy, about £50, provides the comms, WiFi (for internet access), Bluetooth, LTE, LoRa (provides the Pymesh radio network)
 - RTC (rea-time clock), about £5 (PiHut mini RTC module), provides date/time even when powered off
 - GPS, about £12 (TeOhk GT-U7 on Amazon)
 - Battery, 12v 5Ah+, lead-acid, about £20, lead-acid is far cheaper than LiPo (Lithium Polymer) and the extra bulk/weight is not an issue for the intended usage. 
 -Power regulators, the electronics will require 5v and 3.3v in various places (the main 12v is for the UHF readers) so regalators will be required, they are "ten-a-penny", so noise
 - Case, a case to house all the electronics tidly can be 3D printed, allow £20, or just use a lunch box!
 - Mounting poles and/or tripods, cost TBD, allow £10
 - Other odds and ends, cables, connectors, et al, allow £10
 
 This brings the total hardware cost to around £230 per unit. There is scope for cost saving, mostly by replacing the £50 Fipy with something cheaper (but requiring more software). Another cost saving area is to use smaller UHF antennas but that also reduces the reading range. Or cheaper still, use a Yagi array (i.e a TV aerial) but they have the disadvantage of being linearly polarised so the competitors would have to make the tags were worn the "right way up".
 
 ## Major software components
 
  - Pymesh, provides a resilent comms network over the LoRa radios embedded in the FiPy units
  - Diet Pi, the Linux based operating system used in the PiZero W compute devices
  - Webserver, loads available for the Pi
  - Glue software, part of this project
  - Web app, the application users of the system interact with, part of this project
  
  ## Road map (this is all vapourware as of 10/11/20)
  
   - acquire prototype hardware (done)
   - build proof of concept prototype (1 station, in progress)
   - build demo prototype (3 stations, registration, start, finish)
   - use demo prototype in parallel with existing systems to gain usage feedback
   - iterate
   - roll out (10+ stations)
   
