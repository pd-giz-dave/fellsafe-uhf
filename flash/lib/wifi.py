""" history
    2021-01-30 DCN: created
    2021-02-24 DCN: Add simple DNS server
    2021-03-25 DCN: Use PyCom built-in MDNS server not SlimDNS
                    Start a telnet and FTP server too
    2021-03-31 DCN: Use internal WiFi antenna
    """

""" description
    Turn on WiFi AP and mDNS and Telnet and FTP servers for the board
    """

import ulogging as logging
from network import WLAN
from network import MDNS
from network import Server

_antenna = WLAN.INT_ANT

_log = None

def ap(domain,boardname,*,http=80,telnet=23,ftp=21,debug=False):
    """ start a WiFi AP with ssid of domain-boardname.local on given port
        and an mDNS server also for domain-boardname.local
        and a telnet server, credentials are user=domain,pwd=board.name
        and an FTP server
        returns the IP of the AP as a string
        """
    global _log
    if debug:
        _log = logging.getLogger(__name__)
    server = Server()
    try:
        server.deinit()
    except:
        pass
    server.init(login=(domain,boardname),timeout=600)
    dom  = domain+'-'+boardname
    name = dom+'.local'
    wlan = WLAN(mode=WLAN.AP,ssid=name,antenna=_antenna,channel=1)
    ip   = wlan.ifconfig(id=1)[0]
    if _log is not None:
        _log.info('ap: started as {} at IP {}'.format(name,ip))
    _set_host(dom,boardname)
    _add_TCP_service('_http',http)
    _add_TCP_service('_telnetd',telnet)
    _add_TCP_service('_ftp',ftp)
    return ip

def _set_host(hostname,boardname):
    try:
        MDNS.deinit()
    except:
        pass
    MDNS.init()
    MDNS.set_name(hostname=hostname,instance_name=boardname)
    if _log is not None:
        _log.info('set_host: started mDNS for host={}, board={}'.format(hostname,boardname))

def _add_TCP_service(service,port):
    MDNS.add_service(service,MDNS.PROTO_TCP,port)
    if _log is not None:
        _log.info('add_TCP_service: {} on port {}'.format(service,port))
