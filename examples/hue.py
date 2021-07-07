#!/usr/bin/env python3
import os
import pygame
import math
from colorsys import hsv_to_rgb
from hyperpixel2r import Touch
# import rgbmatrix5x5


"""
HyperPixel 2 Hue

Run with: sudo SDL_FBDEV=/dev/fb0 python3 hue.py
"""


class Hyperpixel2r:
    screen = None

    def __init__(self):
        self._init_display()

        self.screen.fill((0, 0, 0))
        pygame.display.update()

        # For some reason the canvas needs a 7px vertical offset
        # circular screens are weird...
        self.center = (240, 247)
        self.radius = 240
        self.inner_radius = 150

        self._running = False
        self._hue = 0
        self._val = 1.0
        self._origin = pygame.math.Vector2(*self.center)
        self._clock = pygame.time.Clock()

        # Draw the hue wheel as lines emenating from the inner to outer radius
        # we overdraw 3x as many lines to get a nice solid fill... horribly inefficient but it works
        for s in range(360 * 3):
            a = s / 3.0
            cos = math.cos(math.radians(a))
            sin = math.sin(math.radians(a))
            x = self.center[0] - self.radius * cos
            y = self.center[1] - self.radius * sin

            ox = self.center[0] - self.inner_radius * cos
            oy = self.center[1] - self.inner_radius * sin

            colour = tuple([int(c * 255) for c in hsv_to_rgb(a / 360.0, 1.0, 1.0)])
            pygame.draw.line(self.screen, colour, (ox, oy), (x, y), 3)

    def _init_display(self):
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        DISPLAY = os.getenv("DISPLAY")
        if DISPLAY:
            print("Display: {0}".format(DISPLAY))

        if os.getenv('SDL_VIDEODRIVER'):
            print("Using driver specified by SDL_VIDEODRIVER: {}".format(os.getenv('SDL_VIDEODRIVER')))
            pygame.display.init()
            self.screen = pygame.display.set_mode((640, 480),  pygame.DOUBLEBUF | pygame.NOFRAME | pygame.HWSURFACE, 16)
            return

        else:
            # Iterate through drivers and attempt to init/set_mode
            for driver in ['rpi', 'kmsdrm', 'fbcon', 'directfb', 'svgalib']:
                os.putenv('SDL_VIDEODRIVER', driver)
                try:
                    pygame.display.init()
                    size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
                    self.screen = pygame.display.set_mode((640, 480),  pygame.DOUBLEBUF | pygame.NOFRAME | pygame.HWSURFACE, 16)
                    print("Using driver: {0}, Framebuffer size: {1:d} x {2:d}".format(driver, *size))
                    return
                except pygame.error as e:
                    print('Driver "{0}" failed: {1}'.format(driver, e))
                    continue
                break

        raise Exception('Failed to init display: No suitable video driver found!')

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

    def get_colour(self):
        return tuple([int(c * 255) for c in hsv_to_rgb(self._hue, 1.0, self._val)])

    def touch(self, x, y, state):
        target = pygame.math.Vector2(x, y)
        distance = self._origin.distance_to(target)
        angle = pygame.Vector2().angle_to(self._origin - target)

        if distance < self.inner_radius and distance > self.inner_radius - 40:
            return

        angle %= 360
        angle /= 360.0

        if distance < self.inner_radius:
            self._val = angle
        else:
            self._hue = angle

        # print("Displaying #{0:02x}{1:02x}{2:02x} {3}".format(*self.get_colour(), angle))

    def run(self):
        self._running = True
        while self._running:
            self._colour = tuple([int(c * 255) for c in hsv_to_rgb(self._hue, 1.0, self._val)])
            pygame.draw.circle(self.screen, self.get_colour(), self.center, self.inner_radius - 10)
            pygame.draw.circle(self.screen, (0, 0, 0), self.center, self.inner_radius - 30)
            for s in range(360 * 3):
                a = s / 3.0
                cos = math.cos(math.radians(a))
                sin = math.sin(math.radians(a))
                x, y = self.center
                ox = x - (self.inner_radius - 40) * cos
                oy = y - (self.inner_radius - 40) * sin
                colour = tuple([int(c * 255) for c in hsv_to_rgb(self._hue, 1.0, a / 360.0)])
                pygame.draw.line(self.screen, colour, (ox, oy), (x, y), 3)

            pygame.display.flip()
            self._clock.tick(30)


display = Hyperpixel2r()
touch = Touch()

# uncomment to set up rgbmatrix
# rgbmatrix = rgbmatrix5x5.RGBMatrix5x5(i2c_dev=touch._bus)
# rgbmatrix.set_clear_on_exit()


@touch.on_touch
def handle_touch(touch_id, x, y, state):
    display.touch(x, y, state)
    # uncomment to set colour on rgbmatrix,
    # or try it with Mote USB or something!
    # rgbmatrix.set_all(*display.get_colour())
    # rgbmatrix.show()


display.run()
