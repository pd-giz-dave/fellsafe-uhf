""" history
    2021-02-08 DCN: created
    """
""" description
    Provide access to the internet via the FiPy LTE-M modem.
    The access is very limited, just GET to some URL.
    That URL is expected to be some API end-point complete
    with any parameters it requires. The response is expected
    to be some text/plain (translated to a string) or application/json
    (translated to a dictionary).
    We use LTE band 20 (800Mhz) as that's used by all UK operators
    providing LTE-M.
    """

import ulogging as logging
from network import LTE
import ure as re
import uasyncio as asyncio

class Gateway():
    def __init__(self,log=None):
        self.connected = False
        self.band = 20
        self.apn  = None
        self.log  = log
        if self.log is None:
            self.log = logging.getLogger(__name__)
        self.url = re.compile('^((.+?)://)?([^:/]+)(:([0-9]+))?(/(.*))?')
        # TODO: LTE should continually try to connect, so make this a task
        try:
            self.attach(apn=board.apn)
        except Exception as e:
            self.log.exc(e,'cannot attach')
            raise
        try:
            self.connect()
        except Exception as e:
            self.log.exc(e,'cannot connect')
            raise
        self.connected = True
        self.log.info('connected')

    def get(self,url):
        # url is [protocol://]host[]:port][/end_point]
        # where protocol must be http or omitted (then http is assumed)
        # if port is omitted 80 is assumed
        # end_point can be anything, it will be URI encoded in the http request
        # if we're not connected, returns None
        if not self.connected: return None

        # decode the url
        protocol = self.url.match.group(2)
        host     = self.url.match.group(3)
        port     = self.url.match.group(5)
        params   = self.url.match.group(7)

        # validate it
        if protocol is not None and protocol.lower() != 'http':
            if self.log is not None:
                self.log.error('url_decode: protocol must be omitted or "http"')
                raise ValueError('protocol must be omitted or "http"')
        if host is None or host == '':
            if self.log is not None:
                self.log.error('url_decode: host must be present')
                raise ValueError('host must be present')
        if port is None: port = '80'

        # attempt to connect
        reader, writer = yield from asyncio.open_connection(host,port)

        # send the request
        if params is not None and params != '':
             params = make_qs(params)
        else:
            params = ''
        yield from writer.awrite(bytes('GET /{} HTTP/1.0\r\nHost: {}'.format(params,host)))

        # get the response
        # what we want is:
        #   HTTP/.. 200 OK
        #   headers
        #   Content-length: nnn
        #   Content-type: text/plain or application/json
        #   more headers
        #   __blank line__
        #   (content)
        while True:
            line = yield from reader.readline().split()
            if line[0].startswith('HTTP') and line[1] == '200' and line[2] == 'OK':
                pass
            else:
                self.log.info('bad response: %s',line)
                return None
            
