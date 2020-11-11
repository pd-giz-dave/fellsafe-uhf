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
 - start confirmation (the readers can cope with mass starts)
 - check point visit confirmation (CP self configures via GPS)
 - finish registration
 - lost/late competitor alerts
 - automatic results publication
 - self powered for at least 24 hours
 
And all of this with real-time feedback from CPs on the course to the race organisers HQ (or anywhere else), even in mountainous terrain with no mobile phone coverage.

In the context of the 2020 Covid-19 pandemic there is scope to use this system while maintaining social distancing. By pre-registering and pre-placig the readers, races could be run by individuals and results collated automatically. All the competitor would need to carry would be the tag which could be posted to them. Going further, the tag could completely identify the individual (like 'dibbers' but far cheaper) so not even registration (pre or otherwise) would be required. Rather like Park Runs, just turn up and go.
 
## The technology
The main component is the use of UHF RFID readers/tags. These are the type of RFID systems typically used for auto entry car parks and road tolls. They have the advantage of very low cost tags (10p each if bought in bulk) and long range reading (3 metres or more) which means competitors do not have to stop at CPs. As long as they get within range of the reader they'll be recorded. The disadvantage of UHF is the higher cost of the readers (compared with for e.g. NFC, as found in modern smartphones), but if carefully sourced (i.e. China!) the cost is not prohibitive. Another disadvantage is the comparatively high power requirement (you don't get long range without broadcasting a lot of power!), but intelligent power management can mitigate this.

On top of the UHF tag readers is the use of *all* the modern comms capbilities to ensure a connection back to HQ, and/or the internet, can always be achieved. The comms include: Wifi, Bluetooth, LTE (mobiles) and LoRa (long range low power radio).

And finally, to allow the device to self configure from its location, a GPS module so it knows where it is and can behave accordingly.

The glue for all this is a low cost compute module, the Raspberry Pi Zero W. That will provide the interface to everything via an embeded web server that can be accessed through any web browser on any device via WiFi.

The only other equipment required to run this system is any phone, tablet, laptop, desktop PC with WiFi. Where the internet is visible, this will also provide access to that. In particular, there will be no software download/install required, it all comes embedded in the device. That will auto update itself everytime it can see the internet.

## Typical hardware components and costings

 - UHF readers (with circulary polarised antennas), there are lots on alibaba.com (the Chinese equivalent of Amazon), ranging from $68 (US) upwards, plus shipping/tax, allow £80 per reader
 - Pi Zero W, about £12, provides the web server software platform and the 'glue' and the WiFI AP (Access Point) for external devices
 - SD card, 32GB, about £10 with NOOBS pre-installed from PiHut
 - Pycom Fipy, about £50, provides the comms, WiFi (for internet access), LTE (NB-IoT access), LoRa (provides the Pymesh radio network) (11/11/20 cannot beat this price with separate Pi modules)
 - RTC (rea-time clock), about £5 (PiHut mini RTC module), provides date/time even when powered off (NB: GPS can supply time but not date)
 - GPS, about £12 (TeOhk GT-U7 on Amazon)
 - Battery, 12v 5Ah+, lead-acid, about £20, lead-acid is far cheaper than LiPo (Lithium Polymer) and the extra bulk/weight is not an issue for the intended usage. 
 - Power regulators, the electronics will require 5v and 3.3v in various places (the main 12v is for the UHF readers) so regalators will be required, they are "ten-a-penny", so noise
 - Case, a case to house all the electronics tidly can be 3D printed, allow £20, or just use a lunch box!
 - Mounting poles and/or tripods, cost TBD, allow £10
 - LTE/WiFi*2/Lora antenna, £20
 - IoT SIM card, 1nce.com £10 for 500MB valid for 10 years
 - PCB (later, initially use a breadboard and wires), e.g. pcbgogo.com $5 for 100mm x 100mm 2 layers
 - Other odds and ends, cables, connectors, et al, allow £10
 
 This brings the total hardware cost to around £250 per unit. There is scope for cost saving, mostly by replacing the £50 Fipy with something cheaper (but requiring more software). Another cost saving area is to use smaller UHF antennas but that also reduces the reading range. Or cheaper still, use a Yagi array (i.e a TV aerial) but they have the disadvantage of being linearly polarised so the competitors would have to make sure the tags were worn the "right way up" (with circular it doesn't matter).
 
 ## Major software components
 
  - Pymesh, provides a resilent comms network over the LoRa radios embedded in the FiPy units
  - Diet Pi, the Linux based operating system used in the PiZero W compute devices
  - Webserver, loads available for the Pi
  - Glue software, part of this project
  - Web app, the application users of the system interact with, part of this project
  
  ## Road map (this is all vapourware as of 10/11/20)
  
   - acquire prototype hardware (done)
   - build proof of concept prototype (1 station, in progress, complete by Jan 2021)
   - build demo prototype (3 stations, registration, start, finish, Mar 2021)
   - dummy test 'race' with a few competitor volunteers (Apr 2021)
   - use demo prototype in parallel with existing systems to gain usage feedback (whenever first race is!)
   - iterate
   - full implementation
   - roll out (10+ stations)
   
