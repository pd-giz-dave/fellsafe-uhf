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

_r1 = 100 * 1000                         # voltage divider resister 1 value in ohms (see hardware diagram)
_r2 = 6.8 * 1000                         # voltage divider resister 2 value in ohms (see hardware diagram)
_ratio      = (_r1+_r2)/_r2              # our voltage divider reduction ratio
_adc_pin    = 'P16'                      # which pin its on
_sleep_time = 60                         # seconds to wait between voltage raadings

def task(_,loop,log,_2):
    """ auto called at start-up """
    loop.create_task(battery_coro(log))
    log.info('created task')


async def battery_coro(log):
    """ this is the task itself, it just reads the volts on a regular basis
        the reading is stored in "status.battery" and can be read via state.get('status','battery')
        NB: The resistors used in the voltage divider chain are only 5%
            so there could be up to 10% error in the voltage reported here
        """
    log.info('starting...')
    adc  = machine.ADC()
    batt = adc.channel(pin=_adc_pin)
    while True:
        volts = batt.voltage() * _ratio / 1000 #convert from millivolts to volts
        log.info('battery volts: {}'.format(volts))
        state.set('status','battery',volts)
        await asyncio.sleep(_sleep_time)
    log.info('...stopping')
    #returns stop iteration from here
