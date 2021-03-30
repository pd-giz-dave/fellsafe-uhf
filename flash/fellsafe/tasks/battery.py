""" history
    2021-03-30 DCN: created stub
    """
""" description
    Monitor battery volts
    A voltage divider is connected to pin GPIO38, aka P15
    It divides the 12v battery by 106.8/6.8 (via a resistor chain of 100k and 6.8k)
    """

import uasyncio as asyncio
import state
import machine
from micropython import const

_ratio      = const(6.8/106.8)
_adc        = const('P15')
_sleep_time = const(60)

#auto called at start-up
def task(_,loop,log,_2):
    loop.create_task(battery_coro(log))
    log.info('created task')


#this is the task itself, it just reads the volts on a regular basis
async def battery_coro(log):
    log.info('starting...')
    adc  = machine.ADC()
    apin = adc.channel(pin=_adc)
    while True:
        volts = apin() * _ratio
        state.set('status','battery',volts)
        await asyncio.sleep(_sleep_time)
    log.info('...stopping')
    #returns stop iteration from here
