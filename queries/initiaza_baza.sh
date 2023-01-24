#!/bin/bash

mysql -u dumitr -p"strongpass" < creaza_baza_proiect.sql
mysql -u dumitr -p"strongpass" < populeaza_baza_proiect.sql
