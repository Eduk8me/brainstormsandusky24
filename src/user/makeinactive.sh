#!/bin/bash

gam='/home/sysadmin/bin/gamadv-xtd3/gam'
in="${1}"
suspend="${2}"

[ -z "${in}" ] && { echo "Pass me a file with email addresses or an email as the first parameter. Add 'suspend' as the second parameter to also suspend the users"; exit; }

db_inactive() {
    echo "Making ${email} inactive in db..."
    /usr/bin/mysql --defaults-extra-file=~/.readonly.cnf kcs -sse "update users set status='inactive' where emailaddress='${email}'"
    if [ "${suspend}" = "suspend" ]; then
        echo "Suspending ${email}'s Google account...'"
        ${gam} update user ${email} suspended true
    fi
}

remove_from_groups() {
    echo "Removing ${email} from any groups..."
    allgroups=($(${gam} info user ${email} | grep -A5000 "Groups:" | tail -n +2 | cut -f2 -d ":"))
    for line in "${allgroups[@]}"; do
        group=$(echo "${line}" | cut -f2 -d ":")
        echo "Working on group ${group}"
        ${gam} update group ${group} remove member ${email}
    done
}

if [ -f "${in}" ]; then
    echo "Marking users from ${in} inactive..."
    while read email; do
        db_inactive
        remove_from_groups
    done < "${in}"
else
    email=${in}
    db_inactive
    remove_from_groups
fi

