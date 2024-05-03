#!/usr/bin/python3

import sys,os,csv,datetime


#KCS Python Libraries
sys.path.append('/home/sysadmin/Development/')
from kcslib.dbfunctions import *
from kcslib.sendemail import *
from kcslib.gen import *
from kcslib.xlsx2csv import Xlsx2csv
from kcslib.freshdesk import *

wd="/home/sysadmin/Development/tools/r2f"
savelastrun=f"{wd}/lastrun"
lock="/tmp/repairs2freshdesk.lock"

group= { 'Elementary School': "4000000441",
         'High School': "190941",
         'Middle School': "190942",
         'Northwood': "190984" }

category={'Category': 'Repair'}

tags = []

# Logging info
current_datetime = datetime.now()
today = current_datetime.strftime("%Y-%m-%d")
timestamp = current_datetime.strftime("%Y%m%d%H%M%S")

if not os.path.exists(wd):
        print(f"Creating directory: {wd}")
        os.makedirs(wd)

# Get last run
if os.path.exists(savelastrun):
    with open(savelastrun,'r') as file:
        lastrun = file.readline().strip()
else:
    lastrun = timestamp

print(f"Today is {today} ({timestamp} to be precise), the school year is {schoolyear}. Last run - {lastrun}")

# Get sheet from Google
out=run_command("/usr/bin/rclone","copyto","techdept:TechShared (GD)/Repairs/DeviceRepairForm.xlsx",f"{wd}/devicerepairform.xlsx")

# Convert updates sheet to csv
Xlsx2csv(f"{wd}/devicerepairform.xlsx",dateformat="%Y%m%d%H%M%S").convert(f"{wd}/devicerepairform.csv",sheetname="ToFreshdesk")


# Find new repairs
with open(f"{wd}/devicerepairform.csv", newline='') as csvfile:
    repairs = csv.DictReader(csvfile)
    for r in repairs:
        if r['Timestamp'] != "":
            print(f"{r['Timestamp']}")
        if r['Timestamp'] >= lastrun:
            print(f"{lastrun} - {r['Timestamp']}")
            tags.clear()
            device      = r['Device ID #:']
            formemail   = r['Email Address']
            description = r['What is the problem with the device?']
            happened   = r['Describe what happened:']

            tags.append(device)
            if r['TeacherCode'] == '#N/A':
                device_user = get_device_user(device)
                userinfo    = get_student_info(device_user)
                userinfo['gradyear'] = "20"+userinfo['username'][:2]
                agent = "hstech"
                tags.append(str(userinfo['gradyear']))
                tags.append(str(device_user))
            else:
                tc          = r['TeacherCode']
                q = "SELECT uid FROM users WHERE teacher_code = %s"
                p = (tc,)
                try:
                    cursor.execute(q,p)
                except:
                    print(f"Error with teacher code {tc}")

                row = cursor.fetchone()
                try:
                    device_user = row['uid']
                    userinfo    = get_user_info(device_user)
                    userinfo['building'] = "Elementary School"
                    userinfo['gradyear'] = ""
                except:
                    print(f"Error with getting email address for teacher code {tc}")
                student_uid = get_device_user(device)
                student = get_student_info(student_uid)
                agent = "dilleyc"

            if str(device_user) == "1000":
                userinfo['gradyear'] = "1987"
                userinfo['emailaddress'] = formemail
            print(f"Working on device {device} from {userinfo['firstname']} {userinfo['lastname']} ({userinfo['emailaddress']}) at {userinfo['building']} submitted at {r['Timestamp']}...")

            group_id=group[userinfo['building']]
            email=f"{userinfo['emailaddress']}"
            description=f"""
            <h3>User Info</H3>
            <p><b>User:</b> {userinfo['firstname']} {userinfo['lastname']}<br/>
            <b>UID:</b> {userinfo['uid']}<br/>
            """
            
            if userinfo['gradyear'] == "":
                description+=f"""
                <b>Student:</b> {student['firstname']} {student['lastname']}<br/>
                <b>Teacher:</b> {userinfo['lastname']}<br/>
                <b>Room:</b> {r['Homeroom']}<br/>
                """
                tags.append(r['Homeroom'])
            description+=f"<b>Submitter:</b> {formemail}"
            description+=f"""
            <h3>What is the problem with the device?</h3>
            <p>{r['What is the problem with the device?']}</p>
            <h3>What happened?</h3>
            <p>{r['Describe what happened:']}
            """

            #email="tech-dept@school.org"
            create_ticket(f"Repair Request for device {device}",email,description,tags,group_id,"Repair","Problem",agent)

# Save run time
with open(savelastrun,'w') as file:
    file.write(timestamp)

# Clean up
os.remove(lock)
