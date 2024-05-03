# General functions that I use a lot


from subprocess import Popen, PIPE, call
import subprocess
import configparser,sys,crypt,random,os,shlex,re,csv,requests,json,configparser
from pathlib import Path

from datetime import datetime,timedelta

schoolyear = datetime.now().year + (datetime.now().month >= 7)
gampy = "/home/sysadmin/bin/gamadv-xtd3/gam"

config = configparser.ConfigParser()
config.read('/home/sysadmin/.kcslib')
chatbot = config.get('default','boturl')

def calcgrade(gradyear):
    grade = (schoolyear + 12) - gradyear
    return grade

def calcgradyear(grade):
    gradyear = (schoolyear + 12) - grade
    return gradyear

def gam(args):
    cmd = shlex.split(gampy + " " + args)
    stdout,stderr = Popen(cmd,stdout=PIPE).communicate()
    return stdout.splitlines()

def run_command(*args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Oops, an error occurred: {e}"

def touch(filename):
    file_path = Path(filename)
    file_path.touch()

def fileage(filename,minutes=10):
    mod_time = os.path.getmtime(filename)
    last_modified_date = datetime.fromtimestamp(mod_time)

    current_time = datetime.now()
    # We ask: Is the last modified time further in the past than our threshold?
    if current_time - last_modified_date > timedelta(minutes=minutes):
        # It is indeed older
        return True
    else:
        # It remains within the bounds of our temporal threshold
        return False

def yellowalert(msg):
    message = {"text": msg}
    response = requests.post(chatbot, data=json.dumps(message), headers={'Content-Type': 'application/json'})

def countlines(file):
    with open(file, 'r') as file:
        line_count = sum(1 for line in file)
    return line_count

def progressbar(status):
    bar_length = 40  # Modify this to make the progress bar longer or shorter
    if isinstance(status, int):
        status = float(status)
    if not isinstance(status, float):
        status = 0
    if status < 0:
        status = 0
    if status >= 1:
        status = 1

    block = int(round(bar_length * status))
    text = "\rProgress: [{0}] {1}%".format("#" * block + "-" * (bar_length - block), int(status * 100))
    if int(status * 100) == 100:
        text+="\n"
    sys.stdout.write(text)
    sys.stdout.flush()
