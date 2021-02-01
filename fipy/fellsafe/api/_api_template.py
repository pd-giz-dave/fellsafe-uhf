""" history
    30/01/21 DCN: Created
    """

""" description
    Template for an API end point module
    Copy code below and use the header snippet on the first line on new file
    """

import picoweb
import ure as re
from . import _api_helpers as API

app = None
log = None

#auto called at start-up, register our route and its handler
def api(app_in,_,log_in):
    global app,log
    app = app_in
    log = log_in
    app.add_url_rule(re.compile('^/api/end_point_name/(.+)'),handler)
    log.info('/api/end_point_name/(.+) routed')

#these are called as coroutines (ie. an iterable)
def handler(req,resp):
    #do stuff, e.g.
    url_param = req.url_match.group(1)                                         #get the first param match
    some_structured_data = {'a': 1, 'b': 2, 'param': url_param, 'etc': 3}      #build an appropriate response in a serialisable object
    yield from picoweb.jsonify(resp,some_structured_data)                      #and send it as a JSON object
