from importlib.abc import Loader
import locale
import os
import yaml
import pathlib
import gettext

ROOT_DIR = pathlib.Path(__file__).parent.parent
USER_DIR = pathlib.Path(os.environ["HOME"], ".photobooth")


class ConfError(Exception):
    pass


class conf:
    def __init__(self):
        self.user_conf = USER_DIR / "conf.yml"
        if self.user_conf.is_file():
            self.yml = yaml.safe_load(self.user_conf.open())
        else:
            self.yml = yaml.safe_load((ROOT_DIR / "conf" / "default_conf.yml").open())
        traduction = gettext.translation('photobooth',
                                         localedir= ROOT_DIR / "data" / "locale")
                                         #languages=[locale.getlocale()[0].split("_")[0]])
        traduction.install()

    def set_lang(self, lang: str):
        self.yml["gui"]["lang"] = lang
        self.commit()

    def commit(self):
        USER_DIR.mkdir(exist_ok=True)
        self.user_conf.write_text(yaml.dump(self.yml))

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


if __name__ == "__main__":
    conf().set_lang("fr")
