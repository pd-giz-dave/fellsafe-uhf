# GPS
- TBS M8 GPS Module from hobbyrc.co.uk - £11 - UART
- GPS Module V2 with Flight Control EEPROM MWC APM2.5 Large Antenna from uk.banggood.com - £3.50 - UART
- Stemedu USB GPS Module Vk-162 Glonass from amazon.co.uk - £20 - USB
- TeOhk GT-U7 on amazon.co.uk - £12 - UART or micro USB
- PyCom pytrackv2 - 37 Euros (~£30) - FiPy plugs into it, then need soldering to access GPIO pins, but very convenient

# UHF Reader
- ACM-812A on alibaba.com - $65 + P&P $45
- cheap Uhf Rfid Reader 865~868MHz long range passive Integrated Reader - $70 + P&P $25 + VAT + £40 import duty/handling - better spec model SW1909 from Shenzen Sinway Communications Co, Ltd via alibab.com - https://www.alibaba.com/product-detail/cheap-Uhf-Rfid-Reader-865-868MHz_62291417319.html?spm=a2700.galleryofferlist.normal_offer.d_title.65cb3b66vHCpRr
- Desktop reader from Amazon - https://www.amazon.co.uk/gp/product/B07C2LV37B/ref=ppx_yo_dt_b_asin_title_o03_s00?ie=UTF8&psc=1 - will not be used, as can use a CP reader for registration as well so reducing equipment complexity - £160
- Kong range reader from Amazon - https://www.amazon.co.uk/gp/product/B018EFLJJI/ref=ppx_yo_dt_b_asin_title_o09_s00?ie=UTF8&psc=1 - will not be used again as can get much cheaper equivalents from alibaba.com - £150

# Interfaces
- RS232-TTL converter - SparkFun Transceiver Breakout - MAX3232 from shop.pimoroni.com - £5

# LoRa
Can't find anything that beats the Pycom FiPy

# LTE-M and NB-Iot
Can't find anything that beats the Pycom FiPy for the hardware.

Pycom supported provider is Vodafone on a NB-IoT network - its expensive for this use case ~£2.50 per month per device, its only davantage is integration with their pybytes platform.

An alternative is *ThingsMobile.com*, they provide a global roaming LTE-M service (which is O2 in the UK) with no fixed fee, its pay-as-you-go at ~10p/MB, for our use case that's huge. Pre-paid credit does not run out (except if not used for 12 months they charge 10p) and better yet, you have an account with N sims and the credit is spread across all of them. The only up-front fee is the sim at £3 each (plus a bit of hassle to register your account).

# m5stack
This is a system that is easy to plug together, so would be simpler for DIY configuration. Suitable modules are:
- GPS $28.50
- NB-IoT $29.90
- LoRaWAN $21.95
- Basic Core, ESP32 Arduino compatible, $27.95 (includes WiFi, Bluetooth, RTC)
- Proto module, to do RS232 I/F to UHF reader, power regulation, $2.95
- or COMMU RS484 module, $11.39

More expensive and the ESP32 has limited capability (its whats in the FiPy)
