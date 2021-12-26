#!/bin/bash
cd /home/pi/projects/google-remote

# pull new changes
git reset --hard HEAD
git checkout raspberrypi
git pull

# place service file in system
sudo cp google-remote.service /lib/systemd/system/google-remote.service

# do things with service for systemd
sudo systemctl daemon-reload
sudo systemctl enable google-remote

echo 'need to reboot to apply changes'
