# Board name for use by rshell and fellsafe
# By convention board names are programming language names as a single word in lower case.
# The board name is used to construct the WiFi AP ssid and the web server name, like this:
#   fellsafe-<boardName>.local
# The 'fellsafe' prefix is fixed, the '.local' suffix is also fixed and is compatible with
# the server being discoverable, via mDNS, on the local network.
name = "java"

# Used in main.py to determine whether to start Fellsafe or just drop
# through to the REPL. Iff True drop through to the REPL.
debug = True

# Used by gateway.py to connect the mobile modem
# This is assuming we are using a Things Mobile sim.
apn = 'pepperWeb'
