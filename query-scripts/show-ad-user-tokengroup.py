#!/usr/bin/python

import sys
import os
import pwd
from ldap3 import *
#from ldap3 import Server, ServerPool, Connection, Tls, SASL, KERBEROS, ALL, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES
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

# There is a pool fo AD servers. All you need dis get ourdom.bigcorp.net from DNS
adserver = Server('ourdom.bigcorp.net', use_ssl=True,get_info=ALL)
# adserver = Server('adtest.private', use_ssl=True,get_info=ALL)

adserver1 = Server('DKTA12DC.ourdom.bigcorp.net', use_ssl=True, get_info=ALL)
adserver2 = Server('SERVER2.ourdom.bigcorp.net', use_ssl=True, get_info=ALL)
ad_server_pool = ServerPool(servers=None, pool_strategy='ROUND_ROBIN', active=True, exhaust=False)
ad_server_pool.add(adserver1)
ad_server_pool.add(adserver2)

# ourdom\myname    may need the domain name ourdom
adconn = Connection(adserver, user='ourdom\myname', password='mypassword',raise_exceptions=True)
# adconn = Connection(adserver, user='adtest\myname', password='Bigcorp2018!',raise_exceptions=True)
# anonymous Bind
# adconn = Connection(ad_server_pool, authentication='ANONYMOUS',raise_exceptions=True)
# using Kerberos. See http://ldap3.readthedocs.io/bind.html
# tls = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2)
# server = Server('SERVER1.ourdom.bigcorp.net', use_ssl=True, tls=tls)
# adconn = Connection(adserver, user='ourdom\\kali', authentication='SASL', sasl_mechanism='KERBEROS',raise_exceptions=False)
# c.bind()
# print(c.extend.standard.who_am_i())
# adconn = Connection(server, user='ldap-client/client.example.com', authentication=SASL, sasl_mechanism=KERBEROS)

if __debug__:
    #print os.environ.get( "LOGONSERVER" )
    print(adconn)
    #adconn.open()  # establish connection without performing any bind (equivalent to ANONYMOUS bind)
    #print 'AD server supports' ,(adserver.info.supported_sasl_mechanisms)
    #print(adconn.extend.standard.who_am_i())

try:
    adconn.bind()  # we could auto bind when setting up the connection object
except:
    if __debug__:
        print 'Failed AD Bind'
        print (adconn.result)
    # Log the error here - do not exit without logging a reason
    exit(1)

# computer objects are here
# CN=IBIS,CN=Computers,DC=ourdom,DC=bigcorp,DC=net

# we seem to have a valid bind let us look for my information
# this is from a Windows dsquery I am
# CN=myname,OU=Managed,OU=Users,OU=Bigcorp_Production,DC=ourdom,DC=bigcorp,DC=net
search_base = ',OU=Managed,OU=Users,OU=Bigcorp_Production,DC=ourdom,DC=bigcorp,DC=net'
search_base = 'CN=' + str(sys.argv[1]) + search_base
#search_base = 'DC=ourdom,DC=bigcorp,DC=net'
#search_base = 'CN=Users,DC=adtest,DC=private'
search_filter = '(CN=' + str(sys.argv[1]) + ')' # no argument checking....
search_scope = 'BASE'
if __debug__:
    print 'Searching in base', search_base
    print 'Searching for user', search_filter
attrs = ['tokenGroups']
#attrs = [ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES]
#attrs = ldap3.ALL_ATTRIBUTES
#attrs = ['+']   plus means all operational attributes
adconn.search(search_base, search_filter, search_scope=BASE, attributes=attrs, get_operational_attributes=True)
pprint(adconn.entries)
#
# userobj = adconn.entries[0]  # clearly for several users we need to loop
# print 'Display Name', userobj.displayName
# print 'Department ',userobj.department









adconn.unbind # close the connection to the AD server
