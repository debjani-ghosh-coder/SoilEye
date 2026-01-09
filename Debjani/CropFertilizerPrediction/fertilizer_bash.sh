#!/bin/bash
#!/usr/bin/python3
export PYTHONPATH=$PYTHONPATH:/home/ggpi/.local/lib/python3.9/site-packages

python3 /home/ggpi/Documents/Debjani/CropFertilizerPrediction/FertilizerPrediction.py /home/ggpi/Documents/Debjani/testing.csv > outputoffertilizer.log 2>&1
