#!/bin/bash

echo "Update all of the Google Groups on "$(date +"%Y-%m-%d_%T")

gam='/home/sysadmin/bin/gam/gam'

cd /home/sysadmin/Development/useradmin

declare -A groups
#-)
groups=( ["all-group"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'student' AND type != 'gone' ORDER BY emailaddress" \
	["classified"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'student' AND type != 'gone' AND category='Classified' ORDER BY emailaddress" \
	["certified"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'student' AND type != 'gone' AND category='Certified' ORDER BY emailaddress" \
	["es-classified"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'student' AND type != 'gone' AND building LIKE '%Elementary School%' AND category='Classified' ORDER BY emailaddress" \
	["es-certified"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'student' AND type != 'gone' AND building LIKE '%Elementary School%' AND category='Certified' ORDER BY emailaddress" \
	["ms-classified"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'student' AND type != 'gone' AND building LIKE '%Middle School%' AND category='Classified' ORDER BY emailaddress" \
	["ms-certified"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'student' AND type != 'gone' AND building LIKE '%Middle School%' AND category='Certified' ORDER BY emailaddress" \
	["hs-classified"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'student' AND type != 'gone' AND building LIKE '%High School%' AND category='Classified' ORDER BY emailaddress" \
	["hs-certified"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'student' AND type != 'gone' AND building LIKE '%High School%' AND category='Certified' ORDER BY emailaddress" \
    ["everyone"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'gone' and emailaddress LIKE '%@school.org' ORDER BY emailaddress" \
    ["families"]="SELECT parentemail FROM parentemails" \
    ["es-families"]="select parentemail from users,parentemails where users.uid=parentemails.studentid and type='student' and status='active' and building='Elementary School'" \
    ["ms-families"]="select parentemail from users,parentemails where users.uid=parentemails.studentid and type='student' and status='active' and building='Middle School'" \
    ["hs-families"]="select parentemail from users,parentemails where users.uid=parentemails.studentid and type='student' and status='active' and building='High School'" \
    ["students"]="SELECT emailaddress FROM users WHERE status='Active' AND type='student' ORDER BY emailaddress" \
    ["hs-students"]="SELECT emailaddress FROM users WHERE status='Active' AND type='student' AND building='High School' ORDER BY emailaddress" \
    ["ms-students"]="SELECT emailaddress FROM users WHERE status='Active' AND type='student' AND building='Middle School' ORDER BY emailaddress" \
    ["es-students"]="SELECT emailaddress FROM users WHERE status='Active' AND type='student' AND building='Elementary School' ORDER BY emailaddress" \
	["2024-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '24%' ORDER BY emailaddress" \
	["2025-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '25%' ORDER BY emailaddress" \
	["2026-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '26%' ORDER BY emailaddress" \
	["2027-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '27%' ORDER BY emailaddress" \
	["2028-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '28%' ORDER BY emailaddress" \
	["2029-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '29%' ORDER BY emailaddress" \
	["2030-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '30%' ORDER BY emailaddress" \
	["2031-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '31%' ORDER BY emailaddress" \
	["2032-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '32%' ORDER BY emailaddress" \
	["2033-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '33%' ORDER BY emailaddress" \
	["2034-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '34%' ORDER BY emailaddress" \
	["2035-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '35%' ORDER BY emailaddress" \
	["2036-group"]="SELECT emailaddress FROM users WHERE status='Active' AND username LIKE '36%' ORDER BY emailaddress" \
	["esall"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'gone' AND building LIKE '%Elementary School%' ORDER BY emailaddress" \
	["msall"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'gone' AND building LIKE '%Middle School%' ORDER BY emailaddress" \
	["hsall"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'gone' AND building LIKE '%High School%' ORDER BY emailaddress" \
	["es-group"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'student' AND type != 'gone' AND building LIKE '%Elementary School%' ORDER BY emailaddress" \
	["ms-group"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'student' AND type != 'gone' AND building LIKE '%Middle School%' ORDER BY emailaddress" \
	["hs-group"]="SELECT emailaddress FROM users WHERE status='Active' AND type != 'student' AND type != 'gone' AND building LIKE '%High School%' ORDER BY emailaddress" \
)

for key in ${!groups[@]}; do

    GROUP="${key}"

    echo "Processing ${GROUP}..."
    /usr/bin/mysql kcs -B -e "${groups[${key}]}" | tail -n +2> /tmp/${GROUP}

    # Check and see if there are additional people to add to a group
    if [ -f "other/${GROUP}" ]; then
        echo "Additional members found to add to ${GROUP}:"
        cat "other/${GROUP}" | tee -a /tmp/${GROUP}
    fi

    case ${GROUP} in
		everyone)
            cat ohpstudents >> /tmp/${GROUP} ;;
        students|hs-students)
            cat ohpstudents >> /tmp/${GROUP} ;;
        hsall)
            cat ohpstudents >> /tmp/${GROUP} ;;
    esac
    ${gam} update group ${GROUP}@school.org sync member file /tmp/${GROUP}

done

# Sync Family Groups
for class in {2024..2036}
do
    grade=${class: -2}
    group="${class}-families"
    echo "Processing ${group} (${grade})..."

    /usr/bin/mysql kcs -B -e "select parentemail from users,parentemails where users.uid=parentemails.studentid and type='student' and status='active' and username LIKE \"${grade}%\"" > /tmp/${group}

    echo "tech-dept@school.org" >> /tmp/${group}
    ${gam} update group ${group}@school.org sync member file /tmp/${group}
done
