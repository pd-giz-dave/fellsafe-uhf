""" history
    2021-01-30 DCN: created
    """

""" description
    Import this to turn off Pycom services on boot
    """

import pycom

pycom.pybytes_on_boot(False)
pycom.smart_config_on_boot(False)
pycom.wifi_on_boot(False)

print("Pycom services turned off.\nIf this is the first time you've turn it off do a hard re-boot.")
