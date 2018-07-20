#!/bin/bash

username='jk'



#infinite loop
while :
do
 #sudo sss_cache -E
 date
 /usr/bin/time  -f "\t%E" groups $username | tr ' ' '\n' | wc -l
 echo
 echo
 sleep 60
done




exit


