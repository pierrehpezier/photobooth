#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
#upgrade system
apt-get update
apt-get install -y libcups2-dev apache2 php libapache2-mod-php python-cups cups git vim pypy3 pypy3-dev libsdl1.2-dev libsdl-mixer1.2-dev libsdl-image1.2-dev libsdl-ttf2.0-dev libportmidi-dev
apt-get remove -y python3-pygame python3-pil
apt autoremove -y
sudo -u pi wget https://bootstrap.pypa.io/get-pip.py
sudo -u pi pypy3 get-pip.py --user
rm -f get-pip.py
chown root.gpio /dev/gpiomem
chmod g+rw /dev/gpiomem
#install software
cd /home/pi/
sudo -u pi git clone --depth=1 https://github.com/pierrehpezier/photobooth
sudo -u pi pypy3 -m pip install -r photobooth/src/requirements.txt --user
git clone --depth=1 https://github.com/mikelothar/show-all-images-in-a-folder-with-php.git
cp -r show-all-images-in-a-folder-with-php/* /var/www/html/
chown -R www-data:www-data /var/www/html
chown -R pi:pi /var/www/html/img
rm -fr /var/www/html/img/* show-all-images-in-a-folder-with-php
systemctl enable apache2
systemctl start apache2
#update printer
sudo systemctl enable cups
sudo systemctl start cups
sudo adduser pi lpadmin
#enable picamera
grep start_x /boot/config.txt >/dev/null
if [ $? -ne 0 ]
then
  echo start_x=1 >> /boot/config.txt
else
  sed -i -e 's/^start_x=0/start_x=1/' /boot/config.txt
fi
#start photomaton at reboot
sudo -u pi mkdir -p /home/pi/.config/lxsession/LXDE-pi/
sudo -u pi cat << EOF >> /home/pi/.config/lxsession/LXDE-pi/autostart
@sudo chmod 777 /sys/class/gpio/gpio4/value
@/usr/bin/pypy3 /home/pi/photobooth/src/photomaton
@xset s noblank
@xset s off
@xset -dpms
EOF
chmod +x /home/pi/.config/lxsession/LXDE-pi/autostart
#enable printer
adduser pi lpadmin
systemctl enable cups
systemctl start cups
echo 'Install the printer!! see http://localhost:631/'
