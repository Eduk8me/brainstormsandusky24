#!/bin/bash

username=${1}


while read username; do
    mysql -e "update users set status='inactive' where emailaddress = \"${username}\""

    gam update user ${username} suspended on
done < d.txt

