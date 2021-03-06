""" history
    2021-01-30 DCN: created by copying github master from https://github.com/pfalcon/pycopy-lib/tree/master/ulogging
    2021-02-01 DCN: Added elapsed time since start on front of all log messages
    2021-04-04 DCN: Make compatible with python
    2021-04-05 DCN: Allow for self.name being None in log prefix
                    use python.time module not naked time
                    don't use sys.print_exception (micropython specific)
    """
""" description
    See ulogging documentation
    """

import sys
import utime as time

CRITICAL = 50
ERROR    = 40
WARNING  = 30
INFO     = 20
DEBUG    = 10
NOTSET   = 0

_level_dict = {
    CRITICAL: "CRIT",
    ERROR: "ERROR",
    WARNING: "WARN",
    INFO: "INFO",
    DEBUG: "DEBUG",
}

_tick_one = time.ticks_ms() #time reference for log message time

_stream = sys.stderr

class Logger:

    level = NOTSET

    def __init__(self, name):
        self.name = name

    def _level_str(self, level):
        l = _level_dict.get(level)
        if l is not None:
            return l
        return "LVL%s" % level

    def setLevel(self, level):
        self.level = level

    def isEnabledFor(self, level):
        return level >= (self.level or _level)

    def log(self, level, msg, *args):
        if level >= (self.level or _level):
            now = time.ticks_diff(time.ticks_ms(),_tick_one) / 1000
            _stream.write('{:_<8}:{:_<10}:{:09.3f}:'.format(self._level_str(level),self.name or 'None',now)) #30/01/21 DCN: Added time
            if not args:
                print(msg, file=_stream)
            else:
                print(msg % args, file=_stream)

    def debug(self, msg, *args):
        self.log(DEBUG, msg, *args)

    def info(self, msg, *args):
        self.log(INFO, msg, *args)

    def warning(self, msg, *args):
        self.log(WARNING, msg, *args)

    def error(self, msg, *args):
        self.log(ERROR, msg, *args)

    def critical(self, msg, *args):
        self.log(CRITICAL, msg, *args)

    def exc(self, e, msg, *args):
        self.log(ERROR, msg, *args)
        self.log(ERROR,'Exception: {}({})'.format(e.__class__.__name__,e.args))

    def exception(self, msg, *args):
        self.exc(sys.exc_info()[0], msg, *args)


_level = INFO
_loggers = {}

def getLogger(name):
    if name in _loggers:
        return _loggers[name]
    l = Logger(name)
    _loggers[name] = l
    return l

def info(msg, *args):
    getLogger(None).info(msg, *args)

def debug(msg, *args):
    getLogger(None).debug(msg, *args)

def basicConfig(level=INFO, filename=None, stream=None, format=None):
    global _level, _stream
    _level = level
    if stream:
        _stream = stream
    if filename is not None:
        print("logging.basicConfig: filename arg is not supported")
    if format is not None:
        print("logging.basicConfig: format arg is not supported")
