import pygame
import threading
import logging
import qrcode
from typing import Union, Optional, Tuple, List

from conf.conf import conf

LOG = logging.getLogger(__name__)

class DisplayError(Exception):
    pass


class Display:
    screen = None
    def __init__(self):
        LOG.debug("Loading Display components")
        try:
            pygameinfo = pygame.display.Info()
            size = (pygameinfo.current_w, pygameinfo.current_h)
            ##Largeur de l'écran
            self.width = pygameinfo.current_w
            ##Hauteur de l'écran
            self.height = pygameinfo.current_h
            ##Surface pygame
            self.font = pygame.font.Font(self.conf.get_font(), int(self.width / 15))
            if not self.screen:
                self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
            self.boot_screen()
            pygame.mouse.set_visible(False)
            self.photo_canevas = self._init_img()
        except Exception as error:
            raise DisplayError(str(error))

    def __del__(self):
        pygame.quit()

    def load_image(self, img: Union[str, pygame.Surface], 
                    width: Optional[Union[float, int]] = None,
                    height: Optional[Union[float, int]] = None, 
                    x: Optional[Union[float, int]] = None,
                    y: Optional[Union[float, int]] = None) -> pygame.Surface:
        if isinstance(img, str):
            img = pygame.image.load(self.conf.get_image_path(img)).convert_alpha()
        if width is not None or height is not None:
            if width is None:
                width = (height * img.get_width()) / img.get_height()
            if height is None:
                height = (width * img.get_height()) / img.get_width()
            img = pygame.transform.smoothscale(img, (int(width), int(height)))
        if x is not None and y is not None:
            self.screen.blit(img, (x, y))
        return img

    def showtext(self, text: str,
                  width: Optional[Union[float, int]] = None,
                  height: Optional[Union[float, int]] = None, 
                  x: Optional[Union[float, int]] = None,
                  y: Optional[Union[float, int]] = None,
                  color: Tuple[int]=(255, 255, 255)) -> pygame.Surface:
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

    def _init_img(self) -> pygame.Surface:
        surface = pygame.surface.Surface((5700, 8500))
        # Set background
        surface.fill(tuple(self.conf.get_customisation("bg_color")))
        # Set footer
        footer = self.load_image(self.conf.get_customisation("footer"),
                                 width=surface.get_width() * 0.9)

        surface.blit(footer, (int((surface.get_width() * 0.1)/2),
                              int(surface.get_height() * 0.9 - footer.get_height()/2)))
        return surface

    def render_single_img(self, photo: pygame.Surface, index: int) -> None:
        width = self.photo_canevas.get_width()
        height = self.photo_canevas.get_height()
        photoxmarge = int((width * .1)/3)
        photowidth = int((width - photoxmarge * 3) / 2)
        # resize image
        photo = self.load_image(photo, width=photowidth)
        photoheight = photo.get_height()
        # Line 1
        yoffset = photoxmarge
        if index == 1:
            threading.Thread(target=self.photo_canevas.blit, args=[photo, (photoxmarge, yoffset)]).start()
        if index == 2:
            threading.Thread(target=self.photo_canevas.blit, args=[photo, (photoxmarge * 2 + photowidth, yoffset)]).start()

        # Line 2
        yoffset += photoheight + photoxmarge
        if index == 3:
            threading.Thread(target=self.photo_canevas.blit, args=[photo, (photoxmarge, yoffset)]).start()
        if index == 4:
            threading.Thread(target=self.photo_canevas.blit, args=[photo, (photoxmarge * 2 + photowidth, yoffset)]).start()

        # Line 3
        yoffset += photoheight + photoxmarge
        if index == 5:
            threading.Thread(target=self.photo_canevas.blit, args=[photo, (photoxmarge, yoffset)]).start()
        if index == 6:
            threading.Thread(target=self.photo_canevas.blit, args=[photo, (photoxmarge * 2 + photowidth, yoffset)]).start()

    def get_photo(self) -> pygame.Surface:
        return self.photo_canevas

    @staticmethod
    def gen_qr(url: str) -> pygame.Surface:
        myqr = qrcode.QRCode(version=2, border=1)
        myqr.add_data(url)
        myqr.make(fit=True)
        image = myqr.make_image().convert('RGB')
        return pygame.image.fromstring(image.tobytes(), image.size, image.mode)

    def display_finished_photo(self, url: str) -> None:
        self.screen.fill((0, 0, 0))
        xoffset = self.load_image(self.get_photo(), height=self.height, x=0, y=0).get_width()
        qrcode = self.gen_qr(url)
        qrcodemargin = self.screen.get_width() * 0.05
        self.showtext(f'{self.conf.get_text("wifi")}:{self.conf.get_customisation("hotspot")}',
                      width=self.screen.get_width() - 2 * qrcodemargin - xoffset,
                      x=xoffset + qrcodemargin,
                      y=0)
        yoffset = 70
        yoffset += self.load_image(qrcode, x=xoffset + qrcodemargin, y=yoffset,
                                  width=self.screen.get_width() - 2 * qrcodemargin - xoffset
                                 ).get_height() + 10
        yoffset += self.showtext(f'{self.conf.get_text("print")}   {self.conf.get_text("cancel")}',
                                 height=50,
                                 x=xoffset + qrcodemargin,
                                 y=yoffset).get_height() + 10
        yoffset += self.load_image("NES_choice.png",
                                   x=xoffset + qrcodemargin,
                                   y=yoffset,
                                   width=self.screen.get_width() - 2 * qrcodemargin - xoffset,
                                  ).get_height() + 10
        pygame.display.flip()

    def boot_msg_info(self, text: str, picture: str) -> None:
        self.screen.fill((0, 0, 0))
        self.showtext(text, x=100, y=10, height=100)
        self.load_image(picture,
                        width=self.width/2,
                        x = self.width / 4,
                        y = 110
                        )
        pygame.display.flip()

    def boot_screen(self, text: Optional[str] = None) -> None:
        if text:
            self.boot_msg_info(text=text, picture="rendering.png")
        else:
            self.boot_msg_info(text=self.conf.get_text("booting"), picture="rendering.png")

    def alert_screen(self, msg: str) -> None:
        self.boot_msg_info(text=msg, picture="Cz-Error.png")

if __name__ == "__main__":
    pygame.init()
    print(Display.gen_qr("lqskjdlqksjdkljsqd"))
