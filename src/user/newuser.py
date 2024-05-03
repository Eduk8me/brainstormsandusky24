#!/usr/bin/python3

import subprocess
import configparser,sys,crypt,random,os,shlex
import MySQLdb as mdb

# Constants

categories = { 'e': 'certified', 'l': 'classified', 's': 'subs', 'n': 'none'}
buildings = { 'e' : 'Elementary School',
              'm' : 'Middle School',
              'h' : 'High School',
              'd' : 'District'}
bgs = { 'Elementary School'  : 'es',
        'Middle School'      : 'ms',
        'High School'        : 'hs'}
schoolyear = 2020
domain = "school.org"
gampy = "/home/sysadmin/bin/gam/gam"

# Functions

def createpw():
    words = [ "Able","Acre","Back","Bale","Barn","Care","Chew","Dots","Dish","Exam","Fame","SNES","Game","Hill","Jump","kite","Link","Made","Need","Oven","Pear","Quiz","Rice","Sofa","Talk","Vine","Walk","Yard","Zoom","Wool" ]

    pw = random.choice(words)
    pw+= "-"
    pw+= str(random.randint(0,9))
    pw+= str(random.randint(0,9))
    pw+= "-"
    pw+= random.choice(words)

    return pw

def gam(args):
    global gampy
    print ("Run gam " + args)
    os.system("/home/sysadmin/bin/gam/gam " + args)
    return



def sendwelcome(dept,user):
    if dept == "tech":
        os.system("sendEmail -f tech-dept@school.org -t " + user + "@school.org -u 'Welcome to KCS from the Technology Department' -o message-file=welcometech.html -o message-content-type=html  -o tls=no")
    elif dept == "treasurer":
        os.system("sendEmail -f treasurer@school.org -t " + user + "@school.org -u \"Welcome to KCS from the Treasurer's Department\" -o message-file=welcometreasurer.html -o message-content-type=html  -a welcometreasurer.pdf  -o tls=no")
    return

# Connection to MySQL

config = configparser.ConfigParser()
config.read('/home/sysadmin/onetoone.cfg')

dbhost = config.get('mysql','host')
dbuser = config.get('mysql','user')
dbpass = config.get('mysql','pass')
db = config.get('mysql','db')

m = mdb.connect(dbhost,dbuser,dbpass,db)
m.autocommit(True)
cur = m.cursor(mdb.cursors.DictCursor)

# Main loop

while True:
    firstname = input("First name: ")
    lastname = input("Last name: ")
    fullname = lastname + ", " + firstname
    gradyear = int(input("Grad year (enter 0 for staff): "))
    category = "student"
    dbtype = "student"
    if gradyear != 0:
        uid = input("Student ID: ")
        username = str(gradyear)[2:4] + lastname[0:4].lower() + firstname.lower()
        grade = 2032 - gradyear
        if grade >= 9:
            building = "High School"
        elif grade >= 7:
            building = "Middle School"
        else:
            building = "Elementary School"
            
    else:
        username = lastname.lower() + firstname[0:1].lower()
        username = lastname.lower() + "." + firstname.lower()
        uid = str(random.randint(1,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9))
        dbtype = "staff"
        
        while True:
            category = input("Certified/Classified/Sub/None (e/l/s/n): ")
            try:
                category = categories[category]
                break
            except:
                print ("Invalid category.")
        while True:
            building = input("ES/MS/HS/District (e/m/h/d): ")
            try:
                building = buildings[building]
                break
            except:
                print ("Invalid building.")

    password = createpw()

    print ("\nCreating the following user:")
    print ("Name:        " + fullname)
    print ("Username:    " + username)
    print ("UID:         " + uid)
    print ("Building:    " + building)
    print ("Username:    " + username)
    print ("Password:    " + password)
    if gradyear == 0:
        print ("Category:    " + category)

    create = input("Create user (y/n)? ")

    if create == "y":
        # Create user
        ## Insert into MySQL

        email = username + "@" + domain

        q = "SELECT username FROM users WHERE username = %s OR uid = %s"
        p = (username,uid)
        try:
            cur.execute(q,p)
        except:
            print(cur._check_executed)
            exit()

        if cur.rowcount !=0:
            print (username + " or " + uid + " already exists.")
            exit()

        print ("Adding to user db...")

        q = "INSERT INTO users (uid,username,firstname,lastname,fullname,emailaddress,password,type,building,category,role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        p = (uid,username,firstname,lastname,fullname,email,password,dbtype,building,"*","*")
        try:
            cur.execute(q,p)
        except:
            print ("An error occurred when saving the record to MySQL")
            print(cur._check_executed)
            exit()
        cur.close()

        ## Create Google Account
        print ("Creating Google account for " + firstname + "...")
        out = gam("create user " + username + "@" + domain + " firstname " + firstname + " lastname " + lastname + " password " + password + " changepassword on")

        ## Create Google Sub Account and email WOCO to create user account
        if category == "certified":
            print ("Creating Google Sub account...")
            subpw = createpw()
            out = gam("create user sub" + username + "@" + domain + " firstname Sub lastname " + username + " password " + subpw)
            print ("Sub account username: sub"+ username + "@" + domain)
            print ("Sub account password: " + subpw)

        ## Add staff to groups
        if gradyear == 0:
            out = gam("update user " + username + "@" + domain + " org /Staff")
            print (out)
            
            if category != 'none':
                # District category group
                print ("Adding " + firstname + " to " + category + "@" + domain)
                out = gam("update group " + category + "@" + domain + " add member user " + username + "@" +domain)
                print (out)

            if category != 'none':
                # Building category group
                print ("Adding " + firstname + " to " + bgs[building] + '-' + category + "@" + domain)
                out = gam("update group " + bgs[building] + '-' + category + "@" + domain + " add member user " + username + "@" +domain)
                print (out)

            # Classroom Teachers group
            print ("Adding " + firstname + " to classroom_teachers@" + domain)
            out = gam("update group classroom_teachers@" + domain + " add member user " + username + "@" +domain)
            print (out)

            # Building group
            if building != 'District':
                print ("Adding " +firstname + " to " + bgs[building] + "-group@" + domain)
                out = gam("update group " + bgs[building] + "-group@" + domain + " add member user " + username + "@" +domain)
                print (out)
            
            # District all group
            print ("Adding " + firstname + " to all-group@" + domain)
            out = gam("update group all-group@" + domain + " add member user " + username + "@" +domain)
            print (out)

        ## Send welcome email

        print ("Sending welcome emails to " + firstname + "...")
        out = sendwelcome("tech",username)

