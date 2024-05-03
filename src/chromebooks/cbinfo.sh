#!/bin/bash

gam="/home/sysadmin/bin/gamadv-xtd3/gam"

cbinfo() {
    #echo "Working on Chromebook ${line}:"
    deviceinfo=$(${gam} info cros ${deviceid} fields recentusers,activeTimeRanges)
    lastused=$(echo "${deviceinfo}" | grep date: | tail -n 1)
    lastuser=$(echo "${deviceinfo}" | grep email: | head -1)
    echo "${cbid},${lastused:10},${lastuser:13}"
}

if [ -f "${1}" ]; then
    while read -r cbid
    do
        deviceid=$(grep ${cbid} chromebooks.csv | cut -d "," -f 1)
        cbinfo
    done < ${1}
else
    cbid=${1}
    deviceid=$(grep ${cbid} chromebooks.csv | cut -d "," -f 1)
    cbinfo
fi
