""" history
    2021-01-30 DCN: created
    2021-03-25 DCN: Don't import fipy_on
                    Always start the WiFi AP
    2021-04-04 DCN: Use config not board
    """
""" description
    Main start-up.
    It can be disabled by setting config.debug(True)
    """

try:
    import config
    if config.debug():
        print('Loading fellsafe...')
        import fellsafe
        fellsafe.prepare() # always do this so we can access the board via WiFi
        print('Debug is set, so skipping fellsafe start.\nTo start it, type:\n    import fellsafe\n    fellsafe.start()\nTo auto start it next time, type:\n    import config\n    config.debug(False)')
    else:
        import fellsafe
        fellsafe.start()
except:
    #if we get here it means one of our modules either does not exist or threw an exception
    import sys
    print(sys.exc_info()[1])
