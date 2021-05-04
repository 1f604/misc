#!/bin/bash

# requires your current clock time to be not more than 2 weeks out of date
# originally named httpstime
# secure time setting via HTTPS
# by Hanno Böck
# crontab example config:
# * * * * * /opt/googletime/googletime.sh | tee -a /opt/googletime/log.txt /dev/tty1

HOST=www.google.com

DATESTRING=$(curl -sI "https://$HOST/" | grep -i "^date: ")

if [[ $? -ne 0 ]]; then
	echo -e "\n `date` googletime: Can't connect to $HOST. Is your system clock more than two weeks out of date?"
	echo "Please use date -s to manually set the system clock to the correct date." 
	exit 1
fi

DATESTRING="${DATESTRING/Date: /}"
DATESTRING="${DATESTRING/date: /}"

date -s "${DATESTRING}" > /dev/null

[[ $? -eq 0 ]] || echo "Time setting failed - maybe you are not root?"
