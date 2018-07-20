#!/usr/bin/python

#

import sys
import pwd
from ldap3 import Server, Connection, Tls, SASL, KERBEROS, ALL
import ssl
from pprint import pprint


# the AD servers are load balanced
# We do not pick just one of them - get the name from the DNS
# The SRV records return a list of the AD controllers
# dig -t SRV _ldap._tcp.ad.example.com

# this computer should be joined to the domain as a computer object by now
# so we have Kerberos credentials valid for a GSS bind
# after all sssd is supposed to work - it uses GSS
#
# to list the SASL types available
# ldapsearch -h  SERVER2.ourdom.company.net -p 389 -x -b "" -s base -LLL supportedSASLMechanisms


if __debug__:
    print 'Trying to bind now'

adserver = Server('SERVER2.ourdom.company.net', get_info=ALL)
#adserver = Server('adtest.private', get_info=ALL)
# ourdom\myname    may need the domain name ourdom
adconn = Connection(adserver, user='ourdom\myname', password='mypassword',raise_exceptions=True)

# using Kerberos. See http://ldap3.readthedocs.io/bind.html
# adconn = Connection(server, user='ldap-client/client.example.com', authentication=SASL, sasl_mechanism=KERBEROS)

if __debug__:
    adconn.open()  # establish connection without performing any bind (equivalent to ANONYMOUS bind)
    #print 'AD server supports' ,(adserver.info.supported_sasl_mechanisms)

try:
    adconn.bind()  # we could auto bind when setting up the connection object
except:
    if __debug__:
        print 'Failed AD Bind'
        exit(1)
    # If we fail then log an error
    # If we fail then send an email  ???

# !!!!!! Try an Anonymoud bind
# Also we ahve a service account rather than using my username nad password


# we seem to have a valid bind let us look for my information
# this is from a Windows dsquery I am
# CN=myname,OU=Managed,OU=Users,OU=Bigcorp_Production,DC=ourdom,DC=bigcorp,DC=net
# search_base = 'OU=Managed,OU=Users,OU=Bigcorp_Production,DC=ourdom,DC=bigcorp,DC=net'
search_base = 'OU=Users,OU=Bigcorp_Production,DC=ourdom,DC=bigcorp,DC=net'
# attrs = ['*']  # we ask AD for everything about the user
attrs = ['displayName','sn']


# we also get a Homedirectory and a Home Drive
# assume these do not clash with the Unix home Directory
#homeDirectory: \\DKTA05FP\EPF$
#    homeDrive: N:



# loop through the file of input users
# we should really look at each line of the local /etc/passwd file here
# this is wrong - we are getting too many non-user accounts over 1000
for user in pwd.getpwall():
    username,passwd,uid,gid,gecos,homedir,shell = user
    # if __debug__:
    #     print username, uid, gid
    if uid < 1999: continue #do not process system accounts
    if __debug__:
         print username, 'is a non system user'
    # get the Active Directory uid number for this user
    # we assume a one to one mapping of username and CommonName
    search_filter = '(CN='+username+')'
    adconn.search(search_base, search_filter, attributes=attrs)
    pprint(adconn.entries)













adconn.unbind # close the connection to the AD server
