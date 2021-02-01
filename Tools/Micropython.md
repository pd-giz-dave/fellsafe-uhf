# Hardware

As of Jan 21, the idea now is to do everything in the FiPy and drop the Pi Zero, also drop the separate RTC module and use the one in the FiPy.
So the hardware now reduces to: FiPy+PyTrack+RS232+PSU+UHF
And the language reduces to Python everywhere (inc the web front-end via Transcrypt).

# Micropython and the FiPy

The Fipy module is programmed in Micorpython.
I prefer 'rshell' over the 'Pymakr' VS Code plugin.
However rshell needs a tweak to work with modern a FiPy, and that is to use the @ character for flow control instead of x06 as x06 looks like Ctrl-F which does a reset and safe boot.
Other modules used are uasyncio - but you must be careful which version to get, the one dated 2018 works, the one dated 2019 does not - and picoweb (which also must be tweaked!) and utemplate and transcrypt. That lot together allow for a Django like experience and Python is used at both ends - server-side and client-side!
