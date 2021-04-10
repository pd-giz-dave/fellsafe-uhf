""" History
    2021-02-01 DCN: Created for use by uasyncio.core
    2021-04-05 DCN: Add deque wrapper
    """
""" Description
    A wrapper around utimeq.utimeq that copes with time roll-over.
    Created initially to isolate roll over effects from uasyncio.core
    It uses a time reference of time.ticks_ms() at system start.
    Thereafter all times are relative to that and it detects when it rolls over
    (i.e. our relative time goes backwards) and re-adjusts everything.
    """

import ucollections
import utimeq
import utime as time

MAX_WAITQ_TIME = 48 * 60 * 60 * 1000     # max time wait Q can deal with without creating rollover issues (48 hours in milliseconds)

DEBUG = 0
log = None

def set_debug(val):
    global DEBUG, log
    DEBUG = val
    if val:
        # import late so no dependency unless caller asks for it
        import ulogging as logging
        log = logging.getLogger("waitq")
        log.info('logging enabled')

def deque(iter,maxlen,flags):
    """ just a wrapper around ucollections so uasyncio does not need to know about ucollections """
    return ucollections.deque(iter,maxlen,flags)

class WaitQ:
    def __init__(self,q_len):
        self.q_len = q_len
        self.waitq = self._make(q_len)

        self.first_time = time.ticks_ms()      # our time reference
        self.last_time  = self._time()         # our time roll-over detector (see _delay)
                    
    def _make(self,q_len):
        """ a wrapper around utimeq.utimeq """
        return utimeq.utimeq(q_len)

    def _reset(self):
        """ this is called when we detect that the time has rolled over

            to stop all currently waiting tasks from waiting forever we
            pop and re-push them all with a very short delay. We preserve
            the order but not the time (we assume running a task early does
            not matter, but the order they run in might).
            """
        oldq       = self.waitq                # note the existing q
        self.waitq = self._make(self.q_len)    # make a new q to copy everything into
        item       = [0,0,0]                   # popped item
        item_delay = 0                         # set highest priority for the first one
        while True:
            try:
                oldq.pop(item)                                 # get existing item
                item[0] = self.time(self.time() + item_delay)  # set the new time
                self.waitq.push(item[0],item[1],item[2])       # put it on our new q
                item_delay = item_delay + 1                    # set priority for the next one
            except IndexError:
                break
        if __debug__ and DEBUG:
            self.log.debug('_reset:re-pushed %s items',item_delay)
        
    def _time(self,t=None):
        """ given a time, normalise it for insertion in our waitq
            if no time given use the current time
            """
        if t is None:
            t = time.ticks_diff(time.ticks_ms(),self.first_time)
        if t > MAX_WAITQ_TIME:
            orig_t = t
            t      = int(orig_t % MAX_WAITQ_TIME)
            if __debug__ and DEBUG:
                log.debug('_time:wrapping time from %s to %s', orig_t, t)
        return int(t)

    def _peek(self):
        """ a wrapper around peektime() as it can tell lies """
        t = self.waitq.peektime()
        if t > MAX_WAITQ_TIME:
            raise RuntimeError('peektime too big at {}, limit is {}'.format(t,MAX_WAITQ_TIME))
        return t

    def push(self,delay,callback,args):
        """ push the given item onto our waitq, api same as utimeq.push
            NB: Unlike utimeq.push we take a delay and not a time
            """
        wtime = self._time(self._time()+delay)
        if __debug__ and DEBUG:
            log.debug('push:pushing: %s, now: %s', (wtime,callback,args), self._time())
        self.waitq.push(wtime,callback,args)
        if __debug__ and DEBUG:
            t = self._peek()
            if t > wtime:
                #something is telling porkies!
                raise RuntimeError('pushed {} but peektime is bigger at {}'.format(wtime,t))

    def delay(self,q_item = None):
        """ if the next item in the wait q has reached its time return 0
            otherwise return how much longer it has to wait
            if the wait q is empty -1 is returned
            if q_item is given it must be a *list* of 3 items and is updated with
            the waitq item if its time has been reached (the item is popped), otherwise
            the item is not popped.
            """
        try:
            tnow = self._time()
            if tnow < self.last_time:
                # this means time has rolled over
                self._reset()
                self.last_time = tnow          # reset the rollover detector
            t = self._peek()
            delay = time.ticks_diff(t, tnow)
            if delay > 0:
                #not there yet
                if __debug__ and DEBUG:
                    log.debug('_delay:shortest delay is %s, t: %s, now: %s', delay, t, tnow)
                return delay
            else:
                # its time
                if q_item is not None:
                    self.waitq.pop(q_item)
                    if __debug__ and DEBUG:
                        log.debug('_delay:item ready: %s, now: %s', q_item, tnow)
                return 0
        except IndexError:
            # wait q empty
            return -1
