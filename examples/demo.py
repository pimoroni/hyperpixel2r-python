#!/usr/bin/env python3
import os
import pygame
import time
import colorsys
import math
from hyperpixel2r import Touch


print("""HyperPixel 2 Lots of Circles Demo

Run with: sudo SDL_FBDEV=/dev/fb0 python3 demo.py

""")


hue_to_rgb = []


for i in range(0, 255):
    hue_to_rgb.append(colorsys.hsv_to_rgb(i / 255.0, 1, 1))


# zoom tunnel
def tunnel(x, y, step):
    u_width = 32
    u_height = 32
    speed = step / 100.0
    x -= (u_width / 2)
    y -= (u_height / 2)
    xo = math.sin(step / 27.0) * 2
    yo = math.cos(step / 18.0) * 2
    x += xo
    y += yo
    if y == 0:
        if x < 0:
            angle = -(math.pi / 2)
        else:
            angle = (math.pi / 2)
    else:
        angle = math.atan(x / y)
    if y > 0:
        angle += math.pi
    angle /= 2 * math.pi  # convert angle to 0...1 range
    hyp = math.sqrt(math.pow(x, 2) + math.pow(y, 2))
    shade = hyp / 2.1
    shade = 1 if shade > 1 else shade
    angle += speed
    depth = speed + (hyp / 10)
    col1 = hue_to_rgb[step % 255]
    col1 = (col1[0] * 0.8, col1[1] * 0.8, col1[2] * 0.8)
    col2 = hue_to_rgb[step % 255]
    col2 = (col2[0] * 0.3, col2[1] * 0.3, col2[2] * 0.3)
    col = col1 if int(abs(angle * 6.0)) % 2 == 0 else col2
    td = .3 if int(abs(depth * 3.0)) % 2 == 0 else 0
    col = (col[0] + td, col[1] + td, col[2] + td)
    col = (col[0] * shade, col[1] * shade, col[2] * shade)
    return (col[0] * 255, col[1] * 255, col[2] * 255)


class Hyperpixel2r:
    screen = None

    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
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
                print('Driver: {0} failed.'.format(driver))
                continue
            found = True
            break

        if not found:
            raise Exception('No suitable video driver found!')

        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        print("Framebuffer size: {:d} x {:d}".format(*size))
        self.screen = pygame.display.set_mode((640, 480), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.NOFRAME | pygame.HWSURFACE)
        self.screen.fill((0, 0, 0))
        pygame.display.update()

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

    def demo(self):
        while True:
            t = int(time.time() * 40)
            for x in range(32):
                for y in range(32):
                    r, g, b = tunnel(x, y, t)
                    r = min(255, int(r))
                    g = min(255, int(g))
                    b = min(255, int(b))
                    pygame.draw.circle(self.screen, (r, g, b), ((x * 15) + 6, (y * 15) + 6 + 7), 7)

            pygame.display.flip()

    def touch(self, x, y, state):
        pass


display = Hyperpixel2r()
touch = Touch()


@touch.on_touch
def handle_touch(touch_id, x, y, state):
    display.touch(x, y, state)


display.demo()
