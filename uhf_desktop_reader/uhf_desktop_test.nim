## Libusb experiments

import
  libusb,
  strutils,
  strformat

const
  #This is the Megawin Technology Co., Ltd RFID Reader (a desktop UHF reader/writer)
  ReaderVendorId  = 0x0e6a
  ReaderProductId = 0x0317
  #These are the in/out endpoints to the reader, they are on inteface #1
  ReaderInterface     = 1                #the interface our end-points are on
  KeyboardInEP:cuchar = char(0x81)       #reading the keyboard "wedge"
  ReaderInEP  :cuchar = char(0x82)       #reading command responses
  ReaderOutEP :cuchar = char(0x03)       #writing commands
  #There is no documentation on how to configure the reader - would need to reverse engineer their Windows app!!
  ReaderTimeOut = 5000                   #time-out in millisecs for reading/writing to the RFID Reader
  #Reader setup commands
  #NB: The user manual for the RF reader is inaccurate. It specifies the commands but the leading/trailing
  #    characters are not as stated. By monitoring the USB streams (as shown by usbdump when mod usbmon is
  #    loaded) the actual prefix is character count, then STX (x02), then the 'A' character, then the command
  #    as stated in the manual. For reader configuration commands its length,STX,x92 then the command.
  #    The responses are length, then STX, then the command prefix (A), then the command response as stated
  #    in the manual. For configuration commands the response is length,STX,prefix (x92), error code, then
  #    the response. See full description elsewhere of reverse engineered commands/responses.
  ReaderCommandHeader   = "\x02"
  ReaderReset           = "\xA3"
  ReaderConfig          = "\x92"         #prefix to commands that change the reader configuration in some way
  ReaderOp              = "A"            #prefix to commands as specified in the user manual
  ReaderDisableKeyboard = "\x92\x00\x02\x81\x05"
  ReaderSetForEU        = "N5,05"
  ReaderGetEPC          = "Q"

type
  ReaderHandle    = ptr LibusbDeviceHandle
  ReaderException = object of CatchableError
  ReaderOp        = enum
                      OpenSession,       #open the USB session
                      CloseSession,      #close the USB session
                      OpenReader,        #find and open the RFID reader, auto starts the USB session
                      CloseReader        #close the reader and the session

var
  readerConnected: ReaderHandle = nil    #is nil if not connected
  libusbIsOpen   : bool         = false  #true when we've init'd libusb

proc checkLibusb(op: ReaderOp = OpenSession) =
  ## Init libusb if not already done so.
  ## Note its init'd state in the global libusbIsOpen.
  ## An exception is raised if cannot init libusb.
  ## We use the default context as there is only one in this app.
  case op:
  of OpenSession:
    if libusbIsOpen:
      # already open, silent no-op
      discard
    else:
      # not open and want it open, so do it
      let r = libusbInit(nil)
      if r < 0:
        raise newException(ReaderException,&"checkLibusb: Failed to initialize libusb, error is {$libusbErrorName(r)}")
      libusbIsOpen = true
  of CloseSession:
    if libusbIsOpen:
      # open and want it closed, so do it
      libusbExit(nil)
      libusbIsOpen = false
    else:
      # already closed, silent no-op
      return
  else:
    # illegal op
    raise newException(ReaderException,&"checkLibusb: op must be {$OpenSession} or {$CloseSession}, given {$op}")
  
proc connectReader(op: ReaderOp = OpenReader): ReaderHandle =
  ## Check our reader is present then open and claim it.
  ## If the reader is not present, raises an exception.
  ## We expect 0e6a:0317 for the S9-WRD-130-U1 UHF dekstop reader/writer.
  ## Returns the reader handle.
  ## Libusb sessions are started/stopped as required
  case op:
  of OpenReader:
    checkLibusb(OpenSession)
    if isNil readerConnected:
      #we're not connected, attempt connect now
      var devices: ptr LibusbDeviceArray = nil
      let c = libusbGetDeviceList(nil, addr devices)
      # iterate all devices looking for our RFID reader
      for i in 0..<c:
        if devices[i] == nil:
          break
        var desc: LibusbDeviceDescriptor
        let r = libusbGetDeviceDescriptor(devices[i], addr desc)
        if (r < 0):
          raise newException(ReaderException,
                             &"connectReader: Failed to get device descriptor for device #{$i} of {$c}," &
                             &" error is {$libusbErrorName(r)}")
        elif desc.idVendor == ReaderVendorId and desc.idProduct == ReaderProductId:
          #found our RFID reader, now open it
          let r = libusbOpen(devices[i],addr readerConnected)
          if (r < 0):
            raise newException(ReaderException,&"connectReader: Cannot open RFID reader, error is {$libusbErrorName(r)}")
          else:
            #opened OK, now claim it
            discard libusbSetAutoDetachKernelDriver(readerConnected,cint(true))  #not always supported, so don't care if get error
            let r = libusbClaimInterface(readerConnected,ReaderInterface)
            if r < 0:
              raise newException(ReaderException,&"connectReader: Cannot claim RFID reader interface, error is {$libusbErrorName(r)}")
          #done it
          break
        else:
          #not found it yet, keep looking
          discard
      if isNil readerConnected:
        #can't find it
        raise newException(ReaderException,&"connectReader: Cannot find RFID reader among {$c} devices")
      #we're done, reader found and opened, dump on devices list as no longer needed
      libusbFreeDeviceList(devices, 1)
  of CloseReader:
    if isNil readerConnected:
      #already closed, silent no-op
      discard
    else:
      #its open, so release and close it now
      discard libusbReleaseInterface(readerConnected,ReaderInterface)
      libusbClose(readerConnected)       #assume it succeeds
      readerConnected = nil              #not connected any more
      checkLibusb(CloseSession)
  else:
    # illegal op
    raise newException(ReaderException,&"connectReader: op must be {$OpenReader} or {$CloseReader}, given {$op}")
  return readerConnected

proc commandReader(c: string): string =
  ## Send a command to the reader and return the response.
  ## Connects to the reader iff required.
  ## Reader commands are formatted as <length><STX>command and sent to the 'out' end-point
  ## Responses are formatted as: <length><stx>response and read from the 'in' end-point
  let reader = connectReader(OpenReader) #we've already connected once, so we know this will succeed
  let command: string = char(c.len+1) & "\2" & c
  var transferred: cint
  let r1 = libusbInterruptTransfer(reader,ReaderOutEP,unsafeAddr command[0],cint(command.len),addr transferred,cuint(ReaderTimeOut))
  if r1 < 0:
    return &"Cannot send command, error was {$r1}:{libusbErrorName(r1)}"
  if transferred < command.len:
    return &"Command length is {command.len} characters but only {$transferred} actually sent"
  var response: string = spaces(256)
  transferred = 0
  let r2 = libusbInterruptTransfer(reader,ReaderInEP,unsafeAddr response[0],cint(response.len),addr transferred,cuint(ReaderTimeOut))
  if r2 < 0:
    return &"Cannot read response, error was {$r2}:{libusbErrorName(r2)}, transferred was: {$transferred}"
  if transferred < 1:
    return &"No response after {$(ReaderTimeOut/1000)} secs"
  return response

#--------------------------------------

echo "Starting..."
try:
  discard connectReader(OpenReader)
except ReaderException as e:
  echo e.msg
  quit(1)
echo "Connected"
while true:
  echo "Enter command to send (blank to quit):"
  let command = readLine(stdin)
  if command == "": break
  echo &"For command: {command}"
  let response = commandReader(command)
  echo &"Response was: {response}"
echo "Stopping..."
discard connectReader(CloseReader)
echo "Stopped"
