#!/usr/bin/env python3
import os
import pygame
from pygame import gfxdraw
import math
import time
import datetime
from colorsys import hsv_to_rgb
from hyperpixel2r import Touch


"""
HyperPixel 2 Clock

Run with: sudo SDL_FBDEV=/dev/fb0 python3 clock.py
"""


class Hyperpixel2r:
    screen = None

    def __init__(self):
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print("I'm running under X display = {0}".format(disp_no))

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
        self.screen = pygame.display.set_mode((640, 480), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.NOFRAME | pygame.HWSURFACE, 16)
        self.screen.fill((0, 0, 0))
        pygame.display.update()

        # For some reason the canvas needs a 7px vertical offset
        # circular screens are weird...
        self.center = (240, 247)
        self._radius = 240

        # Distance of hour marks from center
        self._marks = 220

        self._running = False
        self._origin = pygame.math.Vector2(*self.center)
        self._clock = pygame.time.Clock()
        self._colour = (255, 0, 255)

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

    def touch(self, x, y, state):
        touch = pygame.math.Vector2(x, y)
        distance = self._origin.distance_to(touch)
        angle = pygame.math.Vector2().angle_to(self._origin - touch)
        angle %= 360

        value = (distance / 240.0)
        value = min(1.0, value)
        self._colour = tuple([int(c * 255) for c in hsv_to_rgb(angle / 360.0, value, 1.0)])

    def _get_point(self, origin, angle, distance):
        r = math.radians(angle)
        cos = math.cos(r)
        sin = math.sin(r)
        x = origin[0] - distance * cos
        y = origin[1] - distance * sin
        return x, y

    def _circle(self, colour, center, radius, antialias=True):
        x, y = center
        if antialias:
            gfxdraw.aacircle(self.screen, x, y, radius, colour)
        gfxdraw.filled_circle(self.screen, x, y, radius, colour)

    def _line(self, colour, start, end, thickness):
        # Draw a filled, antialiased line with a given thickness
        # there's no pygame builtin for this so we get technical.
        start = pygame.math.Vector2(start)
        end = pygame.math.Vector2(end)

        # get the angle between the start/end points
        angle = pygame.math.Vector2().angle_to(end - start)

        # angle_to returns degrees, sin/cos need radians
        angle = math.radians(angle)

        sin = math.sin(angle)
        cos = math.cos(angle)

        # Find the center of the line
        center = (start + end) / 2.0

        # Get the length of the line,
        # half it, because we're drawing out from the center
        length = (start - end).length() / 2.0

        # half thickness, for the same reason
        thickness /= 2.0

        tl = (center.x + length * cos - thickness * sin,
              center.y + thickness * cos + length * sin)
        tr = (center.x - length * cos - thickness * sin,
              center.y + thickness * cos - length * sin)
        bl = (center.x + length * cos + thickness * sin,
              center.y - thickness * cos + length * sin)
        br = (center.x - length * cos + thickness * sin,
              center.y - thickness * cos - length * sin)

        gfxdraw.aapolygon(self.screen, (tl, tr, br, bl), colour)
        gfxdraw.filled_polygon(self.screen, (tl, tr, br, bl), colour)

    def run(self):
        self._running = True
        while self._running:
            # self._colour = tuple([int(c * 255) for c in hsv_to_rgb(time.time() / 12.0, 1.0, 1.0)])
            now = datetime.datetime.now()

            a_s = now.second / 60.0 * 360.0

            a_m = now.minute / 60.0 * 360.0
            a_m += (now.second / 60.0) * (360.0 / 60)

            a_h = (now.hour % 12) / 12.0 * 360.0
            a_h += (now.minute / 60.0) * (360.0 / 12)

            a_s += 90
            a_m += 90
            a_h += 90

            a_s %= 360
            a_m %= 360
            a_h %= 360

            point_second_start = self._get_point(self.center, a_s, 10)
            point_second_end = self._get_point(self.center, a_s, self._marks - 30)

            point_minute_start = self._get_point(self.center, a_m, 10)
            point_minute_end = self._get_point(self.center, a_m, self._marks - 60)

            point_hour_start = self._get_point(self.center, a_h, 10)
            point_hour_end = self._get_point(self.center, a_h, self._marks - 90)

            # Clear the center of the clock
            # Black circle on a black background so we don't care about aa
            self._circle((0, 0, 0), self.center, self._radius, antialias=False)

            for s in range(60):
                a = 360 / 60.0 * s
                end = self._get_point(self.center, a, self._marks + 5)
                self._line(self._colour, self.center, end, 3)

            self._circle((0, 0, 0), self.center, self._marks - 5)

            for s in range(12):
                a = 360 / 12.0 * s
                x, y = self._get_point(self.center, a, self._marks)

                r = 5
                if s % 3 == 0:
                    r = 10

                x = int(x)
                y = int(y)

                self._circle(self._colour, (x, y), r)

            # Draw the second, minute and hour hands
            self._line(self._colour, point_second_start, point_second_end, 3)
            self._line(self._colour, point_minute_start, point_minute_end, 6)
            self._line(self._colour, point_hour_start, point_hour_end, 11)

            # Draw the hub
            self._circle((0, 0, 0), self.center, 20)
            self._circle(self._colour, self.center, 10)

            pygame.display.flip()
            self._clock.tick(30)  # Aim for 30fps


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
