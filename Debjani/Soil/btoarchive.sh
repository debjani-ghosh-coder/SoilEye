#!/bin/bash

file_path="/home/pi/Documents/Debjani/Soil/Soil_Type.txt"

image_path="/home/pi/Documents/Debjani/Soil/Sample.jpg"

destination_directory="/home/pi/Documents/Debjani/Soil/Archive/"

date_time=$(date +"%Y-%m-%d_%H-%M-%S")

mv "$file_path" "${destination_directory}${date_time}_Soil_Type.txt"

mv "$image_path" "${destination_directory}${date_time}_Sample.jpg"
