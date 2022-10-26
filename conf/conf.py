from importlib.abc import Loader
from modulefinder import LOAD_CONST
from typing import Optional
import os
import yaml
import struct
import socket
import pathlib
import logging
import gettext

ROOT_DIR = pathlib.Path(__file__).parent.parent
USER_DIR = pathlib.Path(os.environ["HOME"], ".photobooth")

LOG = logging.getLogger(__name__)

class ConfError(Exception):
    pass


class conf:
    def __init__(self):
        try:
            self.yml = yaml.safe_load((USER_DIR / "conf.yml").open())
            LOG.debug("Using user path")
        except FileNotFoundError:
            self.yml = yaml.safe_load((ROOT_DIR / "conf" / "default_conf.yml").open())
            LOG.debug("Using default path")
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
        retval = USER_DIR / "data" / "img" / imgname
        if retval.is_file():
            return retval
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

    def get_customisation(self, name: str) -> Optional[str]:
        try:
            return self.yml["customisation"][name]
        except KeyError:
            return None

    @staticmethod
    def get_rss_path() -> pathlib.Path:
        return pathlib.Path("/var/www/html/.rss")

    @staticmethod
    def get_storage_path() -> pathlib.Path:
        path = pathlib.Path("/var/www/html/img")
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def _get_default_gateway_linux():
        '''!Read the default gateway directly from /proc
        @return L'adresse IP de la gateway
        '''
        with open('/proc/net/route') as routefile:
            for line in routefile:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue
                return socket.inet_ntoa(struct.pack('<L', int(fields[2], 16)))

    @staticmethod
    def get_ip():
        try:
            return [(s.connect((conf._get_default_gateway_linux(), 67)),
                     s.getsockname()[0], s.close())
                    for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        except:
            return '127.0.0.1'

    @staticmethod
    def get_webserver_url() -> str:
        return f"http://{conf.get_ip()}/img/"
