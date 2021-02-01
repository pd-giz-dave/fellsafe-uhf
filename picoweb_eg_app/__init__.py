#
# This is a picoweb example showing a centralized web page route
# specification (classical Django style).
#
import re
import picoweb
import fellsafe_on   # 18/01/21 DCN: Turn on WiFi as a Fellsafe AP

def index(req, resp):
    # You can construct an HTTP response completely yourself, having
    # a full control of headers sent...
    yield from resp.awrite("HTTP/1.0 200 OK\r\n")
    yield from resp.awrite("Content-Type: text/html\r\n")
    yield from resp.awrite("\r\n")
    yield from resp.awrite("I can show you a table of <a href='squares'>squares</a>.<br/>")
    yield from resp.awrite("Or my <a href='file'>source</a>.<br/>")
    yield from resp.awrite('Or, via /iam/<name> I can say "Hi".<br/>')


def squares(req, resp):
    # Or can use a convenience function start_response() (see its source for
    # extra params it takes).
    yield from picoweb.start_response(resp)
    yield from app.render_template(resp, "squares.tpl", (req,))


def hello(req, resp):
    yield from picoweb.start_response(resp)
    # Here's how you extract matched groups from a regex URI match
    yield from resp.awrite("Hello " + req.url_match.group(1))


ROUTES = [
    # You can specify exact URI string matches...
    ("/", index),
    ("/squares", squares),
    ("/file", lambda req, resp: (yield from app.sendfile(resp, __file__))),
    # ... or match using a regex, the match result available as req.url_match
    # for match group extraction in your view.
    (re.compile("^/iam/(.+)"), hello),
]


import ulogging as logging
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

app = picoweb.WebApp(__name__, ROUTES)
# debug values:
# -1 disable all logging
# 0 (False) normal logging: requests and errors
# 1 (True) debug logging
# 2 extra debug logging
app.run(debug=2,host="192.168.4.1",port=80)
