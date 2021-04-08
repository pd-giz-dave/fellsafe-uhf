# ---------------------
# SIM800L example usage
# ---------------------

from sim800l import Modem
import json
import config

def _test():
    print('Starting up...')

    # Create new modem object on the right Pins
    modem = Modem(MODEM_RST_PIN      = 'P11',
                  MODEM_TX_PIN       = 'P9',
                  MODEM_RX_PIN       = 'P10')

    # Initialize the modem
    modem.initialize()

    # Run some optional diagnostics
    print('Modem info: "{}"'.format(modem.get_info()))
    print('Network scan: "{}"'.format(modem.scan_networks()))
    print('Current network: "{}"'.format(modem.get_current_network()))
    print('Signal strength: "{}%"'.format(modem.get_signal_strength()*100))

    # Connect the modem
    modem.connect(apn=config.apn())
    print('\nModem IP address: "{}"'.format(modem.get_ip_addr()))

    # Example GET
    print('\nNow running demo http GET...')
    url = 'http://checkip.dyn.com/'
    response = modem.http_request(url, 'GET')
    print('Response status code:', response.status_code)
    print('Response content:', response.content)

    # Example POST
    print('Now running demo https POST...')
    url  = 'https://postman-echo.com/post'
    data = json.dumps({'myparameter': 42})
    response = modem.http_request(url, 'POST', data, 'application/json')
    print('Response status code:', response.status_code)
    print('Response content:', response.content)

    # Disconnect Modem
    modem.disconnect()
    