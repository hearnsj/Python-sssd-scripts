#!/usr/bin/env bash

for user in   `sss_override user-find | cut -f 1 -d ':'` ;do
    echo $user
    sss_override user-del $user
 done
