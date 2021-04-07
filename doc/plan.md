# Implementation Plan

## Build Software Development System
### Requirements
- provide for unit testing
- provide for simulation of an event
- provide for simulation of the Pi Zero hardware on a Linux PC
- provide for simulation of the FiPy hardware on a Linux PC (esp Micropython)
- ???
### Tools
- Pymakr to interface with the FiPy
- vscode as the main IDE
- Nim as the Pi Zero language
- Micropython as the FiPy language
- ???
### Architecture philosophy
- in the Pi Zero use a process per element using pipes to communicate
- in the FiPy use a thread per element and shared memory to communicate
- in the RO and marshalls browsers use Nim+Karax for the HTML and JS and the Petal CSS library

## Phase 1 - UHF handler
The objective of phase 1 is to build and verify the UHF tag system actually works as expected 'in the wild'.
If it does not then there is no point in going any further!
### Define APIs
- Define Global State Controller API
- Define Event Web Server REST API
- ???
### Build interfaces (see software config diagram)
- UHF Interface
- GPS Interface
- FiPy Interface
- RTC
- Battery monitor
- Global State Controller
- ???
### Build software test system
- Fake UHF tag reads
- Fake GPS locations
- Fake FiPy Module
- Fake Battery monitor
- Build Event Web Server stub (a CLI REPL)
- Test software system
- ???
### Build UHF hardware test system
- Wire-up Pi Zero modules (see hardware config diagram)
- Migrate code to the Pi Zero
- Connect real UHF reader
- Connect real GPS
- Connect real RTC
- Connect real battery
- Build Pi Zero boot scripts
- Test UHF hardware system (especially simulate a mass start to test read rate)
- ???

## Phase 2 - web app front-end
The objective of phase 2 is to provide the user interface so that user feedback can be incorporated as early as possible.

## Phase 3 - inter-station commms
This brings in the FiPy module and the Pymesh system to provide communication between stations where there is no mobile signal.

## Phase 4 - Fellsafe server
This is the public facing web interface that provides real-time feedback during an event and consolidates results afterwards.
