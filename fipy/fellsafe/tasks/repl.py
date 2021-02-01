"""history:
    28/01/21 DCN: Created stub
    """
"""description:
    This provides a simple REPL using sys.stdin and sys.stdout
    These are both 'stream' objects so we can use asyncio to await without blocking.
    This simulates the default REPL using await read() + exec() + write().
    The exec function takes 3 params:
        a program fragment as a multi-line string
        a dictionary representing globals
        a dictionary representing locals
    So a loop like this maintains its own context:
        global_scope = {}
        local_scope = {}
        while True
            async write(prompt)
            line = async read()
            exec(line,global_scope,local_scope)
    If the line ends in a ':' we must keep reading with indentation until the user
    unidents, recursively. If it ends in a '\' append the following line. Otherwise
    execute the line(s). Within the exec the scope is as if we're inside a function,
    so assignments like "a=3" update the local_scope, to update the global_scope
    this idiom is required:
        global a
        a=3
    """

import uasyncio as asyncio

#auto called at start-up
def task(_,loop,log):
    loop.create_task(me_coro(log))
    log.info('created task')
    

#this is the task itself    
async def me_coro(log):
    log.info('starting...')
    while True:
        try:
            #do something, e.g.
            await asyncio.sleep(10)      #returns an iterable from here
            log.info('still here')
        except:
            break
    log.info('...stopping')
    #returns stop iteration from here

# ToDo
# provide facilities to change logging level
# provide an interrupt facility to stop it all and drop into the defult REPL
# make it into a web REPL