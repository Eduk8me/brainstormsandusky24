# A list of database management functions

# install mysqlclient to get this module
import MySQLdb as mdb
from datetime import datetime
import configparser
import pandas as pd

# Connection to MySQL
config = configparser.ConfigParser()
config.read('/home/sysadmin/onetoone.cfg')

dbhost = config.get('mysql','host')
dbuser = config.get('mysql','user')
dbpass = config.get('mysql','pass')
db = config.get('mysql','db')

db = mdb.connect(dbhost,dbuser,dbpass,db, local_infile=1)
db.autocommit(True)
cursor = db.cursor(mdb.cursors.DictCursor)

# Calculate schoolyear
schoolyear = datetime.now().year + (datetime.now().month >= 7)

def get_device_user(deviceid):
    try:
        did = str(deviceid)
    except:
        print(f"Problem with device {deviceid}")
        uid = 0
    q = "SELECT uid FROM chromebooks WHERE asset = %s"
    p = (did,)
    try:
        cursor.execute(q,p)
    except:
        #print(cursor._last_executed)
        print("No go... " + q)
        #print(cursor._check_executed)
    
    numrows = cursor.rowcount

    if numrows > 0:
        row = cursor.fetchone()
        uid = row['uid']
    else:
        print(f"No device found, must be KES student or a loaner")
        kesdevices = pd.read_csv('/home/sysadmin/Development/sheetsdb/sheetsdb/kes-inventory.csv')
        finduid = kesdevices[kesdevices['Laptop Asset #'] == int(deviceid)]['Student ID']
        if finduid.empty:
            uid=1000
        else:
            uid=finduid.iloc[0]

    return uid

def get_student_info(studentid):
    
    try:
        uid = str(studentid)
    except:
        print("Problem with ID")
        uid=0
    #print(uid)
    # get username so we can calculate grade
    q = "SELECT username,firstname,lastname,building,status,emailaddress FROM users WHERE uid = %s"
    p = (uid,)

    try:
        cursor.execute(q,p)
    except:
        #print(cursor._last_executed)
        print("No go... " + q)
        print(cursor._check_executed)
        exit()

    row = cursor.fetchone()
    try:
        #print(row)
        u = row['username']
    except:
        #print(f"Student {uid} not found")
        u = "30nousername"

    #print(studentid)
    if u[:2] == 'ps':
        g = "PS"
    elif str(studentid) == "1000":
        g = 13
    else:
        try:
            g = (schoolyear + 12) - int("20" + u[:2])
        except:
            g = 13

    try:
        student_info = {
        'uid': uid,
        'username': row["username"],
        'firstname': row["firstname"],
        'lastname': row["lastname"],
        'building': row["building"],
        'status': row["status"],
        'emailaddress': row["emailaddress"],
        'grade': str(g)
        }
    except:
        student_info = {
        'uid': 0,
        'username': "nousername",
        'firstname': "nofirstname",
        'lastname': "nolastname",
        'status': "nostatus",
        'emailaddress': "tech@school.org",
        'grade': "nograde"
        }

    return student_info

def get_user_info(userid):

    try:
        uid = str(userid)
    except:
        print("Problem with ID")
        uid=0
    q = "SELECT username,firstname,lastname,building,status,emailaddress FROM users WHERE uid = %s"
    p = (uid,)

    try:
        cursor.execute(q,p)
    except:
        #print(cursor._last_executed)
        print("No go... " + q)
        print(cursor._check_executed)
        exit()

    row = cursor.fetchone()
    try:
        #print(row)
        u = row['username']
    except:
        #print(f"Student {uid} not found")
        u = "NOTFOUND"

    try:
        user_info = {
        'uid': uid,
        'username': row["username"],
        'firstname': row["firstname"],
        'lastname': row["lastname"],
        'building': row["building"],
        'status': row["status"],
        'emailaddress': row["emailaddress"],
        }
    except:
        user_info = {
        'uid': 0,
        'username': "nousername",
        'firstname': "nofirstname",
        'lastname': "nolastname",
        'building': "nobuilding",
        'status': "nostatus",
        'emailaddress': "tech@school.org",
        }

    return user_info

def get_homeroom(studentid):
    uid = str(studentid)
    print(uid)
    #s = get_student_info(uid)
    q = "SELECT teacher_code,period,section,staffemail,staffname,class_name FROM studentschedule WHERE student_id = %s AND (class_name LIKE '%%ADVISORY%%' OR class_name LIKE '%%Activity%%' OR class_name LIKE '%%ADM%%' OR class_name LIKE '%%Preschool%%' OR class_name LIKE '%%301%%') ORDER BY class_name DESC"

    p = (uid,)
    try:
        cursor.execute(q,p)
    except:
        print("No go... " + q)
        print(cursor._executed)
        exit()

    row = cursor.fetchone()
    #print(row)
    return row

def getbuildings(uid):
    print(f"Working on {uid}")
    q = "SELECT building FROM users WHERE uid = %s"
    p = (uid,)

    try:
        cursor.execute(q,p)
    except:
        print("No go... " + q )
        print(cursor._executed)
        exit()

    row = cursor.fetchone()
    buildings = row['building'].split(",")
    return buildings

def updateuser(u,c):
    #print(f"Creating query for: {u} - {c}")
    q = "UPDATE users set "
    for k in c:
        q = q + f"{k}=\"{u[k]}\","

    # Remove comma
    q = q[:-1]
    q = q + f" WHERE uid=\"{u['uid']}\""
    #print(q)
    p = ()
    
    try:
        cursor.execute(q,p)
    except:
        print("No go... " + q )
        print(cursor._executed)
        exit()

    return

def createuserinfocsv(filename):
    q = """SELECT uid,firstname,lastname,emailaddress,building,role,title,category,
        phone,address1,city,state,zip
        FROM users 
        WHERE status=\"active\" AND type!=\"student\" AND role!=\"Coach\"
        ORDER BY lastname,firstname
        """
    p = ()
    try:
        cursor.execute(q,p)
    except:
        print("No go... " + q )
        print(cursor._executed)
        exit()

    result = cursor.fetchall()
    # Output to csv file
    o = open(filename, "w")
    for row in result:
        #print(row)
        row['es']="FALSE"
        row['ms']="FALSE"
        row['hs']="FALSE"

        b = row['building'].split(",")
        if "Elementary School" in b:
            row['es']="TRUE"
        if "Middle School" in b:
            row['ms']="TRUE"
        if "High School" in b:
            row['hs']="TRUE"

        out = f"\"{row['es']}{row['ms']}{row['hs']}{row['category']}{row['role']}{row['title']}{row['phone']}{row['address1']}{row['city']}{row['state']}{row['zip']}\","
        out = out + f"\"{row['uid']}\",\"{row['firstname']}\",\"{row['lastname']}\",\"{row['emailaddress']}\","
        out = out + f"\"{row['es']}\",\"{row['ms']}\",\"{row['hs']}\","
        out = out + f"\"{row['category']}\",\"{row['role']}\",\"{row['title']}\","
        out = out + f"\"{row['phone']}\",\"{row['address1']}\",\"{row['city']}\","
        out = out + f"\"{row['state']}\",\"{row['zip']}\""
        out = out +"\n"
        
        o.write(out)

    o.close()
    return

def term():
    term="2SEM"
    today=datetime.today().strftime('%Y-%m-%d')
    q = f"SELECT end FROM cal WHERE id='2'"
    p = ()

    try:
        cursor.execute(q,p)
    except:
        print("No go... " + q )
        print(cursor._executed)
        exit()

    row = cursor.fetchone()
    if today<=row["end"]:
        term="1SEM"
    return term

def nineweeks():
    today=datetime.today().strftime('%Y-%m-%d')
    q = f"SELECT id FROM cal WHERE start<='{today}' AND end>='{today}'"
    q = f"SELECT id FROM cal WHERE end>='{today}'"
    p = ()

    try:
        cursor.execute(q,p)
    except:
        print("No go... " + q )
        print(cursor._executed)
        exit()

    row = cursor.fetchone()
    id = row["id"]
    r = f"{id}-9W"
    return r
