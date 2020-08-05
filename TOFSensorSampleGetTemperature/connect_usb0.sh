#!/bin/bash -x
sudo modprobe usbserial vendor=0x0590 product=0x00ca
sudo chmod o+wr /dev/ttyUSB0
#sudo chmod o+wr /dev/ttyUSB1
#sudo chmod o+wr /dev/ttyUSB2
#sudo chmod o+wr /dev/ttyUSB3
#ls -l /dev/ttyUSB0
