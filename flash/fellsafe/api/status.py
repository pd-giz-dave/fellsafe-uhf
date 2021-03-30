""" history
    2021-01-30 DCN: Created stub
    2021-03-30 DCN: Add battery volts feedback
    """
""" description
    api end point to report the board status
    """

import picoweb
import board
import utime
import gc
import state
import micropython as mpy

app = None
log = None

#auto called at start-up, register our route and its handler
def api(app_in,_,log_in,_2):
    global app,log
    app = app_in
    log = log_in
    app.add_url_rule('/api/status',handler)
    log.info('api routed')


#generate system status response
def handler(req,resp):
    gmt = utime.gmtime()
    status = {'board':  {'name':     board.name,
                        'type':      'FiPy',
                        },
              'time':   {'ticks_ms': utime.ticks_ms(),
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
