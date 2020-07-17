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

cd /home/pi/Documents/QRscan && sudo aws s3 cp "logs_"$cpu s3://reportes-lectora/logs_$cpu --recursive
