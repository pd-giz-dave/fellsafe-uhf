""" history
    2021-04-06 DCN: created
    """
""" description
    Stubs for machine module when running under the emulator
    NB: We assume we are running Micropython even in the emulator
    """

###############################################################

def reset():
    import sys
    print('reset...press Ctrl-D if this goes in a loop')
    sys.exit()
    # don't expect to get here
    while True:
        pass

###############################################################

class ADC:
    ATTN_0DB   = 0
    ATTN_2_5DB = 1
    ATTN_6DB   = 2
    ATTN_11DB  = 3
    id      = None
    bits    = None
    max     = None
    enabled = False
    ref     = 1100
    def __init__(self,id=0):
        self.id = id
    def init(self,*,bits=12):
        if bits < 9 or bits > 12:
            raise ValueError('invalid argument(s) value')
        self.bits = bits
        self.max  = (1 << bits)-1
        self.enabled = True
    def deinit(self):
        self.enabled = False
    def channel(self,*,pin,attn=0):
        if pin not in ('P13','P14','P15','P16','P17','P18','P19','P20'):
            raise OSError('resource not available')
        if not self.enabled:
            self.init()
        return ADCChannel(self,pin,attn)
    def vref(self,ref=None):
        if ref is not None:
            self.ref = ref
        return self.ref
    def vref_to_pin(self,pin):
        if pin == 'P6' or pin == 'P21' or pin == 'P22':
            self.vref2pin = pin
        else:
            raise ValueError('only pins P6, P21 and P22 are able to output VREF')

class ADCChannel():
    pin    = None
    attn   = None
    val    = 4096
    parent = None
    def __init__(self,parent,pin,attn):
        self.parent = parent
        self.pin    = pin
        self.attn   = attn
    def __call__(self):
        return self.value()
    def value(self):
        if self.parent.enabled:
            return self.val
        else:
            raise OSError('the requested operation is not possible')
    def init(self):
        self.parent.init(self,bits=self.parent.bits)
    def deinit(self):
        self.parent.enabled = False
    def voltage(self):
        return self.value_to_voltage(self.value())
    def value_to_voltage(self,value):
        _ = self.value() # make sure we're enabled
        return (value * self.parent.ref) / self.parent.max
    
###############################################################

class RTC:
    INTERNAL_RC = 0  # default source
    XTAL_32KHZ  = 1
    id          = None
    datetime    = None
    source      = None
    server      = None
    period      = None
    backup      = None
    in_sync     = False
    stored      = None
    def __init__(self,id=0,*,datetime=None,source=0):
        self.id       = id
        self.datetime = datetime
        self.source   = source
    def ntp_sync(self,server,*,update_period=3600,backup_server=None):
        self.server  = server
        self.period  = update_period
        self.backup  = backup_server
        self.in_sync = True
    def now(self):
        import utime as time
        if not self.in_sync:
            # not sync'd yet, so return the epoch
            dt = time.gmtime(0)
        else:
            dt = time.gmtime()
        self.datetime = (dt.tm_year, dt.tm_month, dt.tm_day, dt.tm_hour, dt.tm_minute, dt.tm_second, 0, None)
        return self.datetime
    def synced(self):
        return self.in_sync
    def memory(self,*,data=None):
        if data is not None:
            self.stored = data
        return self.stored
        
###############################################################

