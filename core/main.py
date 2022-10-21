#!/usr/bin/env python3
# -*- CODING: UTF-8 -*-
import pygame
import time
import logging
import coloredlogs
from typing import List
from core import display
from core import raspio


LOG = logging.getLogger(__name__)



class Photobooth(raspio.Io, display.Display):
    continue_execution: bool = True

    def __init__(self, conf):
        self.conf = conf
        #super().__init__()
        raspio.Io.__init__(self)
        display.Display.__init__(self)
        print("init done")
        self.mainloop()


    def mainloop(self):
        """
        Handle main loop
        """
        self.display_welcome_screen()

        # Wait for user input
        while input := self.get_joy_input() not in  (raspio.JOYBUTTONA, raspio.JOYBUTTONB):
            pass
        # Retrieve the list of pictures
        img_list: List[pygame.Surface] = [self._take_photo(text=f'{self.conf.get_text("photo")} {i} sur 6') for i in range(1, 6 + 1)]


    def _take_photo(self, text) -> pygame.Surface:
        t1 = time.time()
        self.screen.fill((0, 0, 0))
        last_sec = 5
        while (elapsed := int(time.time() - t1)) < 5:
            preview = self.take_photo(resolution=(640, 480), flash=False)
            self.load_image(preview, x=self.width/2 - preview.get_width()/2, y=self.height/2 - preview.get_height()/2)
            self.showtext(text, x=100, y=100)
            self.showtext(str(5 - elapsed), x=100, y=300)
            pygame.display.flip()
        photo = self.take_photo()
        self.load_image(photo, width=self.width, x=0, y=0)
        pygame.display.flip()
        time.sleep(3)
        return photo


if __name__ == '__main__':
    LOG.info('Demarrage du photomaton')
    coloredlogs.install(level=logging.INFO)
    Photobooth()
