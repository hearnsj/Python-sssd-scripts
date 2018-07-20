#!/bin/bash


getent passwd | while IFS=: read -r username password uid gid gecos home shell; do
  if  (( $uid > 1999)); then
    echo -n $username '  '
    /usr/bin/time  -f "\t%E" groups $username | tr ' ' '\n' | wc -l
    #groups $username
  fi
done
