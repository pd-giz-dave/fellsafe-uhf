""" history
    2021-01-30 DCN: created
    """

""" description
    Import this to turn on Pycom AP on boot
    """

import board
import pycom
from network import WLAN

pycom.pybytes_on_boot(False)
pycom.smart_config_on_boot(False)
pycom.wifi_on_boot(True)
pycom.wifi_mode_on_boot(WLAN.AP)
pycom.wifi_ssid_ap('fellsafe-'+board.name)

print("Pycom services turned on for fellsafe-{}.\nIf this is the first you've turned it on do a hard re-boot.".format(board.name))
