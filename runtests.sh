#!/bin/bash
export SITE_ID="1"
export SECRET_KEY="10293802948abcabaacbacbacbabefeacbef"
if [ $# -ne 1 ]
then
    python manage.py test springboard courses profiles alerts lms_main
else
    python manage.py test $1
fi


