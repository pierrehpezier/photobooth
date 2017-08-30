photomaton
==========

Testé sur:
 * Raspberry pi B
 * Picaméra v1.2
 * Ecran pour raspberry 10"
 * Imprimante Selphy cp910
 * Relais SODIAL(R) 5V MODULE 2 CANAUX POUR ARDUINO PIC ARM AVR DSP
 * NES Joypad

Des ajustement sur la résolution des images est à prévoir si le matériel est différent.

avec:
 * Raspbian GNU/Linux 8 (jessie)
 * LXDE
 * python2

Configuration:
==============

installer apache2 avec php

installer les modules python suivants:
 * picamera
 * pygame
 * qrcode
 * RPi

copier show-all-images-in-a-folder-with-php dans /var/www/html

ajouter la ligne suivante dans /.config/lxsession/LXDE-pi/autostart:
@/home/pi/photomaton/photomaton.py
@xset s noblank
@xset s off
@xset -dpms

TODO:
=====

Problème de retour imprimante. Aucune information sur l'alimentation papier et le niveau encre. Utiliser la dernière version de gutenprint.


