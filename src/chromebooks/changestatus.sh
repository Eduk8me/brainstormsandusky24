#!/bin/bash

gam=/home/sysadmin/bin/gamadv-xtd3/gam
in=${1}
action=${2}

if [ ! -z ${action} ]; then
    if [ -f "${in}" ]; then
        while read id; do
            cros_sn=$(cat chromebooks.csv | grep ",${id}"'$' | cut -d "," -f 1)
            echo "${action^} ${id}..."
            ${gam} update cros ${cros_sn} action ${action}
        done < ${in}
    else
        id=${in}
        cros_sn=$(cat chromebooks.csv | grep ",${id}"'$' | cut -d "," -f 1)
        echo "${action^} ${id}..."
        ${gam} update cros ${cros_sn} action ${action}
    fi
else
    echo "./changestatus.sh FILE|ID reenable|disable"
fi
