""" history
    2021-01-30 DCN: created
    """

""" description
    Import this to turn on the fellsafe WiFi AP
    """

import board
from network import WLAN

wlan = WLAN(mode=WLAN.AP,ssid='fellsafe-'+board.name,antenna=WLAN.EXT_ANT,channel=1)
