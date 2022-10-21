#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import pygame
from core import main
from conf.conf import conf

def run():
    pygame.init()
    _conf = conf()
    main.Photobooth(_conf)

if __name__ == "__main__":
    run()
