""" history
    30/01/21 DCN: Created stub
    """
""" description
    api end point to report the board status
    """

import picoweb
import board
import utime

app = None
log = None

#auto called at start-up, register our route and its handler
def api(app_in,_,log_in):
    global app,log
    app = app_in
    log = log_in
    app.add_url_rule('/api/status',handler)
    log.info('api routed')


#generate system status response
def handler(req,resp):
    status = {'board': {'name': board.name, 'type': 'FiPy'},
              'tasks': {'ticks': utime.ticks_ms()}}
    yield from picoweb.jsonify(resp,status)
