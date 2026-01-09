#!/bin/bash
bash /home/pi/Documents/Debjani/new_bashtry.sh &
sudo python3 /home/pi/Documents/Debjani/UPS_HAT_D/INA219.py & 

sleep 10

python3 /home/pi/Documents/Debjani/get_soil.py &

