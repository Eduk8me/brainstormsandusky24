#!/bin/bash

gam=/home/sysadmin/bin/gam/gam

while read line; do
    sn=$(echo "${line}" | cut -d "," -f 1)
    id=$(echo "${line}" | cut -d "," -f 2)

    cros_sn=$(cat chromebooks.csv | grep ${sn} | cut -d "," -f 1)

    echo "Working on ${id}..."

    ${gam} update cros ${cros_sn} AssetId ${id}
done < "${1}"
