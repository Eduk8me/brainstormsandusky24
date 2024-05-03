#!/usr/bin/python3

from subprocess import Popen, PIPE, call
import configparser,sys,crypt,random,os,shlex
import MySQLdb as mdb
import time
import datetime

sys.path.append('/home/sysadmin/Development/')
from kcslib.dbfunctions import *

# ct stores current time
ct = datetime.now()
print("Update Class Google Groups:", ct)

domain = "school.org"
gampy = "/home/sysadmin/bin/gam/gam"

currentterm=term()
current9weeks=nineweeks()

def gam(args):
    global gampy
    cmd = shlex.split(gampy + " " + args)
    stdout,stderr = Popen(cmd,stdout=PIPE).communicate()
    return stdout.splitlines()

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

# Create temporary table

q = f"create temporary table IF NOT EXISTS ccgg AS (select distinct Term,teacher_code,staffemail,`Class Period`,Section from `studentschedulefull` WHERE Term='YEAR' OR Term='{currentterm}' OR Term='{current9weeks}' ORDER BY teacher_code,`Class Period`,Section)"
p = ()
print(q)
try:
    cur.execute(q,p)
except:
    print(cur._last_executed)
    exit()

# Get list of every class group to make
q = "SELECT teacher_code,staffemail,`Class Period`,Section FROM ccgg"
p = ()
try:
    cur.execute(q,p)
except:
    print(cur._last_executed)
    exit()

groups = cur.fetchall()
for group in groups:
    tmp = open("/tmp/gg.txt","w")
    tc = group['teacher_code']
    staffemail = group['staffemail']
    period = group['Class Period']
    section = group['Section']

    q = f"select studentemail from studentschedulefull where teacher_code = %s and `Class Period` = %s AND Section= %s AND (Term = '{currentterm}' or Term = 'Year' or Term = '{current9weeks}')"
    print(q)
    p = (tc,period,section)
    try:
        cur.execute(q,p)
    except:
        print(cur._last_executed)
        exit()

    students = cur.fetchall()
    for student in students:
        tmp.write(student['studentemail'] + "\n")

    tmp.close()

    classgroup=tc + "-" + period + "-" + section + "@school.org"

    cmd = "update group " + classgroup + " sync member file /tmp/gg.txt"
    out = gam(cmd)
    time.sleep(1)

# Close access to database
m.close()
