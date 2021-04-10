""" history
    2021-04-08 DCN: created
    """
""" description
    Just here to test the SIM800L is working
    Remove this file once that's done
    """

# ---------------------
# SIM800L example usage
# ---------------------

import sim800l
from sim800l import Modem
import json
import config
import ulogging as logging

logging.basicConfig(level=logging.DEBUG)

modem = None

def start():
    print('Creating modem')
    print('...')
    global modem

    sim800l.set_debug(True)

    # Create new modem object on the right Pins
    modem = Modem(MODEM_RST_PIN      = 'P11',
                  MODEM_TX_PIN       = 'P9',
                  MODEM_RX_PIN       = 'P10')

    # Initialize the modem
    modem.init()

    print('...')

    return modem

def run(modem):
    print('Running tests')
    print('...')

    # Run some optional diagnostics
    print('Modem info: "{}"'.format(modem.get_info()))
    print('...')
    print('Network scan: "{}"'.format(modem.scan_networks()))
    print('...')
    print('Current network: "{}"'.format(modem.get_current_network()))
    print('...')
    print('Signal strength: "{}%"'.format(modem.get_signal_strength()*100))
    print('...')

    # Connect the modem
    modem.connect(apn=config.apn())
    print('...')
    print('Modem IP address: "{}"'.format(modem.get_ip_addr()))
    print('...')

    # Example GET
    print('Testing http GET...')
    print('...')
    url = 'http://checkip.dyn.com/'
    response = modem.http_request(url, 'GET')
    print('...')
    print('Response status code:', response.status_code)
    print('Response content:', response.content)

    # Example POST
    print('...')
    print('Testing https POST...')
    print('...')
    url  = 'https://postman-echo.com/post'
    data = json.dumps({'myparameter': 42})
    response = modem.http_request(url, 'POST', data, 'application/json')
    print('...')
    print('Response status code:', response.status_code)
    print('Response content:', response.content)

    # Disconnect Modem
    print('...')
    modem.disconnect()

    print('...')
    print('Tests complete')
    
def go():
    m = start()
    run(m)
