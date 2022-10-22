import logging
import pathlib
from pydoc import resolve
import time
import threading
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
        LOG.debug("Loading IO components")
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(GPIO_PORT, GPIO.OUT, initial=GPIO.HIGH)
        self.cups = cups.Connection()
        self.camera = picamera.PiCamera()
        pygame.joystick.Joystick(0).init()
        LOG.debug(f"Found {pygame.joystick.get_count()} joysticks")
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

    @staticmethod
    def get_joy_input() -> Optional[pygame.event.Event]:
        pygame.event.clear()
        while True:
            for event in pygame.event.get():
                LOG.debug(str(event))
                if event.type == pygame.JOYBUTTONDOWN:
                    LOG.debug("Joystick pressed")
                    return event.button
                if event.type == pygame.JOYDEVICEADDED:
                    LOG.debug("Joystick added")
                    joy = pygame.joystick.Joystick(event.device_index)

    def take_photo(self, preview=False, flash: bool=True) -> pygame.Surface:
        if flash:
            self.flash_on()
        with io.BytesIO() as buffer:
            if preview:
                """
                stick to the hardware specs
                https://uk.pi-supply.com/products/raspberry-pi-camera-board-v1-3-5mp-1080p?logged_in_customer_id=&lang=fr
                """
                self.camera.resolution = (640, 480)
                self.camera.capture(buffer, format='rgba', use_video_port=True)
                self.camera.framerate = 60
                img = pygame.image.fromstring(buffer.getvalue(), (640, 480), "RGBA").convert()
            else:
                self.camera.resolution = (2592, 1944)
                self.camera.framerate = 30
                self.camera.capture(buffer, format='rgba', use_video_port=False)
				# black magic: wrong string length
                img = pygame.image.fromstring(buffer.getvalue(), (2592, 1952), "RGBA").convert()
        #if img.get_at((10, 10))[:3] == (0, 0, 0):
        #    #FIXME: Bug of picam. Sometimes image is black, try to takz it again
        #    del img
        #    img = self.take_photo(preview, flash)
        if flash:
            self.flash_off()
        return img

    def flash_on(self):
        if self.conf.flash_enabled():
            GPIO.output(7, GPIO.LOW)

    def print(self) -> None:
        LOG.error("Print not implemented")

    @staticmethod
    def flash_off() -> None:
        GPIO.output(7, GPIO.HIGH)

    def save_image(self, surface: pygame.Surface) -> pathlib.Path:
        file_name = '{}.jpg'.format(time.strftime('%H-%M-%S-%d%m%Y'))
        file_path = self.conf.get_storage_path() / file_name
        url = self.conf.get_webserver_url().rstrip("/") + "/" + file_name
		# Copy file in background as it can take some time
        def _save_img(_surface, _file_path):
            LOG.info(f'Saving image to: "{_file_path}"')
            t1 = time.time()
            pygame.image.save(_surface, _file_path)
            LOG.info(f"Saved in {time.time() - t1} seconds")
        threading.Thread(target=_save_img, args=[surface, str(file_path.resolve())]).start()
        return url

if __name__ == "__main__":
	import coloredlogs
	coloredlogs.install(level=logging.DEBUG)
	pygame.init()
	myio = Io()
	myio.take_photo(flash=False)
