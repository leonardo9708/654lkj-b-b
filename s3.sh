#!/bin/bash
pattern='^Serial.*([[:xdigit:]]{16})$'
while read -r line
do
    if [[ $line =~ $pattern ]]
    then
        cpu="${BASH_REMATCH[1]}"
    fi
done < /proc/cpuinfo

echo $cpu
path="/home/pi/Documents/QRscan/logs_"$cpu
mkdir -p "$path"

var=$(date +'%d-%m-%Y' --date="1 days ago")
echo $var

sudo aws s3 cp "/home/pi/Documents/QRscan/logs_"$cpu"/barcodes_"$cpu"_"$var"_"$cpu".csv" s3://reportes-lectora/logs_$cpu/barcodes_$var.csv
sudo rm "/home/pi/Documents/QRscan/logs_"$cpu"/barcodes_"$cpu"_"$var"_"$cpu".csv"
