#!/bin/bash

gam=/home/sysadmin/bin/gamadv-xtd3/gam
in=${1}
ou=${2}

echo "Moving ${in} to ${ou}"

if [ -f "${in}" ]; then
    while read id; do
        cros_sn=$(cat chromebooks.csv | grep ",${id}"'$' | cut -d "," -f 1)
        echo "Moving ${id} to ${ou}..."
        ${gam} update cros ${cros_sn} ou ${ou}
    done < ${in}
else
    id=${in}
    cros_sn=$(cat chromebooks.csv | grep ",${id}"'$' | cut -d "," -f 1)
    echo "Moving ${id} to ${ou}..."
    ${gam} update cros ${cros_sn} ou ${ou}
fi
