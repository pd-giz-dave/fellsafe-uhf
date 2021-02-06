""" history
    2021-02-06 DCN: created
    """
""" description
    Provide a 'console' to capture sys.stdout/err (via os.dupterm)
    The captured output is in a cyclic buffer.
    """

import uos as os
import uio as io

class Console(ByteStream):
    def __init__(self,buf_size=None):
        super().__init__(buf_size)
        self.prev = os.dupterm(self)

    def __del__(self):
        os.dupterm(self.prev)

class ByteStream(io.BytesIO):
    def __init__(self,buf_size=1024):
        self.buf  = bytearray(buf_size)
        self.size = buf_size
        self.wptr = 0
        self.rptr = 0

    def write(self, data):
        # limit data size to our size, chop leading data iff too big
        # wptr is current write position, this increments forever, so we have to wrap as required
        # data to be saved may be split if it wraps past end of buffer
        # return number of bytes written
        # TODO: implement ByteStream.write
        return 0

    def readinto(self, data, nbytes=0):
        # read nbytes into data buffer, as many as will fit or nbytes or as many as available, return bytes stored
        # rptr is current read position, this increments forever, so we have to wrap as required
        # rptr is always <= wptr
        # data available is that between rptr and wptr up to a max of our buf size
        # the available data may be in two pieces if it wraps past the end of the buffer
        # TODO: implement ByteStream.readinto
        return 0

    def read(self,nbytes=0):
        # read up to nbytes, return a bytes object
        available = self.wptr - self.rptr
        if available <= 0: return b''  # nothing available
        buf = bytearrary(available)
        rbytes = self.readinto(buf,nbytes)
        return buf[:rbytes]
