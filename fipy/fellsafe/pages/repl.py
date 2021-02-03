"""history:
    2021001-28 DCN: Created stub
    2021-02-03 DCN: pre-compile our templates
    """
"""description:
    This provides a simple REPL in the browser, the browser sends a command
    to /repl/(.+)), and the response from here is the result of executing
    that (as a JSON object).
    It simulates the default REPL using read() + exec() + write().
    The exec function takes 3 params:
        a program fragment as a multi-line string
        a dictionary representing globals
        a dictionary representing locals
    So a loop like this maintains its own context:
        global_scope = {}
        local_scope = {}
        while True
            write(prompt)
            line = read()
            exec(line,global_scope,local_scope)
    If the line ends in a ':' we must keep reading with indentation until the user
    unidents, recursively. If it ends in a '\' append the following line. Otherwise
    execute the line(s). Within the exec the scope is as if we're inside a function,
    so assignments like "a=3" update the local_scope, to update the global_scope
    this idiom is required:
        global a
        a=3
    Its up to the browser page to render things in a useful way
    """

import picoweb
import ure as re
import board

PAGE_LAYOUT = None
REPL_LAYOUT = '_repl_layout.html'

app = None
log = None

global_scope = {}                        # exec globals
local_scope  = {}                        # exec locals
commands     = []                        # command history
responses    = []                        # response history

#auto called at start-up, register our route and its handler
def page(app_in,_,log_in,layout):
    global PAGE_LAYOUT,app,log
    PAGE_LAYOUT = layout
    app = app_in
    log = log_in
    app.add_url_rule('/repl',repl)
    app.add_url_rule(re.compile('^/repl/(.+)'),do_command)
    log.info('/repl and /repl/(.+) routed')

    # pre-compile our layout
    app.compile_template(REPL_LAYOUT)    # compile our content template
    log.info(REPL_LAYOUT + ' compiled')
    
    
#these are called as coroutines (ie. an iterable)
def repl(req,resp):
    # send the controlling page (with its JS and CSS)
    yield from picoweb.start_response(resp)
    yield from app.render_template(resp,PAGE_LAYOUT,(board.name,'Fellsafe REPL',None,REPL_LAYOUT,[commands,responses]))
    

# called when a repl line is sent from the web page
# do it and send response
def do_command(req,resp):
    command = req.url_match.group(1)           # get the command string, this is URI encoded,
                                               # so we have to translate %xx to utf-8 characters
    """ @@TBD@@ decode, execute, create response
        recognise repl commands as well as python statements, eg:
            help
            clear - command and response history
            reset - clear globals and locals
            responses - re-send response history
            commands - re-send command history
            ???
        """ 
    commands.append(command)
    yield from picoweb.jsonify(resp,commands)

# ToDo
# provide facilities to change logging level
# provide facilities to echo the debug log (dupterm?)
# provide an interrupt facility to stop it all so the default REPL becomes accessible on the serial interface
