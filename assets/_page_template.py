""" history
    30/01/21 DCN: Created
    """
""" description    
    Template for a web page module
    """

import picoweb
import ure as re
from . import _page_helpers as PAGE

APP_LAYOUT = None

app = None
log = None

#auto called at start-up, register our route and its handler
def page(app_in,_,log_in,layout):
    global APP_LAYOUT,app,log
    APP_LAYOUT = layout
    app = app_in
    log = log_in
    app.add_url_rule(re.compile('^/url/(.+)'),handler)
    log.info('/url/(.+) routed')

#these are called as coroutines (ie. an iterable)
def handler(req,resp):
    #do stuff, e.g.
    url_param = req.url_match.group(1)                                         #get the first param match
    yield from picoweb.start_response(resp)                                    #do standard header stuff
    yield from resp.awrite('Your URL param was: {}'.format(url_param))         #write to the response and/or
    yield from app.render_template(resp,APP_LAYOUT,(req,))           #evaluate a template, trailing comma in (req,) to make it into a tuple
