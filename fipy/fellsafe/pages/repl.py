"""history:
    28/01/21 DCN: Created stub
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

app = None
log = None

global_scope = {}                        # exec globals
local_scope  = {}                        # exec locals
commands     = []                        # command history
responses    = []                        # response history

#auto called at start-up, register our route and its handler
def page(app_in,_,log_in):
    global app,log
    app = app_in
    log = log_in
    app.add_url_rule('/repl',repl)
    app.add_url_rule(re.compile('^/repl/(.+)'),do_command)
    log.info('/repl and /repl/(.+) routed')
    
#these are called as coroutines (ie. an iterable)
def repl(req,resp):
    # send the controlling page (with its JS and CSS)
    content = '_repl_layout.html'              # name of our content template
    yield from picoweb.start_response(resp)
    app._load_template(content)                # compile our content template
    yield from app.render_template(resp,'_page_layout.html',(board.name,'Fellsafe REPL',None,content,[commands,responses]))
    

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
