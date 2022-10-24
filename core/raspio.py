import logging
import pathlib
from pydoc import resolve
import time
import threading
from typing import Optional, List, Tuple
import pygame
import cups
import io
import cups
import RPi.GPIO as GPIO
import picamera
import rfeed
import datetime

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


class IoError(Exception):
    pass


class Io:
    def __init__(self):
        LOG.debug("Loading IO components")
        self.feeds: List[rfeed.Item] = []
        try:
            self.cups_conn = cups.Connection()
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(GPIO_PORT, GPIO.OUT, initial=GPIO.HIGH)
            self.cups = cups.Connection()
            self.camera = picamera.PiCamera()
            pygame.joystick.Joystick(0).init()
            LOG.debug(f"Found {pygame.joystick.get_count()} joysticks")
            self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            if len(self.cups_conn.getPrinters()) != 1:
                raise TypeError()
            self.printername = self.cups_conn.getPrinters()[0]
            LOG.debug(f'Found printer "{self.printername}"')
            self.cups_conn.enablePrinter(self.printername)
            self.cups_conn.cancelAllJobs(self.printername)
        except Exception as error:
            raise IoError(str(error))


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

    def _wait_for_processing_jobs(self):
        while any(
            self.cups_conn.getJobAttributes(job_id)["job-state"] == cups.IPP_JOB_PROCESSING
            for job_id in list(self.cups_conn.getJobs())
        ):
            time.sleep(1)

    def print(self, file_path: pathlib.Path) -> None:
        self.boot_screen(self.get_text("printing"))

        if self.cups_conn.getPrinterAttributes(self.printername)["printer-state"] not in (cups.IPP_PRINTER_PROCESSING,
                                                                                          cups.IPP_PRINTER_IDLE,
                                                                                          cups.IPP_PRINTER_BUSY):
            reasons = "".join(f"{x}," for x in 
                              self.cups_conn.getPrinterAttributes(self.printername)["printer-state-reasons"]
                             ).rstrip(",")
            self.alert(f'{self.get_text("printer_problem")}: {reasons}')

        self._wait_for_processing_jobs()
        for job in [self.cups_conn.getJobAttributes(job_id) for job_id in list(self.cups_conn.getJobs())]:
            if job["job-state"] not in (cups.IPP_JOB_PROCESSING, cups.IPP_JOB_PENDING):
                self.cups_conn.cancelJob(job["job-id"])
        
        '''
        while jobs := list():
            for job_id in jobs:
                job = self.cups_conn.getJobAttributes(job_id)
                if job["job-state"] != cups.IPP_JOB_PROCESSING:

                if job["job-state"] != cups.IPP_JOB_PROCESSING:
                    msg = f'{job["job-state"]} {job["job-state-reasons"]}'
                    self.alert(msg)
'''
        self.cups_conn.printFile(printer=self.printername,
                                 filename=str(file_path),
                                 title='IMG',
                                 options={'StpBorderless': 'True'})
        self.alert("")
        LOG.error("Print not implemented")

    @staticmethod
    def flash_off() -> None:
        GPIO.output(7, GPIO.HIGH)

    def save_image(self, surface: pygame.Surface) -> Tuple[pathlib.Path, str]:
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
        return file_path.resolve(), url

    def alert_rss(self, msg: str, level: str="ERROR") -> None:
        self.feeds.append(rfeed.Item(
            title = level,
            link="mlkmlklmk",
            description = msg,
            author = self.conf.get_text("photobooth"),
            guid = rfeed.Guid(str(self.feeds)),
            pubDate = datetime.datetime.now())
        )
        rss = rfeed.Feed(
            title = self.conf.get_text("Photomaton"),
            link = f"https://{self.conf.get_ip()}/.rss",
            description = self.conf.get_text("Photomaton"),
            lastBuildDate = datetime.datetime.now(),
            items = self.feeds)
        try:
            self.conf.get_rss_path().write_text(rss.rss())
        except PermissionError:
            LOG.error(f'Cannot open "{self.conf.get_rss_path()}"')

if __name__ == "__main__":
	import coloredlogs
	coloredlogs.install(level=logging.DEBUG)
	pygame.init()
	myio = Io()
	myio.take_photo(flash=False)
