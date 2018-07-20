#!/usr/bin/python
# We run the command to get the groups of a user
# flush the cache
# run this again - is there any difference int he groups returned?

#import sys
import os
#import pwd
#import grp
# from ldap3 import Server, Connection, Tls, SASL, KERBEROS, ALL
# import ssl
from pprint import pprint


def getgroups(username):
    # format='"\t%E"'
    try:
        os.system('/usr/bin/groups %s ' %(username))
    except:
        return(0)  # we do not care if this fails

    if __debug__:
        print username


username='jk'
getgroups(username)

pprint (grp.getgrgid(1000))
