#!/usr/bin/env python3
# -*- CODING: UTF-8 -*-
import logging
import coloredlogs

from core import display
from core import raspio


LOG = logging.getLogger(__name__)



class Photobooth(display.Display, raspio.Io):
    continue_execution: bool = True

    def __init__(self, conf):
        super().__init__(conf)
        self.mainloop()
	
    def mainloop(self):
        """
        Handle main loop
        """
        self.display_welcome_screen()

        while input := self.get_joy_input():
            print(input)
            pass

        LOG.info("exitting")


if __name__ == '__main__':
    LOG.info('Demarrage du photomaton')
    coloredlogs.install(level=logging.INFO)
    Photobooth()
