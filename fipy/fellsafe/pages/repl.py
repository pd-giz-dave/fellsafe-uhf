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
import machine
import sys
import ujson
import uio as io
import uos as os


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
    app.add_url_rule('/repl/_help',do_help)
    app.add_url_rule('/repl/_clear',do_clear)
    app.add_url_rule('/repl/_reset',do_reset)
    app.add_url_rule('/repl/_stop',do_stop)
    app.add_url_rule(re.compile('^/repl/_log=(.+)'),do_log)
    app.add_url_rule(re.compile('^/repl/(.+)'),do_command)
    if log is not None: log.info('/repl routed')

    # pre-compile our layout
    app.compile_template(REPL_LAYOUT)    # compile our content template
    if log is not None: log.info(REPL_LAYOUT + ' compiled')
    
    
#these are called as coroutines (ie. an iterable)
def repl(req,resp):
    # send the controlling page (with its JS and CSS)
    yield from picoweb.start_response(resp)
    yield from app.render_template(resp,PAGE_LAYOUT,(board.name,'Fellsafe REPL (enter "_help" to get a command list)',None,REPL_LAYOUT,[commands,responses]))


# unecode url characters that have been translated into %xx
def unencode(s):
    arr = s.split("%")
    arr2 = [chr(int(x[:2],16)) + x[2:] for x in arr[1:]]
    return arr[0] + ''.join(arr2)

# save the command/response history and send the response
# everything is jsonified
def do_response(resp,command,response):
    global commands,responses
    commands.append(ujson.dumps(command))
    responses.append(ujson.dumps(response))
    yield from picoweb.start_response(resp,'application/json')
    yield from resp.awrite(responses[-1])

# NB: all route handlers that must be an 'iterable', that means they must yield and not just return
def do_help(req,resp):
    yield from do_response(resp,'_help','_help: show this help</br>'+\
                                        '_clear: clear command and response history</br>'+\
                                        '_reset: clear globals and locals, effectively a re-boot on this repl</br>'+\
                                        '_stop: stop the application (does a device hard reset</br>'+\
                                        '_log=N: set logging level to N, 0=off,1=info,2=debug (you need access to the serial console to see it)</br>'+\
                                        '=expression - evaluated as a python expression and result returned</br>'+\
                                        'statement - executed as a python statement, use =expression to see the result')
    
def do_clear(req,resp):
    global commands,responses
    commands  = []
    responses = []
    yield from do_response(resp,'_clear','cleared history')
    
def do_reset(req,resp):
    global global_scope,local_scope
    global_scope = {}
    local_scope  = {}
    yield from do_response(resp,'_reset','cleared globals and locals (effectively a re-boot of this repl)')
    
def do_stop(req,resp):
    machine.reset()
    #we never get here


# TODO: provide command to view the log (how? dupterm has problems)


def do_log(req,resp):
    # TODO: Implement _log=N command
    level = req.url_match.group(1)       # get the command string, this is URI encoded,
    yield from do_response(resp,'_log={}'.format(level),'_log=N not implemented')
    
# called when a repl line is sent from the web page that is not prefixed by '_'
# if the first char is '=' - evalaute it and show response
# else execute it
def do_command(req,resp):
    global global_scope,local_scope
    command = req.url_match.group(1)     # get the command string, this is URI encoded,
    command = unencode(command)          # so we have to translate %xx to utf-8 characters
    if log is not None: log.debug(command)
    
    if command[0] == '=':
        try:
            response = '{} = {}'.format(command[1:],eval(command[1:],global_scope,local_scope))
        except SyntaxError:
            response = 'SyntaxError eval({})'.format(command[1:])
        except Exception as e:
            response = 'Exception eval({}): {}'.format(command[1:],sys.exc_info()[1])  # [0] is the class, [1] is the name, [3] is dunno

    else:
        # TODO: handle multi-line stuff like if: --> indent --> un-indent --> empty (==execute the block)
        try:
            exec(command,global_scope,local_scope)
            response = 'OK'
        except SyntaxError:
            response = 'SyntaxError exec({})'.format(command)
        except Exception as e:
            response = 'Exception exec({}): {}'.format(command,sys.exc_info()[1])      # [0] is the class, [1] is the name, [3] is dunno

    yield from do_response(resp,command,response)
