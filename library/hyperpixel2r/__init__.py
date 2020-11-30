import smbus2
import struct
import RPi.GPIO as GPIO


__version__ = '0.0.1'


class Touch:
    def __init__(self, bus=11, i2c_addr=0x15, interrupt_pin=27):
        self._i2c_addr = i2c_addr
        self._interrupt_pin = interrupt_pin
        self._bus = smbus2.SMBus(bus)
        self._callback_handler = None
        self._touches = {}

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._interrupt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self._interrupt_pin, edge=GPIO.FALLING, callback=self._handle_interrupt, bouncetime=1)

    def on_touch(self, handler):
        self._callback_handler = handler

    def _handle_interrupt(self, pin):
        count = self._bus.read_byte_data(self._i2c_addr, 0x02)
        # We don't get release events unless we always read both touches
        count = 2
        if count > 0:
            data = self._bus.read_i2c_block_data(self._i2c_addr, 0x03, count * 6)
            for i in range(count):
                offset = i * 6
                touch_status = False
                touch = data[offset:offset + 6]
                touch_event = touch[0] & 0xf0
                touch_id = (touch[2] & 0xf0) >> 4
                touch[0] &= 0x0f  # Mask out event_flg
                touch[2] &= 0x0f  # Mask out touch_ID
                tx, ty, p1, p2 = struct.unpack(">HHBB", bytes(touch))

                if touch_event & 128:
                    touch_status = True

                if touch_event & 64:
                    touch_status = False

                new_touch = touch_id, tx, ty, touch_status

                current_touch = self._touches.get(touch_id, None)

                if new_touch != current_touch:
                    self._touches[touch_id] = new_touch
                    if callable(self._callback_handler):
                        self._callback_handler(*self._touches[touch_id])
