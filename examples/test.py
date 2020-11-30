#!/usr/bin/env python3
import os
import pygame
import time
import signal
import math
from hyperpixel2r import Touch


"""
HyperPixel 2 Test

Run with: sudo SDL_FBDEV=/dev/fb0 python3 test.py
"""


class Hyperpixel2r:
    screen = None

    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print ("I'm running under X display = {0}".format(disp_no))

        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print('Driver: {0} failed. ({1})'.format(driver, dir(pygame.error)))
                continue
            found = True
            break

        if not found:
            raise Exception('No suitable video driver found!')

        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        print("Framebuffer size: {:d} x {:d}".format(*size))
        self.screen = pygame.display.set_mode((640, 480), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.NOFRAME | pygame.HWSURFACE)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))        
        # Initialise font support
        pygame.font.init()
        # Render the screen
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


# Create an instance of the PyScope class
display = Hyperpixel2r()
touch = Touch()

@touch.on_touch
def handle_touch(touch_id, x, y, state):
    display.touch(x, y, state)


display.test()
