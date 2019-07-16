#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
'''
Generate a preview from the template photo
'''
import os
import time
import pygame
import render


CURRDIR = os.path.abspath(os.path.dirname(__file__))
os.environ['DISPLAY'] = ':0.0'

pygame.init()
pygame.display.set_mode((800, 600))
TIME1 = time.time()
ASSEMBLER = render.Assemble([pygame.image.load(os.path.join(CURRDIR, 'images', 'Template.jpeg'))]*6)
print(ASSEMBLER.filename(), 'généré en', time.time() - TIME1, 'secondes')
