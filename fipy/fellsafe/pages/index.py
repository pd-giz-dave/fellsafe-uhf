""" history
    2021-02-01 DCN: created
    2021-02-03 DCN: add layout param to page()
    """
""" description
    the landing page for the station website
    """

import board
import picoweb

APP_LAYOUT = None

app = None
log = None

#auto called at start-up, register our route and its handler
def page(app_in,_,log_in,layout):
    global APP_LAYOUT,app,log
    APP_LAYOUT = layout
    app = app_in
    log = log_in
    app.add_url_rule('/',index)
    log.info('/ routed')

def index(req, resp):
    yield from picoweb.start_response(resp)
    yield from app.render_template(resp,APP_LAYOUT,(board.name,'Hello from Fellsafe!',None,None,None))
