""" history
    2021-02-01 DCN: created stub
    """
""" description
    An example of the structure of a task module.
    Copy the code and then use the header snippet on the first line of the new file
    """


import uasyncio as asyncio

#auto called at start-up
def task(_,loop,log,_2):
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
