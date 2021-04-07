""" history
    2021-01-30 DCN: created
    """

""" description
    import this to connect to farthings WiFi
    """

import network
import utime as time
from machine import RTC

print('Enter Farthings password:')
pwd = input()
print('Connecting...')
wlan = network.WLAN(mode=network.WLAN.STA)
wlan.connect('Farthings', auth=(network.WLAN.WPA2, pwd))
while not wlan.isconnected():
    time.sleep_ms(50)
print(wlan.ifconfig())
rtc = RTC()
rtc.ntp_sync("pool.ntp.org",360)
while not rtc.synced():
    time.sleep_ms(50)
print(rtc.now())
print('Connected!')