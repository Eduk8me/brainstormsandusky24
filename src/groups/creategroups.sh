#!/bin/bash

# Create a Google Group, or multiple groups, and set them up correctly
# Pass the filename of the .csv file to the script

PATH='/home/sysadmin/bin/gam':$PATH
groups=${1}

gam csv "${groups}" gam create group ~email
gam csv "${groups}" gam update group ~email add member nomail user tech-dept@school.org
gam csv "${groups}" gam update group ~email update manager user tech-dept@school.org
gam csv "${groups}" gam update group ~email who_can_invite NONE_CAN_INVITE
gam csv "${groups}" gam update group ~email who_can_join invited_can_join
gam csv "${groups}" gam update group ~email message_moderation_level moderate_all_messages
gam csv "${groups}" gam update group ~email who_can_post_message all_in_domain_can_post
gam csv "${groups}" gam update group ~email who_can_view_group  all_members_can_view
gam csv "${groups}" gam update group ~email who_can_view_membership all_managers_can_view
gam csv "${groups}" gam update group ~email send_message_deny_notification false
gam csv "${groups}" gam update group ~email allow_external_members true



