#############################Actualizar librerias
1- sudo apt-get update
2- sudo apt-get install libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev -y
3- wget www.kernel.org/pub/linux/bluetooth/bluez-5.50.tar.xz
4- tar xvf bluez-5.50.tar.xz && cd bluez-5.50
5- ./configure --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --enable-experimental 
6- make -j4
7- sudo make install
8- cd Documents/QRscan/
9- cp bluez-5.50/test/example-advertisement ./example_advertisement.py
10- cp bluez-5.50/test/example-gatt-server ./example_gatt_server.py
11- sudo pip3 install ipgetter2

#############################Archivos necesarios
1- sustituir todos los archivos por los nuevos dentro de D/Leo/Driveleo/QR-Local-BLE

#############################Cron Job
1-  0 3 * * * sudo reboot
2-  @reboot sleep 40 && cd /home/pi/Documents/QRscan && sudo bash s3.sh
3-  @reboot sleep 45 && cd /home/pi/Documents/QRscan && sudo bash on-ble.sh
4-  @reboot sleep 50 && cd /home/pi/Documents/QRscan && sudo /usr/bin/python3 data_iot.py
5-  @reboot sleep 80 && cd /home/pi/Documents/QRscan && sudo /usr/bin/python3 Lectora-QR-http-Local.py
6-  @reboot sleep 80 && cd /home/pi/Documents/QRscan && sudo /usr/bin/python3 Lectora-QR-http-Local-ble.py
7-  */5 * * * * cd /home/pi/Documents/QRscan && sudo /usr/bin/python3 report.py
8-  * /30 * * * cd /home/pi/Documents/QRscan && sudo bash police.sh


############################
sudo reboot





######################################################################
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
Solo pi viejas
cambiar archivo s3.sh
y
cd Documents/QRscan
sudo rm -r logs_*cpu_serial*/*
