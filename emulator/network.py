""" history
    2021-04-04 DCN: created
    """
""" description
    Stubs for the network module
    """

class WLAN:
    INT_ANT = 1
    EXT_ANT = 2
    STA     = 1
    AP      = 2
    STA_AP  = 3
    def __init__(self,**kwargs):
        pass
    def ifconfig(self,**kwargs):
        return ["127.0.0.1"]

class Server:
    def deinit(self):
        pass
    def init(self,**kwargs):
        pass

class MDNS:
    # MDNS is not a class, but we want to be able to use dot notation, so use @staticmethod decorator on methods
    PROTO_TCP = 0
    @staticmethod
    def deinit():
        pass
    @staticmethod
    def init():
        pass
    @staticmethod
    def set_name(**kwargs):
        pass
    @staticmethod
    def add_service(*args,**kwargs):
        pass
