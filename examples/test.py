#!/usr/bin/env python3
import os
import pygame
import time
import signal
import math
from colorsys import hsv_to_rgb
from hyperpixel2r import Touch


"""
HyperPixel 2 Test

Run with: sudo SDL_FBDEV=/dev/fb0 python3 test.py
"""


class Hyperpixel2r:
    screen = None

    def __init__(self):
        self._init_display()

        self.screen.fill((0, 0, 0))        
        pygame.display.update()

        self._step = 0
        self._steps = [
            (255, 0, 0, 240, 100),  # Top
            (0, 255, 0, 240, 380),  # Bottom
            (255, 0, 0, 100, 240),  # Left
            (0, 255, 0, 380, 240),  # Right
            (0, 0, 255, 240, 240),  # Middle
        ]
        self._touched = False

    def _init_display(self):
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        DISPLAY = os.getenv("DISPLAY")
        if DISPLAY:
            print("Display: {0}".format(DISPLAY))

        if os.getenv('SDL_VIDEODRIVER'):
            print("Using driver specified by SDL_VIDEODRIVER: {}".format(os.getenv('SDL_VIDEODRIVER')))
            pygame.display.init()
            size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
            if size == (480, 480): # Fix for 480x480 mode offset
                size = (640, 480)
            self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.NOFRAME | pygame.HWSURFACE)
            return

        else:
            # Iterate through drivers and attempt to init/set_mode
            for driver in ['rpi', 'kmsdrm', 'fbcon', 'directfb', 'svgalib']:
                os.putenv('SDL_VIDEODRIVER', driver)
                try:
                    pygame.display.init()
                    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
                    if size == (480, 480):  # Fix for 480x480 mode offset
                        size = (640, 480)
                    self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.NOFRAME | pygame.HWSURFACE)
                    print("Using driver: {0}, Framebuffer size: {1:d} x {2:d}".format(driver, *size))
                    return
                except pygame.error as e:
                    print('Driver "{0}" failed: {1}'.format(driver, e))
                    continue
                break

        raise Exception('Failed to init display: No suitable video driver found!')

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

    def touch(self, x, y, state):
        if state:
            _, _, _, tx, ty = self._steps[self._step]
            x = abs(tx - x)
            y = abs(ty - y)
            distance = math.sqrt(x**2 + y**2)
            if distance < 90:
                self._touched = True

    def test(self, timeout=2):
        for colour in [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]:
            self.screen.fill(colour)
            print("Displaying #{0:02x}{1:02x}{2:02x}".format(*colour))
            pygame.display.update()
            time.sleep(0.25)

        for y in range(480):
            hue = y / 480.0
            colour = tuple([int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)])
            pygame.draw.line(self.screen, colour, (0, y), (479, y))

        pygame.display.update()
        time.sleep(1.0)

        while self._step < len(self._steps):
            r, g, b, x, y = self._steps[self._step]
            pygame.draw.circle(self.screen, (r, g, b), (x, y), 90)
            pygame.display.update()
            t_start = time.time()
            while not self._touched:
                if time.time() - t_start > timeout:
                    raise RuntimeError("Touch test timed out!")
            self._touched = False
            pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 90)
            pygame.display.update()
            self._step += 1


display = Hyperpixel2r()
touch = Touch()

@touch.on_touch
def handle_touch(touch_id, x, y, state):
    display.touch(x, y, state)


display.test()
