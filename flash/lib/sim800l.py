""" history
    2021-02-11 DCN: created from https://github.com/pythings/Drivers
    2021-04-08 DCN: Tweaks to make work on a Pycom Fipy/Lopy/Wipy
    2021-04-09 DCN: Add 'raw', 'setverbosity' and 'flush' commands (for testing)
                    Iff given a reset pin on initialise pulse it down then up
                    Do pin initialisation even iff given a UART
                    Flush stuff before write first command
    """
""" description
    SIM800L driver
    """

# Imports
import time
import json

logger = None

def set_debug(val):
    # Setup logging
    global logger, DEBUG
    import ulogging as logging
    if val:
        logger = logging.getLogger(__name__)
    DEBUG = val


class GenericATError(Exception):
    pass


class Response(object):

    def __init__(self, status_code, content):
        self.status_code = int(status_code)
        self.content     = content


class Modem(object):

    def __init__(self, uart=None, MODEM_PWKEY_PIN=None, MODEM_RST_PIN=None, MODEM_POWER_ON_PIN=None, MODEM_TX_PIN=None, MODEM_RX_PIN=None):

        # Pins
        self.MODEM_PWKEY_PIN    = MODEM_PWKEY_PIN
        self.MODEM_RST_PIN      = MODEM_RST_PIN
        self.MODEM_POWER_ON_PIN = MODEM_POWER_ON_PIN
        self.MODEM_TX_PIN       = MODEM_TX_PIN
        self.MODEM_RX_PIN       = MODEM_RX_PIN

        # Uart
        self.uart = uart

        self.initialized = False
        self.modem_info = None
        self.verbosity = 0     # error reporting level, 0=default 'ERROR', 1=numeric '+CMEE ERROR: n', 2=verbose '+CMEE ERROR: msg'


    #----------------------
    #  Modem initializer
    #----------------------

    def init(self):

        from machine import Pin

        if logger is not None: logger.debug('Initialising modem...')

        if not self.uart:
            from machine import UART

            # Setup UART
            self.uart = UART(1, 9600, pins=(self.MODEM_TX_PIN,self.MODEM_RX_PIN))  # use default time-out of 2 chars

        # Pin initialization
        MODEM_PWKEY_PIN_OBJ = Pin(self.MODEM_PWKEY_PIN, Pin.OUT) if self.MODEM_PWKEY_PIN else None
        MODEM_RST_PIN_OBJ = Pin(self.MODEM_RST_PIN, Pin.OUT) if self.MODEM_RST_PIN else None
        MODEM_POWER_ON_PIN_OBJ = Pin(self.MODEM_POWER_ON_PIN, Pin.OUT) if self.MODEM_POWER_ON_PIN else None
        #MODEM_TX_PIN_OBJ = Pin(self.MODEM_TX_PIN, Pin.OUT) # Not needed as we use MODEM_TX_PIN
        #MODEM_RX_PIN_OBJ = Pin(self.MODEM_RX_PIN, Pin.IN)  # Not needed as we use MODEM_RX_PIN

        # Status setup
        if MODEM_PWKEY_PIN_OBJ:
            MODEM_PWKEY_PIN_OBJ.value(0)
        if MODEM_POWER_ON_PIN_OBJ:
            MODEM_POWER_ON_PIN_OBJ.value(1)
        if MODEM_RST_PIN_OBJ:
            # generate a down pulse of 100mS
            MODEM_RST_PIN_OBJ.value(1)
            time.sleep_ms(10)
            MODEM_RST_PIN_OBJ.value(0)
            time.sleep_ms(100)
            MODEM_RST_PIN_OBJ.value(1)

        # Flush anything lurking
        try:
            while True:
                self.do('flush')
        except:
            # we expect a time-out error
            pass

        # Test AT commands
        retries = 0
        while True:
            try:
                self.modem_info = self.do('modeminfo')
            except:
                retries+=1
                if retries < 3:
                    if logger is not None: logger.debug('Error in getting modem info, retrying.. (#{})'.format(retries))
                    time.sleep(3)
                else:
                    raise
            else:
                break

        if logger is not None: logger.debug('Ok, modem "{}" is ready and accepting commands'.format(self.modem_info))
        if DEBUG:
            self.setverbosity(2)

        # Set initialized flag and support vars
        self.initialized = True


    #----------------------
    # Execute AT commands
    #----------------------
    def do(self, command, data=None, clean_output=True, timeout=None, end=None):

        """ TODO: make getdata safe from detecting the end token within the data stream
            Needs splitting into 2: getlen to get the HTTPREAD data_length (response is +HTTPREAD: nnnn\r\n)
                                    getdata to read that number of chars *then* look for the end token
            """

        timeout = timeout or 5
        end     = end     or 'OK'

        # Commands dictionary. Not the best approach ever, but works nicely.
        commands = {
                    'modeminfo':    {'string':'ATI', 'timeout':timeout, 'end': end},
                    'fwrevision':   {'string':'AT+CGMR', 'timeout':timeout, 'end': end},
                    'battery':      {'string':'AT+CBC', 'timeout':timeout, 'end': end},
                    'scan':         {'string':'AT+COPS=?', 'timeout':max(timeout,60), 'end': end},
                    'network':      {'string':'AT+COPS?', 'timeout':timeout, 'end': end},
                    'signal':       {'string':'AT+CSQ', 'timeout':timeout, 'end': end},
                    'checkreg':     {'string':'AT+CREG?', 'timeout':timeout, 'end': None},
                    'setapn':       {'string':'AT+SAPBR=3,1,"APN","{}"'.format(data), 'timeout':timeout, 'end': end},
                    'initgprs':     {'string':'AT+SAPBR=3,1,"Contype","GPRS"', 'timeout':timeout, 'end': end}, # Appeared on hologram net here or below
                    'opengprs':     {'string':'AT+SAPBR=1,1', 'timeout':timeout, 'end': end},
                    'getbear':      {'string':'AT+SAPBR=2,1', 'timeout':timeout, 'end': end},
                    'inithttp':     {'string':'AT+HTTPINIT', 'timeout':timeout, 'end': end},
                    'sethttp':      {'string':'AT+HTTPPARA="CID",1', 'timeout':timeout, 'end': end},
                    'enablessl':    {'string':'AT+HTTPSSL=1', 'timeout':timeout, 'end': end},
                    'disablessl':   {'string':'AT+HTTPSSL=0', 'timeout':timeout, 'end': end},
                    'initurl':      {'string':'AT+HTTPPARA="URL","{}"'.format(data), 'timeout':timeout, 'end': end},
                    'doget':        {'string':'AT+HTTPACTION=0', 'timeout':max(timeout,10), 'end': '+HTTPACTION'},
                    'setcontent':   {'string':'AT+HTTPPARA="CONTENT","{}"'.format(data), 'timeout':timeout, 'end': end},
                    'postlen':      {'string':'AT+HTTPDATA={},5000'.format(data), 'timeout':timeout, 'end': 'DOWNLOAD'},  # "data" is data_length in this context, while 5000 is the timeout
                    'dumpdata':     {'string':data, 'timeout':timeout, 'end': end},
                    'dopost':       {'string':'AT+HTTPACTION=1', 'timeout':max(timeout,10), 'end': '+HTTPACTION'},
                    'getdata':      {'string':'AT+HTTPREAD', 'timeout':timeout, 'end': end},
                    'closehttp':    {'string':'AT+HTTPTERM', 'timeout':timeout, 'end': end},
                    'closebear':    {'string':'AT+SAPBR=0,1', 'timeout':max(timeout,10), 'end': end},
                    'setverbosity': {'string':'AT+CMEE={}'.format(data), 'timeout':timeout, 'end': end},
                    'flush':        {'string':'', 'timeout':1, 'end': ''},
                    'raw':          {'string':(data or 'ATI'), 'timeout':timeout, 'end': end},
        }

        # References:
        # https://github.com/olablt/micropython-sim800/blob/4d181f0c5d678143801d191fdd8a60996211ef03/app_sim.py
        # https://arduino.stackexchange.com/questions/23878/what-is-the-proper-way-to-send-data-through-http-using-sim908
        # https://stackoverflow.com/questions/35781962/post-api-rest-with-at-commands-sim800
        # https://arduino.stackexchange.com/questions/34901/http-post-request-in-json-format-using-sim900-module (full post example)

        # Sanity checks
        if command not in commands:
            raise Exception('Unknown command "{}"'.format(command))

        # Support vars
        command_string  = commands[command]['string']
        expected_end    = commands[command]['end']
        timeout         = commands[command]['timeout']

        # Execute the AT command
        if command == 'flush':
            # we're just flushing extraneous responses,
            # so just read whatever is there without sending a command
            if logger is not None: logger.debug('{}: Writing nothing'.format(command))
            pass
        else:
            command_string_for_at = "{}\r\n".format(command_string)
            if logger is not None: logger.debug('{}: Writing "{}"'.format(command,command_string_for_at.encode('utf-8')))
            self.uart.write(command_string_for_at)

        # Support vars
        pre_end = True
        output  = ''
        empty_reads = 0

        while True:

            line = self.uart.readline()
            if not line:
                # To get here means nothing appeared within the time-out period (default 2 character times)
                empty_reads += 1
                if empty_reads > timeout:
                    if logger is not None: logger.debug('{}: Timed-out after {} re-tries'.format(command,timeout))
                    raise Exception('{}: Timeout (timeout={})'.format(command, timeout))
                else:
                    if logger is not None: logger.debug('{}: Re-trying read attempt {}, {} re-tries left'.format(command,empty_reads,max(timeout-empty_reads,0)))
                    time.sleep(1)        # wait for some (more) characters to arrive
            else:
                # NB: this may be a partial line if there was a read time-out
                if logger is not None: logger.debug('{}: Read "{}"'.format(command,line))

                # Convert line to string
                line_str = line.decode('utf-8')

                # Do we have an error or the expected end?
                if command == 'flush':
                    # just dumping crap, so even errors are crap and not expecting any 'end'
                    pass
                elif line_str.startswith('ERROR\r\n') or line_str.startswith('+CME ERROR:'):
                    if line_str.endswith('\r\n'):
                        line_str = line_str[:-2]
                    raise GenericATError('{}: Failed with "{}"'.format(command,line_str))
                else:
                    # If we had a pre-end, do we have the expected end?
                    if line_str == '{}\r\n'.format(expected_end):
                        if logger is not None: logger.debug('{}: Detected exact end'.format(command))
                        break
                    if pre_end and line_str.startswith('{}'.format(expected_end)):
                        if logger is not None: logger.debug('{}: Detected startwith end (and adding this line to the output too)'.format(command))
                        output += line_str
                        break
                    # Do we have a pre-end?
                    if line_str == '\r\n':
                        pre_end = True
                        if logger is not None: logger.debug('{}: Detected pre-end'.format(command))
                        if clean_output:
                            line_str = ','
                    else:
                        pre_end = False

                # Save this line unless in particular conditions
                if command == 'getdata' and line_str.startswith('+HTTPREAD:'):
                    pass
                else:
                    output += line_str

        # Remove the command string from the output
        output = output.replace(command_string+'\r\r\n', '')

        # ..and remove the last \r\n added by the AT protocol
        if output.endswith('\r\n'):
            output = output[:-2]

        # Also, clean output if needed
        if clean_output:
            output = output.replace('\r', '')
            output = output.replace('\n', ',')
            while ',,' in output:
                output = output.replace(',,', ',')
            if output.startswith(','):
                output = output[1:]
            if output.endswith(','):
                output = output[:-1]

        if logger is not None: logger.debug('{}: Returning "{}"'.format(command,output.encode('utf8')))

        # Return
        return output


    #----------------------
    #  Function commands
    #----------------------

    def raw(self,command,end=None,timeout=None):
        output = self.do('raw',data=command,timeout=timeout,end=end)
        return output

    def setverbosity(self,level=0):
        output = self.do('setverbosity',data=level)
        return output

    def get_info(self):
        output = self.do('modeminfo')
        return output

    def battery_status(self):
        output = self.do('battery')
        return output

    def scan_networks(self):
        networks = []
        output = self.do('scan')
        pieces = output.split('(', 1)[1].split(')')
        for piece in pieces:
            piece = piece.replace(',(','')
            subpieces = piece.split(',')
            if len(subpieces) != 4:
                continue
            networks.append({'name': json.loads(subpieces[1]), 'shortname': json.loads(subpieces[2]), 'id': json.loads(subpieces[3])})
        return networks

    def get_current_network(self):
        output = self.do('network')
        network = output.split(',')[-1]
        if network.startswith('"'):
            network = network[1:]
        if network.endswith('"'):
            network = network[:-1]
        # If after filtering we did not filter anything: there was no network
        if network.startswith('+COPS'):
            return None
        return network

    def get_signal_strength(self):
        # See more at https://m2msupport.net/m2msupport/atcsq-signal-quality/
        output = self.do('signal')
        signal = int(output.split(':')[1].split(',')[0])
        signal_ratio = float(signal)/float(30) # 30 is the maximum value (2 is the minimum)
        return signal_ratio

    def get_ip_addr(self):
        output = self.do('getbear')
        output = output.split('+')[-1] # Remove potential leftovers in the buffer before the "+SAPBR:" response
        pieces = output.split(',')
        if len(pieces) != 3:
            raise Exception('Cannot parse "{}" to get an IP address'.format(output))
        ip_addr = pieces[2].replace('"','')
        if len(ip_addr.split('.')) != 4:
            raise Exception('Cannot parse "{}" to get an IP address'.format(output))
        if ip_addr == '0.0.0.0':
            return None
        return ip_addr

    def connect(self, apn):
        if not self.initialized:
            raise Exception('Modem is not initialized, cannot connect')

        # Are we already connected?
        if self.get_ip_addr():
            if logger is not None: logger.debug('Modem is already connected, not reconnecting.')
            return

        # Closing bearer if left opened from a previous connect gone wrong:
        if logger is not None: logger.debug('Trying to close the bearer in case it was left open somehow..')
        try:
            self.do('closebear')
        except GenericATError:
            pass

        # First, init gprs
        if logger is not None: logger.debug('Connect step #1 (initgprs)')
        self.do('initgprs')

        # Second, set the APN
        if logger is not None: logger.debug('Connect step #2 (setapn)')
        self.do('setapn', apn)

        # Then, open the GPRS connection.
        if logger is not None: logger.debug('Connect step #3 (opengprs)')
        self.do('opengprs')

        # Ok, now wait until we get a valid IP address
        retries = 0
        max_retries = 5
        while True:
            retries += 1
            ip_addr = self.get_ip_addr()
            if not ip_addr:
                retries += 1
                if retries > max_retries:
                    raise Exception('Cannot connect modem as could not get a valid IP address')
                if logger is not None: logger.debug('No valid IP address yet, retrying... (#')
                time.sleep(1)
            else:
                break

    def disconnect(self):

        # Close bearer
        try:
            self.do('closebear')
        except GenericATError:
            pass

        # Check that we are actually disconnected
        ip_addr = self.get_ip_addr()
        if ip_addr:
            raise Exception('Error, we should be disconnected but we still have an IP address ({})'.format(ip_addr))


    def http_request(self, url, mode='GET', data=None, content_type='application/json'):

        # Protocol check.
        assert url.startswith('http'), 'Unable to handle communication protocol for URL "{}"'.format(url)

        # Are we  connected?
        if not self.get_ip_addr():
            raise Exception('Error, modem is not connected')

        # Close the http context if left open somehow
        if logger is not None: logger.debug('Close the http context if left open somehow...')
        try:
            self.do('closehttp')
        except GenericATError:
            pass

        # First, init and set http
        if logger is not None: logger.debug('Http request step #1.1 (inithttp)')
        self.do('inithttp')
        if logger is not None: logger.debug('Http request step #1.2 (sethttp)')
        self.do('sethttp')

        # Do we have to enable ssl as well?
        ssl_available = self.modem_info >= 'SIM800 R14.00'
        if ssl_available:
            if url.startswith('https://'):
                if logger is not None: logger.debug('Http request step #1.3 (enablessl)')
                self.do('enablessl')
            elif url.startswith('http://'):
                if logger is not None: logger.debug('Http request step #1.3 (disablessl)')
                self.do('disablessl')
        else:
            if url.startswith('https://'):
                raise NotImplementedError("SSL is only supported by firmware revisions >= R14.00")

        # Second, init and execute the request
        if logger is not None: logger.debug('Http request step #2.1 (initurl)')
        self.do('initurl', data=url)

        if mode == 'GET':

            if logger is not None: logger.debug('Http request step #2.2 (doget)')
            output = self.do('doget')
            response_status_code = output.split(',')[2]
            if logger is not None: logger.debug('Response status code: "{}"'.format(response_status_code))

        elif mode == 'POST':

            if logger is not None: logger.debug('Http request step #2.2 (setcontent)')
            self.do('setcontent', content_type)

            if logger is not None: logger.debug('Http request step #2.3 (postlen)')
            self.do('postlen', len(data))

            if logger is not None: logger.debug('Http request step #2.4 (dumpdata)')
            self.do('dumpdata', data)

            if logger is not None: logger.debug('Http request step #2.5 (dopost)')
            output = self.do('dopost',timeout=10)
            response_status_code = output.split(',')[2]
            if logger is not None: logger.debug('Response status code: "{}"'.format(response_status_code))

        else:
            raise Exception('Unknown mode "{}'.format(mode))

        # Third, get data
        if logger is not None: logger.debug('Http request step #4 (getdata)')
        response_content = self.do('getdata', clean_output=False)  # NB: Relies on textual data to stop it recognising 'OK\r\n' in the data stream

        if logger is not None: logger.debug(response_content)

        # Then, close the http context
        if logger is not None: logger.debug('Http request step #4 (closehttp)')
        self.do('closehttp')

        return Response(status_code=response_status_code, content=response_content)
