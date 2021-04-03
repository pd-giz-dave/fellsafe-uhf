""" history
    2021-01-30 DCN: created
    2021-03-25 DCN: Don't import fipy_on
                    Always start the WiFi AP
    2021-03-31 DCN: Turn off Pycom services
    """
""" description
    Main start-up.
    It can be disabled by setting board.debug=true
    """

import pycom

pycom.pybytes_on_boot(False)             # we're not using Pybytes
pycom.smart_config_on_boot(False)        # ..so we don't want this either
pycom.wifi_on_boot(False)                # ....nor this as we setup our own AP

try:
    print('Loading board...')
    import board
    if board.debug:
        print('Loading fellsafe...')
    import fellsafe
    if board.debug:
        fellsafe.prepare() # always do this so we can access the board via WiFi
        print('Skipping fellsafe start.\nType "fellsafe.start()" to start it.\nSet "board.debug=False" to auto start it.')
    else:
        fellsafe.start()
except Exception as e:
    #if we get here it means one of our modules either does not exist or threw an exception
    import sys
    sys.print_exception(e)
