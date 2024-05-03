#!/bin/bash

gam=/home/sysadmin/bin/gam/gam

cd /home/sysadmin/Development/chromebooks

${gam} print cros fields deviceID,serialNumber,annotatedassetid > chromebooks.csv

dos2unix chromebooks.csv
