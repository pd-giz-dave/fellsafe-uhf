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

def page(app_in,_,log_in,_2):
    """ auto called at start-up, register our route and its handler """
    global app,log
    app = app_in
    log = log_in
    app.add_url_rule(re.compile('^/favicon.ico'),handler)
    log.info('/favicon.ico routed')


def handler(req,resp):
    """ send the favicon """
    yield from app.sendfile(resp,'static/favicon.ico')
