
""" history
    2021-02-24 DCN: Get IP from the WLAN, not hard wired
    2021-03-25 DCN: Split WiFi setup into a separate function (so main.py can call it)
    """
""" description

    OVERVIEW
    ========
    This is the main Fellsafe app that is accessable through any modern web browser.
    That browser connects to Fellsafe via a WiFi access point (AP).
    The default SSID is fellsafe-<station>.local where <station> is the name of the station.
    That name is set in the board module in the root folder of the device.
    All stations are identical feature-wise, their names are by convention the name
    of some programming language where that name is a single word - e.g. python, java.
    The board can also be accessed via telnet or FTP (but not both at once).
    The credentials for both are user=fellsafe and pwd=<station>.
    The telnet connection gives you access to the Micropython repl. When Fellsafe is
    running this will echo debug information. Pressing Ctrl-C will interupt it and drop
    you into the bare repl. To re-start Fellsafe from there do this:
        import machine
        machine.reset()
    this re-boots the controller. If the board is in debug mode the fellsafe app does
    not auto start. To start it, connect to the repl (via Wifi or USB) and type fellsafe.start()

    PAGES
    =====
    The web facing side of this app consists of conventional html pages that are routed
    to using the picoweb package. All the pages appear as a module in the 'pages' 
    folder. On start-up, the 'pages' folder is scanned and each 'py' or 'mpy' file found
    is 'imported'. That file must provide a function called 'page' that takes 3 parameters:
      the picoweb webapp
      the asyncio event loop
      a logger instance
    Using the webapp it must call the 'add_url_rule' method to add its route and handler.

    TEMPLATES
    =========
    This folder contains the templates used by the [PAGES].

    STATIC
    ======
    This folder just contains static resources (JS, CSS, images, etc) that loaded
    via URLs of the form /static/some_name. This is auto by the picoweb app.

    API
    ===
    Each file under this folder is an AJAX end-point for some request from a web page.
    On start-up these are scanned and called in the same way as [PAGES] except the 
    function it must provide is 'api' instead of 'page'. It too should call the
    'add_url_rule' method of the given picoweb app instance.

    TASKS
    =====
    Each file under this folder is an async task that runs alongside the web server.
    They are scanned at start-up and must provide a 'task' function that calls
    'create_task' on the given instance of an uasyncio event loop. The function is
    given 3 parameters; the same as [PAGES].

    Files with a name starting with an underscore (_) are ignored in the start-up
    scans, as are any files that do not have a 'py' or 'mpy' extension.

    REPL
    ====
    One of the tasks is a REPL on stdin/out to give diagnostic access to state.

    STATE
    =====
    This folder contains all the system state, both volatile and persistent, and
    their access functions. Centralising the state provides for easy debugging by
    reading/writing state via the REPL. Non-trivial state is not allowed to be
    held anywhere else. Tasks update state, the web api accesses it.

    CONVENTIONS
    ===========
    Any module, on being imported, must at most initialise constants and define
    functions and classes. They must *NOT* execute any code other than that. Also,
    it must not rely on any context outside of itself. Similarly for globals in any
    import. I.e. all logic that does stuff must be inside a function or a class
    method.

    @@TBD@@
    =======
    and the comfy chair...

    """

import board
import ulogging as logging

HOST_IP   = ''
HOST_PORT = 80
# debug values:
# -1 disable all logging
# 0 (False) normal logging: requests and errors
# 1 (True) debug logging
# 2 extra debug logging
if board.debug:
    DEBUG_LEVEL   = 2
    LOGGING_LEVEL = logging.DEBUG        # see ulogging module for other options
else:
    DEBUG_LEVEL   = 0
    LOGGING_LEVEL = logging.INFO

MASTER_LAYOUT = '_page_layout.html'      # all pages are based on this

# (folder name, function name, parameter) tuples to scan and run
FOLDERS = [('pages','page', MASTER_LAYOUT),
           ('api'  ,'api' , None         ),
           ('tasks','task', None         ),
          ]

prepared = False # set True when we have started the WiFi AP

def prepare():
    # this is auto called from main.py on boot-up when debug is set, it starts the WiFi AP
    import wifi
    global HOST_IP, prepared
    HOST_IP = wifi.ap('fellsafe',board.name,http=HOST_PORT,debug=DEBUG_LEVEL>0) # turn on WiFi as a Fellsafe AP (also starts mDNS and Telnet servers)
    prepared = True

def start():
    # this is auto called from main.py on boot-up when debug is not set
    logging.basicConfig(level=LOGGING_LEVEL)   # setup logging
    log = logging.getLogger(__name__)
    log.debug('logging enabled at level {}'.format(LOGGING_LEVEL))
    log.info('starting...')

    # these imports take a while
    import os
    import sys
    import uasyncio as asyncio
    import picoweb

    if not prepared:
        prepare()                              # turn in WiFi AP

    loop = asyncio.get_event_loop()            # instantiate the async scheduler loop ASAP

    # start the web app early so we can add routes and compile templates before we start
    app = picoweb.WebApp(__name__,None,True,os.getcwd()+'/'+__path__)
    app.start(debug=DEBUG_LEVEL,host=HOST_IP,port=HOST_PORT)

    # pre-compile our master template
    app.compile_template(MASTER_LAYOUT)
    log.info(MASTER_LAYOUT + ' compiled')
    
    #find and start all our components
    for folder in FOLDERS:
        log.info('scanning {} for {} passing {}'.format(folder[0],folder[1],folder[2]))
        items = os.listdir(__path__+'/'+folder[0])
        for item in items:
            path = str.split(item,'.')
            if item[0] != '_' and (path[1] == 'py' or path[1] == 'mpy'):
                module = __path__+'.'+folder[0]+'.'+path[0]
                log.info('found {}'.format(module))
                __import__(module)
                module = sys.modules[module]
                if hasattr(module,folder[1]) and callable(getattr(module,folder[1])):
                    #the function we want exists, so call it
                    getattr(module,folder[1])(app,loop,logging.getLogger(path[0]),folder[2])
                else:
                    log.warning('module {} has no callable {} attribute'.format(module,folder[1]))

    #now fire it all up
    log.info('...running...')
    loop.run_forever()

    #we never get here
    loop.close()

    log.info('...stopped')
