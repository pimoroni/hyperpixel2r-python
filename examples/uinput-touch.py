#!/usr/bin/env python

import os
import signal
import sys
import time

from datetime import datetime
from threading import Timer

try:
    from evdev import uinput, UInput, AbsInfo, ecodes as e
except ImportError:
    exit("This service requires the evdev module\nInstall with: sudo pip install evdev")

try:
    import RPi.GPIO as gpio
except ImportError:
    exit("This service requires the RPi.GPIO module\nInstall with: sudo pip install RPi.GPIO")

try:
    import smbus
except ImportError:
    exit("This service requires the smbus module\nInstall with: sudo apt-get install python-smbus")


os.system("sudo modprobe uinput")

rotate = False

try:
    config = open("/boot/config.txt").read().split("\n")
    for option in config:
        if option.startswith("display_rotate="):
            key, value = option.split("=")
            if value.strip() == "0":
               rotate = True
except IOError:
    pass

DAEMON = False

CAPABILITIES = {
    e.EV_ABS : (
        (e.ABS_X, AbsInfo(value=0, min=0, max=480, fuzz=0, flat=0, resolution=1)),
        (e.ABS_Y, AbsInfo(value=0, min=0, max=480, fuzz=0, flat=0, resolution=1)),
        (e.ABS_MT_SLOT, AbsInfo(value=0, min=0, max=1, fuzz=0, flat=0, resolution=0)),
        (e.ABS_MT_TRACKING_ID, AbsInfo(value=0, min=0, max=65535, fuzz=0, flat=0, resolution=0)),
        (e.ABS_MT_POSITION_X, AbsInfo(value=0, min=0, max=480, fuzz=0, flat=0, resolution=0)),
        (e.ABS_MT_POSITION_Y, AbsInfo(value=0, min=0, max=480, fuzz=0, flat=0, resolution=0)),
    ),
    e.EV_KEY : [
        e.BTN_TOUCH, 
    ]
}

PIDFILE = "/var/run/hyperpixel2r-touch.pid"
LOGFILE = "/var/log/hyperpixel2r-touch.log"

if DAEMON:
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)

    except OSError as e:
        print("Fork #1 failed: {} ({})".format(e.errno, e.strerror))
        sys.exit(1)

    os.chdir("/")
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            fpid = open(PIDFILE, 'w')
            fpid.write(str(pid))
            fpid.close()
            sys.exit(0)
    except OSError as e:
        print("Fork #2 failed: {} ({})".format(e.errno, e.strerror))
        sys.exit(1)

    si = file("/dev/null", 'r')
    so = file(LOGFILE, 'a+')
    se = file("/dev/null", 'a+', 0)

    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def log(msg):
    sys.stdout.write(str(datetime.now()))
    sys.stdout.write(": ")
    sys.stdout.write(msg)
    sys.stdout.write("\n")
    sys.stdout.flush()

try:
    ui = UInput(CAPABILITIES, name="Touchscreen", bustype=e.BUS_USB)

except uinput.UInputError as e:
    sys.stdout.write(e.message)
    sys.stdout.write("Have you tried running as root? sudo {}".format(sys.argv[0]))
    sys.exit(0)


from hyperpixel2r import Touch


last_status = [False, False]
last_status_xy = [(0, 0), (0, 0)]


def write_status(touch_id, x, y, touch_state):
    if touch_id > 1:  # Support touches 0 and 1
        return

    if touch_state:
        ui.write(e.EV_ABS, e.ABS_MT_SLOT, touch_id)

        if not last_status[touch_id]: # Contact one press
            ui.write(e.EV_ABS, e.ABS_MT_TRACKING_ID, touch_id)
            ui.write(e.EV_ABS, e.ABS_MT_POSITION_X, x)
            ui.write(e.EV_ABS, e.ABS_MT_POSITION_Y, y)
            ui.write(e.EV_KEY, e.BTN_TOUCH, 1)
            ui.write(e.EV_ABS, e.ABS_X, x)
            ui.write(e.EV_ABS, e.ABS_Y, y)

        elif not last_status[touch_id] or (x, y) != last_status_xy[touch_id]:
            if x != last_status_xy[touch_id][0]: ui.write(e.EV_ABS, e.ABS_X, x)
            if y != last_status_xy[touch_id][1]: ui.write(e.EV_ABS, e.ABS_Y, y)
            ui.write(e.EV_ABS, e.ABS_MT_POSITION_X, x)
            ui.write(e.EV_ABS, e.ABS_MT_POSITION_Y, y)

        last_status_xy[touch_id] = (x, y)
        last_status[touch_id] = True

        ui.write(e.EV_SYN, e.SYN_REPORT, 0)
        ui.syn()

    elif not touch_state and last_status[touch_id]:
        ui.write(e.EV_ABS, e.ABS_MT_SLOT, touch_id)
        ui.write(e.EV_ABS, e.ABS_MT_TRACKING_ID, -1)
        ui.write(e.EV_KEY, e.BTN_TOUCH, 0)
        last_status[touch_id] = False

        ui.write(e.EV_SYN, e.SYN_REPORT, 0)
        ui.syn()


log("HyperPixel2r Touch daemon running...")

touch = Touch()


@touch.on_touch
def handle_touch(touch_id, x, y, state):
    write_status(touch_id, x, y, state)


signal.pause()

log("HyperPixel2r Touch daemon shutting down...")

ui.close()
