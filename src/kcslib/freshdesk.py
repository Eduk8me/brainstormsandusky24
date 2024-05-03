#!/usr/bin/python3

from freshdesk.api import API
import configparser

config = configparser.ConfigParser()
config.read('/home/sysadmin/.freshdesk')
apikey = config.get('default','apikey')

a = API('COMPANY.freshdesk.com',apikey)

agents = {
        'agent1'      : "9999999",
        }

groups= {
        'group1'  : "99999999999",
         }

categories = ['AV','Hardware','Repair','Software','Staff Development','Research',
              'Order','Useradmin','sysadmin','PrintJob','PR','PrintJob']


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)



def create_ticket(subject,requester,description,tags,group,category,t,agent,cc=[]):
    tags.append("automation")
    group_id=groups[group]
    agent_id=agents[agent]

    ticket = a.tickets.create_ticket(subject,
            email=requester,
            cc_emails=cc,
            description=description,
            tags=tags,
            group_id=int(group_id),
            custom_fields={'category': category},
            type=t.capitalize(),
            responder_id=int(agent_id)
            )

    return ticket

def list_tickets(view):

    tickets = a.tickets.list_tickets()



