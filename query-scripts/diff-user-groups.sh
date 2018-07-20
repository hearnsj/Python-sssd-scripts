#!/bin/bash

username='jk'


# first time before the loop
oldgroups=$(groups $username)
#echo $oldgroups



#infinite loop
while :
do
   echo 'Running groups' $username
   # flush the cache
   # sudo /usr/sbin/sss_cache -E
   sssctl cache-remove
   newgroups=$(groups $username) #form newgroups
   # echo $newgroups
   # compare this output with the output from the last time round the loop
   diff  <(echo "$oldgroups" ) <(echo "$newgroups")
   oldgroups=$newgroups # store this value for the next time round the loop
   sleep 2
done


# flush the cache


exit


getent passwd | while IFS=: read -r username password uid gid gecos home shell; do
  if  (( $uid > 1999)); then
    echo -n $username '  '
    /usr/bin/time  -f "\t%E" groups $username | tr ' ' '\n' | wc -l
    #groups $username
  fi
done
