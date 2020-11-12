S9-WRD-130-U1 Protocol
======================

All numbers are in hex.
Stop a configuration command at | to do a 'get' instead of a 'set' (with approp length adjust).
All commands/responses are preceded by a message length character (not including self) and an STX (x02).
This prefix is shown between [] below. There is no suffix to commands/responses.
NB: The above is *not* as stated in the manual. The manual is wrong!


Configuration commands:
=======================
These are not in the manual. They have been determined by watching what is sent/recieved to/from the
RFID reader from the given config EXE (Windows). They were watched via usbmon in Linux, like this:
  1. Run the Windows reader config EXE in a VM with the RFID Reader device attached
  2. Run "sudo modprobe usbmon" to load the USB monitoring tool in Linux
  3. Install and run "usbdump -d 0e6a:0317" in Linux to watch the RFID Reader (numbers are vid:pid)
  4. Do stuff in the reader config EXE

Reader action test:
-------------------
[04 02] 91 options time --> [03 02] 91 00
options: 1=beeper, 2=red LED, 4=green LED, 8=yellow LED
time:    how long to do the test in mSecs

Set USB mode:
-------------
[06 02] 92 00 02 | flags delay --> [07 02] 92 00 00 02 flags delay
flags: 80 = disable enter (default) (for keyboard wedge)
       40 = ?
       20 = ?
       10 = ?
       08 = ?
       04 = COM auto send
       02 = HID/CDC auto send
       01 = enable keyboard wedge (default) (==usb end-point 0 on interface 0)
delay: keyboard delay in mSecs (default=5mS)

Reset to factory settings:
--------------------------
[02 02] A3 --> [03 02] A3 00

Reboot reader:
--------------
[02 02] A2 --> [03 02] A2 00

Set reader card mode:
---------------------
[08 02] 92 02 04 | flags scan_time same_card_time 00 --> [09 02] 92 02 00 02 04 flags scan_time same_card_time status
flags:          80=auto, 40=same card, 20=check UID, 10=?, 8=?, 4=?, 2=beep, 1=LED (default=C3)
scan_time:      time in units of 10mS (default=5, i.e. 50mS)
same_card_time: time in units of 100mS (default=10, i.e. 1Sec)
status:         =00 iff been set since factory reset, =0F when 'get' after a factory reset

Set UART baudrate:
------------------
[05 02] 92 06 01 | rate --> [06 02] 92 00 06 01 rate
rate: 1=1200, 2=2400, 3=4800, 4=7200, 5=9600, 6=14400, 7=19200, 8=38400, 9=57600, A=115200 (default), 9A=default(?)

Set Wiegand:
------------
[05 02] 92 07 01 | mode --> [06 02] 92 00 07 01 mode
mode: 0=off (default), 1=26 bits, 2=34, 3=35, 4=42, 5=50, 6=58, 7=66 bits

Set auto read UID options:
--------------------------
[0A 02] 92 08 06 | read_bit_shift read_byte_shift auto_read flags format read_bytes_max -->
                   [0B 02] 92 00 08 06 read_bit_shift read_byte_shift auto_read flags format read_bytes_max
read_bit_shift:  0..16 (default=0)
read_byte_shift: 0..16 (default=0)
auto_read:       0=no, 1=yes (default)
flags:           1=not MSB first (default), 2=MSB first, 4=dec reverse
format:          0=ascii, 1=hex, 2=dec, 3..8=various hex to dec groupings (default=hex)
read_bytes_max:  0..32 (default=0)


Usage commands:
===============
These are as in the manual but commands must be preceded by length,STX,"A" and responses are also
preceded by this prefix followed by an error code (00=OK) then the response. There is no suffix,
the command/response ends at the specified length.

Get UHF power:
--------------
[07 02] 41 4E 30 2C 30 30 --> [06 02] 41 00 4E hh power
hh:    reflects whatever was used by 'set'
power: 30=-2dBm, 31=-1, 32=0 .. 44=27dBm (default 44)

Set UHF power:
--------------
[07 02] 41 4E 31 2C hh power --> [06 02] 41 00 4E hh power
hh:    AFAICT this is ignored, but manual says use 30
power: as above

Get frequency range:
--------------------
[07 02] 41 4E 34 2C 30 30 --> [06 02] 41 00 4E 30 range
range: 31=US, 32=TW, 33=CN, 34=CN2, 35=EU, 36=JP, 37=KR, 38=VN, 39=EU2, 41=IN

Set frequency range:
--------------------
[07 02] 41 4E 35 2C 30 range --> [06 02] 41 00 4E 30 range
range: as above

Read tag EPC ID:
----------------
[03 02] 41 51 --> [?? 02] 41 00 51 pc_word epc 
pc_word: dunno what that is   ( 4 characters)
epc:     the EPC from the tag (24 characters)
crc16:   CRC 16 of what?      ( 4 characters)
Best to treat whole 32 character string as the EPC, OK as long as desktop read is reliable (no CRC error).
