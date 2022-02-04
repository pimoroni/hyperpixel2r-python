# HyperPixel 2" Round Touch Driver

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/pimoroni/hyperpixel2r-python/Python%20Tests)](https://github.com/pimoroni/hyperpixel2r-python/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/hyperpixel2r-python/badge.svg?branch=master)](https://coveralls.io/github/pimoroni/hyperpixel2r-python?branch=master)
[![PyPi Package](https://img.shields.io/pypi/v/hyperpixel2r.svg)](https://pypi.python.org/pypi/hyperpixel2r)
[![Python Versions](https://img.shields.io/pypi/pyversions/hyperpixel2r.svg)](https://pypi.python.org/pypi/hyperpixel2r)

# Pre-requisites

You must install the HyperPixel 2r drivers which enable an i2c bus for the touch IC - https://github.com/pimoroni/hyperpixel2r

Make sure you edit `/boot/config.txt` and add `:disable-touch` after `hyperpixel2r`, like so:

```
dtoverlay=hyperpixel2r:disable-touch
```

This disables the Linux touch driver so Python can talk to the touch IC.

# Installing

Stable library from PyPi:

* Just run `pip3 install hyperpixel2r`

In some cases you may need to use `sudo` or install pip with: `sudo apt install python3-pip`

Latest/development library from GitHub:

* `git clone https://github.com/pimoroni/hyperpixel2r-python`
* `cd hyperpixel2r-python`
* `sudo ./install.sh`

# SDL/Pygame on Raspberry Pi

## pygame.error: No video mode large enough for 640x480

The version of Pygame shipped with Raspberry Pi OS doesn't like non-standard resolutions like 480x480. You can fake a 640x480 standard display by forcing HDMI hotplug, and then just to a 480x480 region to display on HyperPixel 2.0" round. In `/boot/config.txt`:

```text
# Force 640x480 video for Pygame / HyperPixel2r
hdmi_force_hotplug=1
hdmi_mode=1
hdmi_group=1
```

# Usage

Set up touch driver instance:

```python
touch = Touch(bus=11, i2c_addr=0x15, interrupt_pin=27):
```

Touches should be read by decorating a handler with `@touch.on_touch`.

The handler should accept the arguments `touch_id`, `x`, `y` and `state`.

* `touch_id` - 0 or 1 depending on which touch is tracked
* `x` - x coordinate from 0 to 479
* `y` - y coordinate from 0 to 479
* `state` - touch state `True` for touched, `False` for released

For example:

```python
@touch.on_touch
def handle_touch(touch_id, x, y, state):
    print(touch_id, x, y, state)
```
