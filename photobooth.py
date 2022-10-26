#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import pygame
import coloredlogs
import os
import logging
from core import main
from conf.conf import conf

LOG = logging.getLogger(__name__)


def run():
    pygame.init()
    _conf = conf()
    main.Photobooth(_conf)

if __name__ == "__main__":
    coloredlogs.install(level=logging.DEBUG)
    os.environ['DISPLAY'] = ':0.0'
    try:
        run()
    except KeyboardInterrupt:
        LOG.info("User exit")
