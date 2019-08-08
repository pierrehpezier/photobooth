#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
#upgrade system
apt-get update
apt-get install -y gunicorn3 redis-server libcups2-dev apache2 php libapache2-mod-php python-cups cups git vim pypy3 pypy3-dev libsdl1.2-dev libsdl-mixer1.2-dev libsdl-image1.2-dev libsdl-ttf2.0-dev libportmidi-dev python3-dev
apt-get remove -y python3-pygame python3-pil
apt autoremove -y
sudo -u pi wget https://bootstrap.pypa.io/get-pip.py
sudo -u pi pypy3 get-pip.py --user
sudo -u pi python3 get-pip.py --user
rm -f get-pip.py
chown root.gpio /dev/gpiomem
chmod g+rw /dev/gpiomem
#install software
cd /home/pi/
sudo -u pi git clone --depth=1 https://github.com/pierrehpezier/photobooth
sudo -u pi pypy3 -m pip incordova.plugin.http.setHeader('www.example.com', 'Header', 'Value');stall -r photobooth/src/requirements.txt --user
sudo -u pi python3 -m pip install -r photobooth/src/requirements.txt --user
sudo -u pi pypy3 -m pip install -r photobooth/server/requirements.txt --user
sudo -u pi python3 -m pip install -r photobooth/server/requirements.txt --user
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
grep gpu_mem /boot/config.txt >/dev/null
if [ $? -ne 0 ]
then
  echo gpu_mem=128>> /boot/config.txt
else
  sed -i -e 's/^gpu_mem=64/gpu_mem=128/' /boot/config.txt
fi

#start photomaton at reboot
cat << EOF > /lib/systemd/system/photobooth.service
[Service]
Type=simple
ExecStart=/home/pi/photobooth/src/photomaton
User=pi
Restart=on-failure
TimeoutStopSec=3
SuccessExitStatus=0

[Install]
WantedBy=multi-user.target
EOF

cat << EOF > /lib/systemd/system/redis.service
[Service]
Type=simple
ExecStart=/usr/bin/redis-server
User=pi
Restart=on-failure
TimeoutStopSec=3
SuccessExitStatus=0

[Install]
WantedBy=multi-user.target
EOF

cat << EOF > /lib/systemd/system/adminserver.service
[Service]
Type=simple
ExecStart=gunicorn3 server --certfile /home/pi/photobooth/pki/issued/cert.pem --keyfile /home/pi/photobooth/pki/issued/key.pem  --bind 0.0.0.0:8000 --pythonpath /home/pi/photobooth/server/
User=pi
Restart=on-failure
TimeoutStopSec=3
SuccessExitStatus=0

[Install]
WantedBy=multi-user.target
EOF

systemctl enable photobooth
systemctl enable redis
systemctl enable adminserver
#enable printer
adduser pi lpadmin
systemctl enable cups
systemctl start cups
echo 'Install the printer!! see http://localhost:631/'
