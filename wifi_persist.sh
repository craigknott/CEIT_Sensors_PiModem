#!/bin/bash

wlan=`ifconfig wlan0 | grep inet\ addr | wc -l`
if [ $wlan -eq 0 ]; then
sudo ifdown wlan0 && sudo ifup wlan0
else
echo interface is up
fi
