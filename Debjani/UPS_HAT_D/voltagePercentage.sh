#!/bin/bash

while true; do

	#cp test.txt percentages.txt
        #sudo python3 -i INA219.py > percentages.txt
	cat percentages.txt | tail -n 1 > latestPercentages.txt
        
done
