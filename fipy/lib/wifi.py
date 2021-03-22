""" history
    2021-01-30 DCN: created
    2021-02-24 DCN: Add simple DNS server
    """

""" description
    Turn on WiFi AP and DNS server for the board
    """

import board
import ulogging as logging
from network import WLAN
from slimDNS import SlimDNSServer
from slimDNS import set_debug
import uasyncio as asyncio

DEBUG = False
log   = None

def ap(domain,loop,debug=False):
    """ start a WiFi AP with ssid of domain-boardname.local
        and an mDNS server also for domain-boardname.local
        if log is supplied log info, errors and exceptions to that
        returns the IP of the AP as a string
        """
    dom  = domain+'-'+board.name
    name = dom+'.local'
    wlan = WLAN(mode=WLAN.AP,ssid=name,antenna=WLAN.EXT_ANT,channel=1)
    ip   = wlan.ifconfig(id=1)[0]
    global DEBUG, log
    if __debug__ and debug:
        DEBUG = debug
    if DEBUG:
        set_debug(True)
    log  = logging.getLogger(__name__)
    mdns = SlimDNSServer(ip,dom)
    if log is not None:
        log.info('started mDNS on {} for {}'.format(ip,name))
    loop.create_task(resolver_coro(loop,mdns))
    if log is not None:
        log.debug('scheduled mDNS resolver')
    return ip

async def resolver_coro(loop,mdns):
    if DEBUG and log is not None:
        log.debug('resolver_coro called')
    await asyncio.sleep(0)               # this is required to make sure this function is recognised as a coroutine
    while True:
        if DEBUG and log is not None:
            log.debug('wait for socket ready')
        yield asyncio.IORead(mdns.sock)
        if DEBUG and log is not None:
            log.debug('socket ready')
        mdns.process_waiting_packets()
