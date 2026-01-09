#!/bin/bash
#!/usr/bin/python3
export PYTHONPATH=$PYTHONPATH:/home/pi/.local/lib/python3.9/site-packages
python3 /home/pi/Documents/Debjani/CropFertilizerPrediction/CropPrediction.py /home/pi/Documents/Debjani/testing.csv > outputofcrop.log 2>&1
