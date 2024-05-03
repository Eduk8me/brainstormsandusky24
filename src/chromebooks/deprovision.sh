#!/bin/bash

gam="/home/sysadmin/bin/gamadv-xtd3/gam"

while read -r line
do
    echo "Working on Chromebook ${line}:"
    deviceid=$(grep ${line} chromebooks.csv | cut -d "," -f 1)
    ${gam} update cros ${deviceid} action deprovision_retiring_device acknowledge_device_touch_requirement
done < ${1}
