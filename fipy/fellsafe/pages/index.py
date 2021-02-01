""" history
    2021-02-01 DCN: created
    """

""" description
    the landing page for the station website
    """

import board
import picoweb

app = None
log = None

#auto called at start-up, register our route and its handler
def page(app_in,_,log_in):
    global app,log
    app = app_in
    log = log_in
    app.add_url_rule('/',index)
    log.info('page routed')

def index(req, resp):
    yield from picoweb.start_response(resp)
    yield from app.render_template(resp,'_page_layout.html',(board.name,'Hello from Fellsafe!',None))
