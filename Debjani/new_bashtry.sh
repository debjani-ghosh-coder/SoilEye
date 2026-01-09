#!/bin/bash

# Open serial port at 9600 baud rate
SERIAL_PORT="/dev/ttyUSB0"
BAUD_RATE="9600"
stty -F $SERIAL_PORT $BAUD_RATE

# Function to handle SIGTERM signal
function cleanup {
    echo "Cleaning up..."
    stty -F $SERIAL_PORT sane # Restore serial port settings
    exit 0
}

# Set signal handler for SIGTERM
trap cleanup SIGTERM

# Define the valid ranges for each of the 7 values
declare -a MIN_VALUES=(-40 0 0 0 0 0 0)
declare -a MAX_VALUES=(80 100 1999 1999 1999 14 5000)

# Read sensor data from serial
while true; do
    echo "I am inside while loop"
    NOW=$( date '+%F_%H:%M:%S' )
    echo "hello1"
    SENSOR_DATA=$(head -n 1 $SERIAL_PORT)
    echo "hello2"
    echo $SENSOR_DATA
    if [ -n "$SENSOR_DATA" ]; then # Only update the file if SENSOR_DATA is not empty
        # Split the values separated by a comma into an array
        IFS=',' read -ra values <<< "$SENSOR_DATA"

        # Check if all values are in their valid range
        valid_values=1
        for (( i=0; i<7; i++ )); do
            if ! [[ ${values[i]} =~ ^-?[0-9]+(\.[0-9]+)?$ ]]; then
            valid_values=0
            echo "Invalid input: ${values[i]} is not a number."
            break
            fi

            if (( $(echo "${values[i]} < ${MIN_VALUES[i]} || ${values[i]} > ${MAX_VALUES[i]}" | bc -l) )); then
                valid_values=0 # Set flag if value is not in valid range
                break
            fi
        done
        echo $valid_values

        # If all 7 values are valid, update the givingData.csv file
        if (( valid_values == 1 )); then
            echo "$NOW,$SENSOR_DATA" >> /home/pi/Documents/Debjani/givingData.csv
            echo "$SENSOR_DATA" > /home/pi/Documents/Debjani/testing.csv
        else
           echo "$NOW,$SENSOR_DATA" >> /home/pi/Documents/Debjani/soilSensorData.csv 
           continue # Skip to next iteration of loop if values are not valid
        fi

        # Append all received values to soilSensorData.csv
    fi
    sleep 1
done
