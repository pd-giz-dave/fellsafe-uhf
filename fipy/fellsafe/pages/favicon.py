""" history
    2021-02-01 DCN: created
    """

""" description
    trap favicon requests and send from our static folder
    """

import picoweb
import ure as re

app = None
log = None

#auto called at start-up, register our route and its handler
def page(app_in,_,log_in):
    global app,log
    app = app_in
    log = log_in
    app.add_url_rule(re.compile('^/favicon.ico'),handler)
    log.info('/favicon.ico routed')


def handler(req,resp):
    yield from app.sendfile(resp,'static/favicon.ico')
