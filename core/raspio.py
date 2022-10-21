import logging
from typing import Optional, Tuple
import pygame
import cups
import io
import RPi.GPIO as GPIO
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


GPIO_PORT = 7


class Io:
    def __init__(self):
        print('IO')
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(GPIO_PORT, GPIO.OUT, initial=GPIO.HIGH)
        self.cups = cups.Connection()
        self.camera = picamera.PiCamera()
        pygame.joystick.Joystick(0).init()
        #print(pygame.joystick.get_init())
        #print('nb', pygame.joystick.get_count())

    def get_joy_input(self) -> Optional[pygame.event.Event]:
        pygame.event.clear()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    return event.button
                if event.type == pygame.JOYDEVICEADDED:
                    joy = pygame.joystick.Joystick(event.device_index)

    def take_photo(self, resolution: Tuple[int] = (2592, 1944), flash: bool=True) -> pygame.Surface:
        with io.BytesIO() as buffer:
            self.camera.resolution = resolution
            if resolution == (2592, 1944):
                resolution = (2592, 1952)
            if flash:
                self.flash_on()
            self.camera.capture(buffer, format='rgba', use_video_port=False)
			#resolution = #FIXME: Resolution trick!! C'est hyper crade, pas trouvé mieux.
            img = pygame.image.fromstring(buffer.getvalue(), resolution, 'RGBA').convert()
        if img.get_at((10, 10))[:3] == (0, 0, 0):
            #FIXME: Bug of picam. Sometimes image is black, try to takz it again
            img = self.take_photo(resolution)
        self.flash_off()
        return img

    def flash_on(self):
        if self.conf.flash_enabled():
            GPIO.output(7, GPIO.LOW)

    def flash_off(self):
        GPIO.output(7, GPIO.HIGH)
