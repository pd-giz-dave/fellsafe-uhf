# Board name for use by rshell and fellsafe.py and fipy.py
# By convention board names are programming language names as a single word in lower case.
name = "python"  #this becomes the AP ssid suffix, e.g. 'fellsafe-python'

# Used in main.py to determine whether to start Fellsafe or just drop
# through to the REPL. Iff True drop through to the REPL.
debug = True

# Used by gateway.py to connect the LTE-M modem
# This is assuming we are using a Things Mobile sim.
apn = 'pepperWeb'
