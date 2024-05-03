#!/bin/bash

user="${1}"
gam="/home/sysadmin/bin/gamadv-xtd3/gam"

if [ -z ${user} ]; then
    echo "I need a username!"
    exit
fi

pw=$(bw generate --passphrase --words 3 --separator - --capitalize --includeNumber)
echo "Changing the password for ${user} to ${pw}..."

${gam} update user "${user}" password "${pw} changepassword on"

echo "Done!"

