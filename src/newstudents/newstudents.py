#!/usr/bin/python3

from subprocess import Popen, PIPE, call
import subprocess
import configparser,sys,crypt,random,os,shlex,re,csv

#KCS Python Libraries
sys.path.append('/home/sysadmin/Development/')
from kcslib.sendemail import sendemail
from kcslib.dbfunctions import *
from kcslib.freshdesk import *

## install mysqlclient to get this module
import MySQLdb as mdb

# Email Setup
server      = "mailserver@school.org"
sender      = 'tech-dept@school.org'
esreceivers = []
hsreceivers = ['hs-tech@school.org']
msreceivers = []

# Constants

categories = { 'e': 'certified', 'l': 'classified', 's': 'subs', 'n': 'none'}
buildings = { 'KBCE' : 'Elementary School',
              'KBMS' : 'Middle School',
              'KBHS' : 'High School'}
ous = { 'KBCE' : 'EL',
        'KBMS' : 'MS',
        'KBHS' : 'HS'}

# Calculate schoolyear
schoolyear = datetime.now().year + (datetime.now().month >= 7)
print(f"Schoolyear: {schoolyear}")

domain = "school.org"
gampy = "/home/sysadmin/bin/gamadv-xtd3/gam"

new = 0
reactivated = 0
deactivated = 0
tags = []

# Functions

def createpw():

    # Open the file and read the lines
    with open('words.txt', 'r') as file:
        words = file.read().splitlines()
    
    # In case our magical tome is lacking
    if len(words) < 2:
        return "The spellbook is too thin. More words, please!"
    
    # Select two noble words at random
    word1, word2 = random.sample(words, 2)
    
    # Enchant one with a number, randomly chosen
    number = random.randint(0, 9)
    if random.choice([True, False]):
        word1 += str(number)
    else:
        word2 += str(number)
    
    # Elevate them to their rightful status
    word1, word2 = word1.capitalize(), word2.capitalize()
    
    # Bind them with the hyphen of destiny
    password = f"{word1}-{word2}"
    
    return password

def gam(args):
    global gampy
    print ("gam " + args)
    cmd = shlex.split(gampy + " " + args)
    stdout,stderr = Popen(cmd,stdout=PIPE).communicate()
    return stdout.splitlines()

def status(uid):
    q = "SELECT uid,status FROM users WHERE uid = %s"
    p = (uid,)

    try:
        cur.execute(q,p)
    except:
        print(cur._last_executed)
        exit()

    if cur.rowcount == 0:
        status = 'new'
    else:
        row = cur.fetchone()
        status = row["status"]

    return status


def pw(uid):
    q = "SELECT uid,password FROM users WHERE uid = %s"
    p = (uid,)

    try:
        cur.execute(q,p)
    except:
        print(cur._last_executed)
        exit()

    row = cur.fetchone()
    password = row["password"]

    return password

def username(uid):
    q = "SELECT uid,username FROM users WHERE uid = %s"
    p = (uid,)

    try:
        cur.execute(q,p)
    except:
        print(cur._last_executed)
        exit()

    row = cur.fetchone()
    user = row["username"]

    return user

def find_device_id(search_value):
    with open('/home/sysadmin/Development/chromebooks/chromebooks.csv', newline='') as csvfile:
        search_value_str = str(search_value).strip()  # Convert to string and strip spaces
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            # print(f"Checking row: {row}")  # Debug print
            if row[2] == search_value_str:
                return row[0]  # Return the first field
    return None  # Return None if no match is found

def kes_device_info(studentid):
    with open('/home/sysadmin/Development/sheetsdb/out/kes-inventory.csv', newline='') as csvfile:
        sid=str(studentid).strip()
        reader = csv.DictReader(csvfile)
        for row in reader:
            #print(row)
            if row['Student ID'] == sid:
                kesinfo = {
                    'asset': row['Laptop Asset #'],
                    'room': row['Room'],
                    'email': emailaddress(row['teacher_code'])
                    }
                return kesinfo
    return None

def emailaddress(teacher_code):
    q = "SELECT emailaddress FROM users WHERE teacher_code = %s"
    p = (teacher_code,)

    try:
        cur.execute(q,p)
    except:
        print(cur._last_executed)
        exit()

    row = cur.fetchone()

    email = row["emailaddress"]

    return email

def newstudent(s):
    global new
    student_id  = s["student_id"]
    grade       = s["grade"]
    first_name  = re.sub(r'[^a-zA-Z]','',s["first_name"])
    last_name   = re.sub(r'[^a-zA-Z]','',s["last_name"])
    b           = buildings[s["building_code"]]
    fullname    = last_name + ", " + first_name

    if grade == "KG":
        grade = "0"

    if grade != 'PS':
        grade = int(grade)
        gradyear = schoolyear+12-int(grade)
        username = str(gradyear)[2:4]
    else:
        grade = -1
        gradyear = "PS"
        username = "ps-" 

    username+= last_name[0:4].lower()
    username+= first_name.lower()

    email = username + "@school.org"
    ##print(grade)
    if grade > 6:
        password = createpw()
    elif grade >=0 and grade <=6:
        password = "cats" + str(student_id)[-5:]
    else:
        password = "cats20"

    print("Creating " + username + " with a password of " + password + "...")
    
    if grade > 6:
        print("Need laptop for " + fullname + " \(" + str(student_id) + "\), " + username)

    q = "INSERT INTO users (uid,username,firstname,lastname,fullname,emailaddress,password,type,building) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    p = (student_id,username,first_name,last_name,fullname,email,password,"student",b)
    try:
        cur.execute(q,p)
        ##print(q,p)
    except:
        print("An error occurred when saving the record to MySQL")
        print(cur._last_executed)
        exit()

    print("Creating Google account for " + first_name + "...")
    out = gam("create user " + email + " firstname " + first_name + " lastname " + last_name + " password " + password + "changepassword on")
    print("update user " + email + " ou /Students/" + ous[s["building_code"]] +"/" + str(gradyear))
    out = gam("update user " + email + " ou /Students/" + ous[s["building_code"]] +"/" + str(gradyear)+ "changepassword on")

    new+=1
    
def reactivate(s):
    global reactivated
    print(s)

    student_id  = s["student_id"]
    grade       = s["grade"]
    first_name  = s["first_name"]
    last_name   = s["last_name"]
    b           = buildings[s["building_code"]]
    fullname    = last_name + ", " + first_name

    if grade == "KG":
        grade = "0"

    if grade !='KG' and grade != 'PS':
        q = "SELECT username,password FROM users WHERE uid = %s"
        p = (student_id,)
        try:
            cur.execute(q,p)

        except:
            print(cur._last_executed)
            exit()

        row = cur.fetchone()
        username = row["username"]
        password = row["password"]

        gradyear = schoolyear+12-int(grade)
        email = username + "@school.org"
        vusername = str(gradyear)[2:4]
        vusername+= re.sub(r'[^a-zA-Z]','',last_name[0:4].lower()) 
        vusername+= re.sub(r'[^a-zA-Z]','',first_name.lower())

        #print(f"{username} {vusername} {grade} {gradyear} {schoolyear}")

        if (int(grade) > 6 and password[-5:] == str(student_id)[-5:]) or (password == str(student_id)):
            print("Changing password from " + password)
            password = createpw()

        if vusername == username:
            print("Re-activating " + username + " with a password of " + password)
            out = gam("update user " + email + " username " + username + " password " + password + " ou /Students/" + ous[s["building_code"]] +"/" + str(gradyear) + " suspended off changepassword on")
            email = username + "@school.org"
        else:
            print("Student was held back...")
            out = gam("update user " + email + " username " + vusername + " password " + password + " ou /Students/" + ous[s["building_code"]] +"/" + str(gradyear) + " suspended off changepassword on")
            username = vusername
            email = username + "@school.org"

        if int(grade) > 6:
            print("Need laptop for " + fullname + " (" + str(student_id) + "), " + username)

        q = "UPDATE users SET status = %s, username = %s, password = %s, emailaddress = %s, building = %s WHERE uid = %s"
        p = ("Active",username,password,email,b,student_id)

        try:
            cur.execute(q,p)
            #print(q,p)

        except:
            print("An error occurred when saving the record to MySQL")
            print(cur._last_executed)
            exit()
        print("update user " + email + " ou Students/" + ous[s["building_code"]] +"/" + str(gradyear) + " suspended off changepassword on")
        out = gam("update user " + email + " ou Students/" + ous[s["building_code"]] +"/" + str(gradyear) + " suspended off changepassword on")
        
        reactivated+= 1

def procoreemail(g,name,sid):

    to = "ccurriculum@school.org"
    subject = "New student, " + name + " (" + str(sid) + ") in grade " + str(g) 
    text = "\nTerm, School, Class Name, Class ID, Class Period, Teacher Code\n" 

    # Get schedule
    q = "SELECT Term,School,`Class Name`,`Class ID`,`Class Period`,teacher_code FROM studentschedulefull WHERE `Student ID` = %s"
    p = (sid,)
    cur.execute(q,p)
    result = cur.fetchall()

    for row in result:
        text = text + row["Term"]+", "+row["School"]+", "+row["Class Name"]+", "+row["Class ID"]+", "+row["Class Period"]+", "+row["teacher_code"]+"\n"
        
    
    text = text + "\n\nThanks!"

    message = """\
    FROM: %s
    TO: %s
    SUBJECT: %s

    %s
    """ % (sender, ", ".join(to),subject,text)
    
    process = subprocess.Popen(['/home/sysadmin/bin/gam/gam',args],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    #process = subprocess.Popen(['ls','-al'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout,stderr = process.communicate()
    #cmd = shlex.split("sendEmail -f " + sender + " -t " + to + " -u \"" + subject + "\"  -m \"" + text + "\"")
    #stdout,stderr = Popen(cmd,stdout=PIPE).communicate()
    # print text

def cafeemail(g,name,sid):

    sender = "tech-dept@school.org"
    to = "cafeteria@school.org"
    subject = "New student, " + name + " (" + str(sid) + ") in grade " + str(g) 
    text = "Subject: " + subject + "\n\nTerm, School, Class Name, Class ID, Class Period, Teacher Code\n" 

    # Get schedule
    q = "SELECT Term,School,`Class Name`,`Class ID`,`Class Period`,teacher_code FROM studentschedulefull WHERE `Student ID` = %s"
    p = (sid,)
    cur.execute(q,p)
    result = cur.fetchall()

    for row in result:
        text = text + row["Term"]+", "+row["School"]+", "+row["Class Name"]+", "+row["Class ID"]+", "+row["Class Period"]+", "+row["teacher_code"]+"\n"
        
    
    text = text + "\n\nThanks!"

    email = smtplib.SMTP(server)
    email.sendmail(sender,to,text)
    email.quit()

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

# Main Loop

#q = "SELECT uid AS student_id, '8' AS grade, firstname AS first_name, lastname AS last_name, 'KBHS' AS building_code FROM users WHERE uid='700060738'"
q = "SELECT student_id, grade, first_name, last_name, building_code FROM newstudents"
cur.execute(q,)
numrows = cur.rowcount

if numrows == 0:
    print("No new students.")
else:
    result = cur.fetchall()

    for row in result:
        student_id  = row["student_id"]
        tags.clear()
        tags.append("newstudent")
        if row["grade"] == "PS":
            grade=-1
        elif row["grade"] == "KG":
            grade=0
        else:
            grade       = int(row["grade"])

        first_name  = row["first_name"]
        last_name   = row["last_name"]
        b           = row["building_code"]
        assignto = "#john"
        agent = "deanj"
        appendsubject = ""

        if grade >= 9:
            to = hsreceivers.copy()
            sender = "hs-secretary@school.org"
        elif grade >= 7:
            to = msreceivers.copy()
            sender = "ms-tech@school.org"
        else:
            to = esreceivers.copy()
            #print(f"esreceivers: {esreceivers}-{to}")
            r = get_homeroom(student_id)
            #to.append(r['staffemail'])
            if r is None:
                r = {
                "staffemail": "tech-dept@school.org",
                'staffname': "Ryan Collins",
                }
            
            sender = r['staffemail']
            appendsubject = " in room " + r['staffname']
            assignto = "#carrie"
            agent = "dilleyc"

        #print(f"To dictionary: {to}")

        if status(student_id) == "new":
            print("New student " + first_name + " " + last_name + "...")
            newstudent(row)
        elif status(student_id) == "inactive":
            print("Re-activating " + first_name + " " + last_name + "...")
            reactivate(row)
        else:
            print("There is a problem with " + first_name + " " + last_name + "...")
       
        s=get_student_info(student_id)
        if grade >=0:        
            gradyear = schoolyear + 12 - grade
            tags.append(str(gradyear))
            tags.append(str(student_id))

            subject = f"New student, {first_name} {last_name}, needs a laptop ({gradyear}-{student_id}) {appendsubject}" 
            msg = f"""

            {first_name} {last_name} is a new student and will need a laptop.

            Thanks!!

            """

            ### Create ticket
            t = create_ticket(subject,sender,msg,tags,b,"Hardware","Request",agent,to)

            # Send to Cafeteria
            receiver=["cafeteria@school.org"]
            subject = f"New " + str(row["grade"]) + f" student {first_name} {last_name} ({gradyear}-{student_id})" 
            msg = f"""

            Thanks!!
            """  
            sendemail(sender,receiver,subject,msg)

        if b=="KBMS" or b == "KBHS":
            subprocess.run(["./printloginsheet.sh", str(student_id)])

## Deactivate students
q = "SELECT student_id,first_name,last_name,username FROM leftstudents"
cur.execute(q,)

if cur.rowcount == 0:
    print("No withdrawals.")
else:
    result = cur.fetchall()

    for row in result:
        tags.clear()
        tags.append("leftstudent")
        student_id  = row["student_id"]
        username    = row["username"]
        first_name  = row["first_name"]
        last_name   = row["last_name"]
        if row["username"][:2] == "ps":
            g = -1
        else:
            g = (schoolyear + 12) - int("20" + username[:2])

        if g >=7:
            q = "SELECT asset FROM chromebooks WHERE uid = %s"
            p = (student_id,)
            cur.execute(q,p)

            r = cur.fetchone()
            try:
                asset = r["asset"]
            except:
                asset = "none assigned"

        else:
            kes_info = kes_device_info(student_id)
            try:
                asset = kes_info['asset']
            except:
                asset = "none assigned"

        device_id = find_device_id(asset)
        if device_id:
            print(f"Disabling device ID for {asset}: {device_id}")
            out = gam("update cros " + device_id + " action disable")
        else:
            print(f"No match found for {asset}")

        print("De-activating " + username + " with a laptop of " + str(asset) + "...")
        print("Collect laptop " + str(asset) + " from " + username + " (" + str(student_id) + ")")

        subject = "Retrieve laptop " + str(asset) + " from " + first_name + " " + last_name + "(" + str(student_id) + ")" 
        agent = "deanj"
        assignto = "#john"
        
        if g >= 9:
            to = hsreceivers.copy()
            sender = "hs-secretary@school.org"
            b = 'khs'
        elif g >= 7:
            to = msreceivers.copy()
            sender = "ms-tech@school.org"
            b = 'kms'
        else:
            to = esreceivers.copy()
            try:
                sender = kes_info['email']
            except:
                sender = "tech-dept@school.org"
            b = 'kes'
            try:
                to.append(kes_info['email'])
                room = kes_info['room']
            except:
                room = ""
            tags.append(room)
            tags.append(str(student_id))
            tags.append(str(asset))

            subject = subject + " in room " + room
            assignto = "#tech"
            agent = "tech"


        msg = f"""

        {first_name} {last_name} has withdrawn and their laptop needs to be collected.

    Thanks!

    """
        if g >= 0:
            ### Create ticket
            t = create_ticket(subject,sender,msg,tags,b,"Hardware","Request",agent,to)

        ##sendemail(sender,to,subject,msg)

        # Notification for Robin
        subject=f"Withdrawn student {first_name} {last_name}  (" + str(student_id) + ") - Grade " +str(g)
        body="Withdrawn student."
        receiver = ['datamgr@school.org']
        ##sendemail(sender,receiver,subject,msg)

        out = gam("update user " + username + "@school.org suspended on")

        q = "UPDATE users SET status = %s WHERE uid = %s"
        p = ("inactive",student_id)
        cur.execute(q,p)
        #print(q,p)

        deactivated+=1

print("Created " + str(new) + " students, reactivated " + str(reactivated) + " students, and deactivated " + str(deactivated) + ".")

cur.close()
