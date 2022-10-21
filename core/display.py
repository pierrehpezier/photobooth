import os
import sys
import pygame
import logging
from typing import Union, Optional, Tuple

LOG = logging.getLogger(__name__)

class Display:
    def __init__(self):
        print('Display')
        os.environ['DISPLAY'] = ':0.0'
        pygameinfo = pygame.display.Info()
        size = (pygameinfo.current_w, pygameinfo.current_h)
        ##Largeur de l'écran
        self.width = pygameinfo.current_w
        ##Hauteur de l'écran
        self.height = pygameinfo.current_h
        ##Surface pygame
        self.font = pygame.font.Font(self.conf.get_font(), int(self.width / 15))
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        #self.screen = pygame.display.set_mode(size)
        pygame.mouse.set_visible(False)

    def __del__(self):
        pygame.quit()

    def load_image(self, img: Union[str, pygame.Surface], 
                    width: Optional[Union[float, int]] = None,
                    height: Optional[Union[float, int]] = None, 
                    x: Optional[Union[float, int]] = None,
                    y: Optional[Union[float, int]] = None) -> Optional[pygame.Surface]:
        if isinstance(img, str):
            img = pygame.image.load(self.conf.get_image_path(img)).convert_alpha()
        if width is not None or height is not None:
            if width is None:
                width = (height * img.get_width()) / img.get_height()
            if height is None:
                height = (width * img.get_height()) / img.get_width()
            img = pygame.transform.smoothscale(img, (int(width), int(height)))
        if x is None or y is None:
            return img
        self.screen.blit(img, (x, y))


    def showtext(self, text: str,
                  width: Optional[Union[float, int]] = None,
                  height: Optional[Union[float, int]] = None, 
                  x: Optional[Union[float, int]] = None,
                  y: Optional[Union[float, int]] = None,
                  color: Tuple[int]=(255, 255, 255)) -> Optional[pygame.Surface]:
        text = self.conf.get_text(text)
        img = self.font.render(text, 1, color)
        return self.load_image(img, width, height, x, y)


    def display_welcome_screen(self) -> None:
        """
		Display welcome screen to users
		"""
        self.load_image("menu_background.png", self.width, self.height, 0, 0)
        self.load_image("NES.png",
                         self.width/2, None, self.width/2 - (self.width/2)/2, self.height-self.height/3)
        self.showtext("press_A_B_choice", 
                       self.width/2, None, self.width/2 - (self.width/2)/2, self.height/4)
        pygame.display.flip()
