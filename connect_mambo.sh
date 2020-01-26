#!/bin/bash

sudo rm pyparrot/images/*.png
sudo rm pyparrot/images/*.jpg

sudo dhclient -r wlan0
sudo ifdown wlan0
sudo ifup wlan0
sudo dhclient -v wlan0
iwgetid wlan0

echo '\n'