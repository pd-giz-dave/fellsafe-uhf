"""history:
    2021001-28 DCN: Created stub
    2021-02-03 DCN: pre-compile our templates
    2021-04-05 DCN: Use config not board
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
import re
import config
import machine
import sys
import json
import os

PAGE_LAYOUT = None
REPL_LAYOUT = '_repl_layout.html'

app = None
log = None

global_scope = {}                        # exec globals
local_scope  = {}                        # exec locals
commands     = []                        # command history
responses    = []                        # response history

# unecode url characters that have been translated into %xx
def unencode(s):
    arr = s.split("%")
    arr2 = [chr(int(x[:2],16)) + x[2:] for x in arr[1:]]
    return arr[0] + ''.join(arr2)


#auto called at start-up, register our routes and their handlers
def page(app_in,_,log_in,layout):
    global PAGE_LAYOUT,app,log
    PAGE_LAYOUT = layout
    app = app_in
    log = log_in
    app.add_url_rule('/repl',repl_home)
    app.add_url_rule('/repl/_help',repl_help)
    app.add_url_rule('/repl/_clear',repl_clear)
    app.add_url_rule('/repl/_reset',repl_reset)
    app.add_url_rule('/repl/_stop',repl_stop)
    app.add_url_rule(re.compile('^/repl/_log=(.+)'),repl_log)
    app.add_url_rule(re.compile('^/repl/(.+)'),repl_command)
    if log is not None: log.info('/repl routed')

    # pre-compile our layout
    app.compile_template(REPL_LAYOUT)    # compile our content template
    if log is not None: log.info(REPL_LAYOUT + ' compiled')


# save the command/response history and send the response
# everything is jsonified
def repl_response(resp,command,response):
    global commands,responses
    commands.append(json.dumps(command))
    responses.append(json.dumps(response))
    yield from picoweb.start_response(resp,'application/json')
    yield from resp.awrite(responses[-1])

##################################################   
# these are called as coroutines (ie. an iterable)
##################################################

# NB: all route handlers must be an 'iterable', that means they must yield and not just return

def repl_home(req,resp):
    # send the controlling page (with its JS and CSS)
    yield from picoweb.start_response(resp)
    yield from app.render_template(resp,PAGE_LAYOUT,(config.name(),'Fellsafe REPL (enter "_help" to get a command list)',None,REPL_LAYOUT,[commands,responses]))


def repl_help(req,resp):
    yield from repl_response(resp,'_help','_help: show this help</br>'+\
                                          '_clear: clear command and response history</br>'+\
                                          '_reset: clear globals and locals, effectively a re-boot on this repl</br>'+\
                                          '_stop: stop the application (does a device hard reset</br>'+\
                                          '_log=N: set logging level to N, 0=off,1=info,2=debug (you need access to the serial console to see it)</br>'+\
                                          '=expression - evaluated as a python expression and result returned</br>'+\
                                          'statement - executed as a python statement, use =expression to see the result')
    
def repl_clear(req,resp):
    global commands,responses
    commands  = []
    responses = []
    yield from repl_response(resp,'_clear','cleared history')
    
def repl_reset(req,resp):
    global global_scope,local_scope
    global_scope = {}
    local_scope  = {}
    yield from repl_response(resp,'_reset','cleared globals and locals (effectively a re-boot of this repl)')
    
def repl_stop(req,resp):
    machine.reset()
    #we never get here
    return

def repl_log(req,resp):
    # TODO: Implement _log=N command
    level = req.url_match.group(1)       # get the command string, this is URI encoded,
    yield from repl_response(resp,'_log={}'.format(level),'_log=N not implemented')
    
# called when a repl line is sent from the web page that is not prefixed by '_'
# if the first char is '=' - evalaute it and show response
# else execute it
def repl_command(req,resp):
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
            response = 'Exception exec({}): {}'.format(command,sys.exc_info()[1])      # [0] is the class, [1] is the name, [3] is stack trace

    yield from repl_response(resp,command,response)
