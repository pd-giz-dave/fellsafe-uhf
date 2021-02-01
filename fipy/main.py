""" history
    2021-01-30 DCN: created
    """

""" description
    Main start-up.
    It can be disabled by setting board.debug=true
    """

try:
    print('Loading board...')
    import board
    print('Loading fipy_on...')
    import fipy_on             #turn on Pycom services
    print('Loading fellsafe...')
    import fellsafe
    if board.debug:
        print('Skipping fellsafe start.\nType "fellsafe.start()" to start it.\nSet "board.debug=False" to auto start it.')
    else:
        print('Starting fellsafe...')
        fellsafe.start()
except Exception as e:
    #if we get here it means one of our modules either does not exist or threw an exception
    import sys
    sys.print_exception(e)
