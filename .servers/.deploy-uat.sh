#!/bin/bash
USERNAME=mohara
HOSTS="web02-cl02-mde.flexiion-customer.net"
SCRIPT="cd medi;git pull origin development;docker exec -i medi_djangoapp_1 python manage.py migrate"
for HOSTNAME in ${HOSTS} ; do
    ssh -l ${USERNAME} ${HOSTNAME} "${SCRIPT}"
done
