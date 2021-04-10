""" history
    2021-02-04 DCN: created
    """
""" description
    Maintain the RTC accuracy
    The RTC in the FiPy can roll over quite quickly unless utime.time() is called
    on a regular basis. This task does that and also tries to sync to GPS time if
    that is available.
    """

import uasyncio as asyncio
import utime as time
import machine

UPDATE_INTERVAL = 1 * 60 * 60            # how often to re-sync in seconds (hourly)

def task(_,loop,log,_2):
    """ auto called at start-up """
    loop.create_task(clock_coro(log))
    log.info('created task')


async def clock_coro(log):
    """ this is the task itself """
    log.info('starting...')
    # TODO: setup the rtc from some source, below is an e.g from pycom, needs a network connect, how?)
    rtc = machine.RTC()
    rtc.ntp_sync("pool.ntp.org")                           # attemt sync
    await asyncio.sleep(1)                                 # give it time to happen (crude but good enough)
    while True:
        try:
            now = time.localtime()
            log.info('Date/time now is %04d-%02d-%02d %02d:%02d:%02d',now[0],now[1],now[2],now[3],now[4],now[5])
            await asyncio.sleep(UPDATE_INTERVAL)
            now = time.time()                              # this makes uPy deal with internal time roll over
        except Exception as e:
            log.exc(e,'oops!')
            break # TODO: what to do?
    log.info('...stopping')
    #returns stop iteration from here
