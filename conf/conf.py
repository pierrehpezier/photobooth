import pathlib
import gettext

ROOT_DIR = pathlib.Path(__file__).parent.parent

class ConfError(Exception):
    pass


class conf:
    lang = "en"

    def __init__(self):
        traduction = gettext.translation('photobooth',
                                         localedir= ROOT_DIR / "data" / "locale",
                                         languages=[self.lang])
        traduction.install()

    def get_text(self, index: str):
        return _(index)

    @staticmethod
    def get_image_path(imgname: str) -> pathlib.Path:
        retval = ROOT_DIR / "data" / "img" / imgname
        if not retval.is_file():
            raise ConfError(f'File "{retval}" does not exists')
        return retval

    @staticmethod
    def get_font() -> pathlib.Path:
        return ROOT_DIR / "data" / "fonts" / 'Another day in Paradise.ttf'


    @staticmethod
    def flash_enabled() -> bool:
        return True
