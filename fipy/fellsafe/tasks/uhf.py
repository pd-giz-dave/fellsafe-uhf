""" history
    2021-02-01 DCN: created stub
    """
""" description
    UHF reader interface
    """

import uasyncio as asyncio

#auto called at start-up
def task(_,loop,log,_2):
    loop.create_task(uhf_coro(log))
    log.info('created task')


#this is the task itself    
async def uhf_coro(log):
    log.info('starting...')
    while True:
        try:
            #do something, e.g.
            await asyncio.sleep(10)      #returns an iterable from here
            log.info('still here')
        except Exception as e:
            log.exc(e,'oops!')
            break # TODO: what to do?
    log.info('...stopping')
    #returns stop iteration from here
