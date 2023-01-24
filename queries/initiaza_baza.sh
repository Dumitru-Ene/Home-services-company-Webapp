#!/bin/bash

if [ $# -ne 2 ];then
echo "USAGE:$0 <mysql username> <mysql user password>"
exit
fi

mysql -u $1 -p"$2" < creaza_baza_proiect.sql
mysql -u $1 -p"$2" < populeaza_baza_proiect.sql
