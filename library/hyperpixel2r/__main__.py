import signal

from . import Touch


if __name__ == "__main__":
    touch = Touch()

    print("HyperPixel 2 Round: Touch Test")

    @touch.on_touch
    def handle_touch(touch_id, x, y, state):
        print(touch_id, x, y, state)

    signal.pause()
