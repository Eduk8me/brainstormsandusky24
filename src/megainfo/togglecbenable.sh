#!/bin/bash

gam=/home/sysadmin/bin/gamadv-xtd3/gam
inventory="/home/sysadmin/Development/chromebooks/chromebooks.csv"

#read -p "Chromebook Asset #: " device
device=$(whiptail --inputbox "Chromebook Asset #:" 10 30 3>&1 1>&2 2>&3)

cros_sn=$(cat "${inventory}" | grep ",${device}"'$' | cut -d "," -f 1)

[ -z ${cros_sn} ] && { whiptail --msgbox "I can't find device ${device}!" 10 30; exit; } 

TERM=ansi whiptail --infobox "Getting status..." 10 30

status=$(${gam} info cros ${cros_sn} | grep "^  status: "| cut -d " " -f 4)

if [ ${status} = "ACTIVE" ]; then
    action="disable"
else
    action="reenable"
fi

whiptail --yesno "${device} is ${status}, ${action} it?" 10 30

if [ $? = 0 ]
then
    TERM=ansi whiptail --infobox "${action^} device ${device} (${cros_sn}...)" 10 30
    out=$(${gam} update cros ${cros_sn} action ${action})
    msg="${out}\n\nPress any key to return to the menu"
else
    msg="User abort"
fi

whiptail --msgbox "${msg}" 15 40

