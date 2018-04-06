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
 * NES Joypad retrolink
 * Un Relai Wi-Fi SMC barridade N

Des ajustement sur la résolution des images est à prévoir si le matériel est différent.

avec:
 * Raspbian GNU/Linux 8 (jessie)
 * LXDE
 * python2
 * gutenprint-5.2.12

Configuration:
==============

1 Installer les dépendances système
```
sudo apt-get update
sudo apt-get install -y apache2 php libapache2-mod-php python-pygame python-cups cups
```

2 Installer les dépendances python:

```
cd photobooth
pip install -r requirements.txt --user
```

3 Copier show-all-images-in-a-folder-with-php dans /var/www/html et autoriser le programme photomaton à écrire dedans:

```
cd
git clone https://github.com/mikelothar/show-all-images-in-a-folder-with-php.git
sudo cp -r show-all-images-in-a-folder-with-php/* /var/www/html/
sudo chown -R pi:pi /var/www/html/img
sudo rm -f /var/www/html/img/*
```

4 Configurer les services au démarrage

4.1 Lancement d'apache au démarrage

```
sudo systemctl enable apache2
sudo systemctl start apache2
```

4.2 Optionnel: SSH au démarrage (Attention à la sécurité)

```
sudo systemctl enable ssh
sudo systemctl start ssh
```

4.3 Configurer le photomaton au démarrage de la machine

```
cat << EOF >> ~/.config/lxsession/LXDE-pi/autostart
@/usr/bin/python2 /home/pi/photobooth/photomaton.py
@xset s noblank
@xset s off
@xset -dpms
EOF
```

4.4 Démarrage de cups

```
sudo systemctl enable cups
sudo systemctl start cups
sudo adduser pi lpadmin
```

5 Configurer le driver d'imprimante

voir les images dans doc/images

6 Configurer la caméra

```
sudo raspi-config
5 Interfacing Options -> P1 Camera -> enable
```
Changer la résolution si besoin avec la même commande
Allouer 128MB de mémoire vidéo

7 Montage automatique d'un disque

Brancher et formater le disque
identifier l'uuid de ce disque
```
blkid
```
Ajouter une ligne dans /etc/fstab (à adapter)
```
echo "UUID=1f1fa48b-1128-4931-a632-d351cd4a854a /var/www/img ext2 defaults 0 1" >> /etc/fstab
mount
sudo chown -R pi:pi /var/www/html/img
```

6 Conn

TODO:
=====

Problème de retour imprimante. Aucune information sur l'alimentation papier et le niveau encre. Utiliser la dernière version de gutenprint.
