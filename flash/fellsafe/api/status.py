""" history
    2021-01-30 DCN: Created stub
    2021-03-30 DCN: Add battery volts feedback
    2021-04-05 DCN: Use config not board and python.time/gc not time/gc
    """
""" description
    api end point to report the board status
    """

import time
import gc
import micropython as mpy
import sys

import picoweb
import config
import state

app = None
log = None

def api(app_in,_,log_in,_2):
    """ auto called at start-up, register our route and its handler """
    global app,log
    app = app_in
    log = log_in
    app.add_url_rule('/api/status',status_handler)
    log.info('/api/status routed')


def status_handler(req,resp):
    """ generate system status response """
    gmt = time.gmtime()
    status = {'platform': {'name': sys.platform
                        },
              'config': {'name':     config.name(),
                        'debug':     config.debug(),
                        'apn'  :     config.apn(),
                        'port' :     config.port(),
                        },
              'time':   {'ticks_ms': time.ticks_ms(),
                         'date':     '{:04n}-{:02n}-{:02n}'.format(gmt[0],gmt[1],gmt[2]),
                         'time':     '{:02n}:{:02n}:{:02n}'.format(gmt[3],gmt[4],gmt[5]),
                        },
              'memory': {'alloc':    gc.mem_alloc(),
                         'free':     gc.mem_free(),
                         'stack':    mpy.stack_use(),
                        },
              'battery':{'volts':    state.get('status','battery'),
                        },
             }
    yield from picoweb.jsonify(resp,status)
