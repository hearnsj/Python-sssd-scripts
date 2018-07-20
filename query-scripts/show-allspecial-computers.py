#!/usr/bin/python

#

import sys
import pwd
from ldap3 import Server, ServerPool, Connection, Tls, SASL, KERBEROS, ALL
import ssl
from pprint import pprint

# the AD servers are load balanced
# We do not pick just one of them - get the name from the DNS
# The SRV records return a list of the AD controllers
# dig -t SRV _ldap._tcp.ad.example.com

# this computer should be joined to the domain as a computer object by now
# so we have Kerberos credentials valid for a GSS bind
# after all sssd is supposed to work - it uses GSS

if __debug__:
    print 'Trying to bind now'

# we define a pool of AD servers. Thsi may be in the DNS SRV record
# so hard wiring like this is probably bad
adserver1 = Server('SERVER1.ourdom.bigcorp.net', get_info=ALL)
adserver2 = Server('SERVER2.ourdom.bigcorp.net', get_info=ALL)

ad_server_pool = ServerPool(servers=None, pool_strategy='ROUND_ROBIN', active=True, exhaust=False)
ad_server_pool.add(adserver1)
ad_server_pool.add(adserver2)

# ourdom\myname    may need the domain name ourdom
adconn = Connection(ad_server_pool, user='ourdom\myname', password='mypassword',raise_exceptions=True)
#adconn = Connection(ad_server_pool, user='ourdom\svc_bts_smb', password='e@ViNg0blESIZAt',raise_exceptions=True)
# anonymous Bind
# adconn = Connection(ad_server_pool, authentication='ANONYMOUS',raise_exceptions=True)
# using Kerberos. See http://ldap3.readthedocs.io/bind.html
# adconn = Connection(server, user='ldap-client/client.example.com', authentication=SASL, sasl_mechanism=KERBEROS)

if __debug__:
    adconn.open()  # establish connection without performing any bind (equivalent to ANONYMOUS bind)
    # print 'AD server supports' ,(server2.info.supported_sasl_mechanisms)

try:
    adconn.bind()  # we could auto bind when setting up the connection object
except:
    if __debug__:
        print 'Failed AD Bind'
    # Log the error here - do not exit without logging a reason
    exit(1)

# computer account: CN=IBIS,CN=Computers,DC=ourdom,DC=bigcorp,DC=net
#search_base = 'CN=Computers,DC=ourdom,DC=bigcorp,DC=net'
search_base = 'OU=Special,OU=Servers,DC=ourdom,DC=bigcorp,DC=net'
search_filter = '(CN=' + str(sys.argv[1]) + ')' # no argument checking....
search_filter = '(CN=*)'
if __debug__:
    print 'Searching for computer ', search_filter
attrs = ['*']
adconn.search(search_base, search_filter, attributes=attrs)
pprint(adconn.entries)

adconn.unbind # close the connection to the AD server
