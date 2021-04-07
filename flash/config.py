""" history
    2021-04-04 DCN: created
    2021-04-05 DCN: Turn off Pycom services (was in main)
    2021-04-06 DCN: Put emulated board in emulator/board.py not the project root
    """
""" description
    Provide access to configuration info for this board.
    The actual settings are in a board.py file in the root of the file system.
    This module provides the means to set/get those settings.
    This file is generic and the same on all stations.
    The board.py file is station specific and created via here manually when the station firmware is first loaded.
    The only attribute provided by this module is 'emulated'.
    config.emulated will be True iff we're running under an emulator
    """

def name(set_to=None,*,silent=False):
    """ get/set our board name
        we do that by importing board but delete any existing import so we get a fresh copy
        if silent is asserted a 'get' will return the name come what may, otherwise no name
        or no board module raises an exception
        """
    _load_board()
    if set_to is not None:
        _update_board('name',set_to)
    if silent:
        return board.name
    if board.name == 'no-name':
        raise ValueError('Board name not set (use {}.name(...some-name...) to set it), the system will not run until you set it\nUntil then, access the repl via FTP or Telnet through the "fellsafe-{}.local" Wifi SSID'.format(__name__,board.name))
    return board.name

def debug(set_to=None):
    _load_board()
    if set_to is not None:
        _update_board('debug',set_to)
    return board.debug

def apn(set_to=None):
    # Used by gateway.py to connect the mobile modem
    # This is assuming we are using a Things Mobile sim.
    _load_board()
    if set_to is not None:
        _update_board('apn',set_to)
    return board.apn

def root():
    # work out what our root file system path is
    # if we're in the microcontroller its '/'
    # otherwise its our parent folder
    # in both cases we assume we started in the 'flash' folder
    # so we just get the cwd and return whatever is in front of that
    import os
    import ure as re
    try:
        path = re.match('^(.*)/flash.*$',os.getcwd()).group(1)
    except Exception as e:
        raise e
    if path != '/':
        path += '/'
    return path

def port():
    # get the http server port to use
    # in the microcontroller its the conventional 80
    # in the emulator its 8080 ('cos there is prob already a server running on 80)
    if emulated:
        return 8080
    else:
        return 80

def _load_board(forced=False,fail_on_missing=False):
    # load/create the board module
    global board
    if forced:
        # make it re-load if its already present (so we get a fresh copy)
        import sys
        try:
            del sys.modules['board']
        except:
            pass
    try:
        import board
        return                           # it exists and we loaded it
    except Exception as e:
        if fail_on_missing:
            # we think we created it but cannot find it, that's bad news
            raise e
        pass                             # it does not exist, drop through
    # if we get here the board module does not exist, so create it, but...
    # in the microcontroller we want to create it as /flash/board.py
    # in the emulator we do not want what we create to appear in our firmware source tree
    # (to stop it being downloaded by rshell rsync), so we create it in '../emulator'
    path = root()
    if path == '/':
        # we're in the microcontroller
        path += 'flash/'
    else:
        path += '/emulator/'
    f = open(path+'board.py','w')
    f.write("""
# THIS FILE IS AUTO GENERATED - DO NOT EDIT

# Board name for use by rshell and fellsafe
# By convention board names are programming language names as a single word in lower case.
# The board name is used to construct the WiFi AP ssid and the web server name, like this:
#   fellsafe-<boardName>.local
# The 'fellsafe' prefix is fixed, the '.local' suffix is also fixed and is compatible with
# the board being discoverable, via mDNS, on the local network.
name = 'no-name'

# Used in main.py to determine whether to start Fellsafe or just drop
# through to the REPL. Iff True drop through to the REPL.
debug = True

# Used by gateway.py to connect the mobile modem
# This is assuming we are using a Things Mobile sim.
apn = 'pepperWeb'

                """)
    f.close()
    return _load_board(True,True)

def _update_board(key,value):
    # set board[key] = value in memory and in the board.py file
    # board is assumed to have been loaded  via _load_board()
    # the current directory must not have been changed since board was loaded
    # this function is written for simplicity and not performnace, the assumption
    # is that board.py is small and not updated very often
    # NB: any end-of-line comments in the file on the key line will be lost
    import ure as re
    # update memory
    setattr(board,key,value)
    # update the file
    with open(board.__file__,'r') as f:
        old_contents = f.read().split('\n')
    # NB: re.sub is not available in Micropython, so we have to do the replace the hard way
    #     It also does not have the MULTILINE re flag, so we have to do it line by line
    new_contents = []
    found_key = False
    for line in old_contents:
        parts = re.match('^({} *?= *? ?)(.*)'.format(key),line)
        if parts:
            # \1 is the pre-amble up to line starting key =
            # \2 is the current value
            # we want to swap \2 with value and keep everything else as is
            # NB: using repr(value) 'cos want quotes around strings
            line = parts.group(1)+repr(value)
            found_key = True
        new_contents.append(line)
    if not found_key:
        # key not there, add it as a new line
        new_contents.append('{} = {}'.format(key,repr(value)))
    contents = '\n'.join(new_contents)
    with open(board.__file__,'w') as f:
        f.write(contents)

###################################################################

# setup for native or emulated running
if root() == '/':
    # assume this means we're running native
    emulated = False                     # assume we're native for now
else:
    # assume this means we're running in an emulator
    # fiddle things so that mostly works
    emulated = True                      # we're emulated
    import sys
    # modify the path such that our files are found first
    sys.path.insert(0,root()+'emulator')   # make our emulator visible
    sys.path.insert(0,root()+'flash/lib')  # standard Micropython path
    sys.path.insert(0,root()+'flash')      # ..
    sys.path.insert(0,root())              # make sure we can always use our root (to allow for cwd changing)

try:
    # turn off Pycom services we don't want
    import pycom
    pycom.pybytes_on_boot(False)         # we're not using Pybytes
    pycom.smart_config_on_boot(False)    # ..so we don't want this either
    pycom.wifi_on_boot(False)            # ....nor this as we setup our own AP
except:
    # this means we're not running in a pycom board, so nothing to turn off
    pass
