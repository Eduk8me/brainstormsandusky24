#!/bin/bash

uid=${1}
dest=${2}

if [ -z ${uid} ]; then
    echo "Pass the user id as the first parameter. If you want to email it to someone, pass their email as the second parameter:"
    echo "./printloginsheet.sh 7000XXXX or ./printloginsheet.sh 7000XXXX SOMEONE@school.org"
    exit
fi

from="tech@school.org"
kola=$(mysql -sNe "SELECT class_name FROM studentschedule WHERE student_id=${uid} AND class_name LIKE '%KOLA%' LIMIT 1")
if [ ! -z "${kola}" ]; then
    echo "KOLA student, emailing sheet to Amy"
    dest="hs-guidance@school.org"
fi

kms=$(mysql -sNe "SELECT building FROM users WHERE uid=${uid} AND building='Middle School'")
if [ ! -z "${kms}" ]; then
    echo "KMS student, emailing sheet to Robin M."
    dest="ms-secretary@school.org"
fi


khs=$(mysql -sNe "SELECT building FROM users WHERE uid=${uid} AND building='High School'")
if [ ! -z "${khs}" ]; then
    echo "KHS student, emailing sheet to Nathalie and/or Amy."
    if [ -z "${dest}" ]; then
        dest="hs-tech@school.org"
    else
        dest="${dest},hs-tech@school.org"
    fi
fi
#u=${2}
#p=${3}

student=$(mysql -sNe "SELECT username,password,firstname,lastname FROM users WHERE uid=${uid}")
u=$(echo "${student}" | cut -f 1)
p=$(echo "${student}" | cut -f 2)
f=$(echo "${student}" | cut -f 3)
l=$(echo "${student}" | cut -f 4)

echo "Creating sheet for ${u} (${uid})"
convert -units PixelsPerInch -density 300 2023-08-29-loginsheet.pdf \
	-font JetBrainsMono-Regular.ttf \
    -pointsize 12 \
    -draw "fill black text 760,790 \"${u}@school.org\"" \
    -draw "fill black text 760,920 \"${p}\"" \
	out.pdf

echo "Printing sheet for ${u} (${uid})"
lp -d NW-Stage out.pdf

if [ ! -z "${dest}" ]; then
    echo "Mailing new user sheet form for ${u} ${l} (${uid}) to ${dest}"
    mv out.pdf "${u}.pdf"
    sendEmail -f ${from} -t ${dest} \
        -u "New user information for ${f} ${l}" \
        -m "Attached is the new user sheet for ${f} ${l} (${uid})" \
        -o tls=no \
        -a "${u}.pdf"
    rm "${u}.pdf"
fi




