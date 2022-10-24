#!/usr/bin/env python3
# -*- CODING: UTF-8 -*-
import threading
import pygame
import time
import logging
from typing import List
from core import display
from core import raspio


LOG = logging.getLogger(__name__)



class Photobooth(raspio.Io, display.Display):
    continue_execution: bool = True

    def __init__(self, conf):
        self.conf = conf
        last_error = ""
        while True:
            try:
                display.Display.__init__(self)
                raspio.Io.__init__(self)
                break
            except (display.DisplayError, raspio.IoError) as error:
                if str(error) != last_error:
                    last_error = str(error)
                    self.alert(last_error)
                time.sleep(10)
        LOG.debug("init done. Initiating mainloop")
        while True:
            self.mainloop()


    def mainloop(self):
        """
        Handle main loop
        """
        self.display_welcome_screen()

        # Wait for user input
        while self.get_joy_input() not in  (raspio.JOYBUTTONA, raspio.JOYBUTTONB):
            pass
        # Retrieve the list of pictures
        currthreadnb = threading.active_count()
        for index in range(1, 7):
            self.render_single_img(self._take_photo(text=f'{self.conf.get_text("photo")} {index} sur 6'), index)

        t1 = time.time()
        self.boot_screen(text=self.conf.get_text("processing"))
        while threading.active_count() > currthreadnb:
            time.sleep(.1)
        LOG.debug(f"Processed in {time.time() - t1} seconds")
        image_path, url = self.save_image(self.get_photo())
        self.display_finished_photo(url)
        while user_input := self.get_joy_input() not in  (raspio.JOYBUTTONA, raspio.JOYBUTTONB):
            pass
        if user_input == raspio.JOYBUTTONB:
            self.print(image_path)
        # End of mainloop

    def _take_photo(self, text) -> pygame.Surface:
        t1 = time.time()
        self.screen.fill((0, 0, 0))
        last_sec = 5
        thread = None
        while (elapsed := int(time.time() - t1)) < 5:
            preview = self.take_photo(preview=True, flash=False)
            self.load_image(preview, x=self.width/2 - preview.get_width()/2, y=self.height/2 - preview.get_height()/2)
            self.showtext(text, height=100, x=100, y=10)
            self.showtext(str(5 - elapsed), width=100, x=self.width/2-50, y=150)
            pygame.display.flip()
        self.screen.fill((255, 255, 255))
        pygame.display.flip()
        photo = self.take_photo(preview=False, flash=True)
        self.load_image(photo, width=self.width, x=0, y=0)
        pygame.display.flip()
        time.sleep(3)
        return photo

    def alert(self, msg: str) -> None:
        self.alert_screen(msg)
        self.alert_rss(msg)
