# HyperPixel 2" Round Touch Driver

[![Build Status](https://travis-ci.com/pimoroni/hyperpixel2r-python.svg?branch=master)](https://travis-ci.com/pimoroni/hyperpixel2r-python)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/hyperpixel2r-python/badge.svg?branch=master)](https://coveralls.io/github/pimoroni/hyperpixel2r-python?branch=master)
[![PyPi Package](https://img.shields.io/pypi/v/hyperpixel2r.svg)](https://pypi.python.org/pypi/hyperpixel2r)
[![Python Versions](https://img.shields.io/pypi/pyversions/hyperpixel2r.svg)](https://pypi.python.org/pypi/hyperpixel2r)

# Pre-requisites

You must install the HyperPixel 2r drivers which enable an i2c bus for the touch IC - https://github.com/pimoroni/hyperpixel4/tree/hp2-round

# Installing

Stable library from PyPi:

* Just run `pip3 install hyperpixel2r`

In some cases you may need to use `sudo` or install pip with: `sudo apt install python3-pip`

Latest/development library from GitHub:

* `git clone https://github.com/pimoroni/hyperpixel2r-python`
* `cd hyperpixel2r-python`
* `sudo ./install.sh`

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

# Changelog
0.0.1
-----

* Initial Release
