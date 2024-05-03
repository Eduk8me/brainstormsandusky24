#!/bin/bash

gam='/home/sysadmin/bin/gam/gam'
email="${1}"

${gam} info user ${email} |grep Suspended
${gam} update user ${email} suspended on

/usr/bin/mysql --defaults-extra-file=~/.readonly.cnf kcs -sse "update users set status='inactive' where emailaddress=\"${emailaddress}\""

