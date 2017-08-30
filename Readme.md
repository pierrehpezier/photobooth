Description
===========

Le photomaton utilisé pour mon mariage. Ce photomaton permet d'imprimer des photos dans une soirée pour environ 0.30€ la photo.

Une série de 6 photos sont prises et assemblées en une seule. L'utilisateur peut choisir d'imprimer ou non la photo. Elle est téléchargeable via un QRCode à tout moment via un point d'accès Wi-Fi ouvert par le photomaton.

voir:
  * doc/Guide de téléchagement.pdf
  * doc/Guide d'utilisation du photomaton.pdf

photomaton
==========

Testé sur:
 * Raspberry pi B
 * Picaméra v1.2
 * Ecran pour raspberry 10"
 * Imprimante Selphy cp910
 * Relais SODIAL(R) 5V MODULE 2 CANAUX POUR ARDUINO PIC ARM AVR DSP
 * NES Joypad
 * Un Relai Wi-Fi hors d'age

Des ajustement sur la résolution des images est à prévoir si le matériel est différent.

avec:
 * Raspbian GNU/Linux 8 (jessie)
 * LXDE
 * python2
 * gutenprint-5.2.12

Configuration:
==============

installer apache2 avec php

installer les modules python suivants:
 * picamera
 * pygame
 * qrcode
 * RPi

copier show-all-images-in-a-folder-with-php dans /var/www/html et autoriser le programme photomaton à écrire dedans.

ajouter la ligne suivante dans /.config/lxsession/LXDE-pi/autostart:
@/home/pi/photomaton/photomaton.py
@xset s noblank
@xset s off
@xset -dpms

TODO:
=====

Problème de retour imprimante. Aucune information sur l'alimentation papier et le niveau encre. Utiliser la dernière version de gutenprint.


