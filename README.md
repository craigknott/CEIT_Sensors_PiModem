CEIT_Sensors_PiModem
================

CEIT sensor network, modem codes:
This repository contains the files required for the raspberry pi to communicate with panStamp sensors and publish the data to a MQTT server. 

Install
=======
Install dependencies.
 1. sudo apt-get install python-pip
 2. sudo pip install redis pyserial mosquitto
 3. git clone https://github.com/craigknott/CEIT_Sensors_PiModem
 4. cd CEIT_Sensors_PiModem/pyswap/
 5. sudo python setup.py install

Setup cronjob to restart wifi on disconnect
 1. sudo crontab -e
 2. add the following lines, replacing /path/to with the path to your CEIT_Sensors_PiModem clone.
 3. '* * * * * /path/to/CEIT_Sensors_PiModem/wifi_persist.sh'
 4. '0 * * * * /path/to/CEIT_Sensors_PiModem/gitpull.sh'
 5. save and exit
 6. make sure wifi_persist.sh has execute priveledge.

Setup daemontools to automatically monitor and reboot script on shutdown.
 1. sudo apt-get install daemontools daemontools-run
 2. sudo mkdir /etc/service/ /etc/service/lib /etc/service/lib/log
 3. make a file called run in /etc/service/lib/ and give it execute priveleges (chmod +x /etc/service/lib/run)
 4. repeat 3 in the /etc/service/lib/log/ folder.
 5. write the following to /etc/service/lib/run, replacing 401 with the PIs ID number.
    #!/bin/bash
    exec python /path/to/CEIT_Sensors_PiModem/swapmanager.py 401
 6. write the following to /etc/service/lib/log/run
    #!/bin/bash
    exec 2>&1
    exec multilog t /var/log/lib_log

Run
===
THATS IT YOU'RE DONE!
Unless you chose not to use daemontools in which case run as below.
 1. sudo python swapmanager.py XXX [where XXX is the ID of the RPi you are using, first number is the floor of the building]
