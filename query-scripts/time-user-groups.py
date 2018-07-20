#!/usr/bin/python

#

import sys
import os
import pwd
#from ldap3 import Server, Connection, Tls, SASL, KERBEROS, ALL
#import ssl
from pprint import pprint



# the AD servers are load balanced
# We do not pick just one of them - get the name from the DNS
# The SRV records return a list of the AD controllers
# dig -t SRV _ldap._tcp.ad.example.com

# this computer should be joined to the domain as a computer object by now
# so we have Kerberos credentials valid for a GSS bind
# after all sssd is supposed to work - it uses GSS
def getgroups(username):
    format='"\t%E"'
    try:
        os.system('/usr/bin/time -f "\t%E" echo %s ' %(username))
    except:
        return(0) # we do not care if this fails


#
# we should really look at each line of the local /etc/passwd file here
for user in pwd.getpwall():
    username,passwd,uid,gid,gecos,homedir,shell = user
    # if __debug__:
    #     print username, uid, gid
    if uid < 1999: continue #do not process system accounts
    if __debug__:
         print 'Timing user ', username
         getgroups(username)

    # timeit
