import logging
from typing import Optional, Tuple
import pygame
import cups
import io
import gpio4
import picamera

LOG = logging.getLogger(__name__)

JOYBUTTONA = 1
JOYBUTTONB = 2
JOYBUTTONUP = 10
JOYBUTTONDOWN = 11
JOYBUTTONLEFT = 12
JOYBUTTONRIGHT = 13
JOYBUTTONSELECT = 8
JOYBUTTONSTART = 9

class Io:
    def __init__(self):
        self.gpio = gpio4.GPIO()
        self.gpio.setmode(gpio4.constants.BOARD_NANO_PI)
        self.gpio.setup(pin=[self.gpioport,], state=gpio4.GPIO.OUT, initial=gpio4.GPIO.HIGH)
        self.cups = cups.Connection()

        self.camera = picamera.PiCamera()
        pygame.joystick.Joystick(0).init()

    def get_joy_input(self) -> Optional[pygame.event.Event]:
        pygame.event.clear()
        while event := pygame.event.wait():
            print(event.__class__)
            if event.type == pygame.QUIT or\
			(event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return None

            elif event.type == pygame.JOYBUTTONDOWN:
                return event.button

    def take_photo(self, resolution: Tuple[int] = (2592, 1944)) -> pygame.Surface:
        with io.BytesIO() as buffer:
            self.camera.resolution = resolution
            self.flash_on()
            self.camera.capture(buffer, format='rgba', use_video_port=False)
			#resolution = (2592, 1952)#FIXME: Resolution trick!! C'est hyper crade, pas trouvé mieux.
            img = pygame.image.fromstring(buffer.getvalue(), resolution, 'RGBA').convert()
        if img.get_at((10, 10))[:3] == (0, 0, 0):
            #FIXME: Bug of picam. Sometimes image is black, try to takz it again
            img = self.take_photo(resolution)
        self.flash_off()
        return img

    def flash_on(self):
        if self.conf.flash_enabled():
            self.gpio.output(self.gpioport, gpio4.GPIO.LOW)

    def flash_off(self):
        self.gpio.output(self.gpioport, gpio4.GPIO.HIGH)
