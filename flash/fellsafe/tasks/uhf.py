""" history
    2021-02-01 DCN: created stub
    """
""" description
    UHF reader interface
    """

import uasyncio as asyncio

def task(_,loop,log,_2):
    """ auto called at start-up """
    loop.create_task(uhf_coro(log))
    log.info('created task')


async def uhf_coro(log):
    """ this is the task itself """
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
