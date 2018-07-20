#!/usr/bin/python

# python script which creates a file of mappings from usernames to existing UID numbers
# see  man sss_override  for documentation
#
#        user-import FILE
#           Import user overrides from FILE. Data format is similar to standard passwd file. The format is:
#
#           original_name:name:uid:gid:gecos:home:shell
#
#           where original_name is original name of the user whose attributes should be overridden.
#           The rest of fields correspond to new values. You can
#           omit a value simply by leaving corresponding field empty.
#
#           Examples:
#
#           ckent:superman::::::
#
#           ckent@krypton.com::501:501:Superman:/home/earth:/bin/bash
#
# the plan is to run this script once per day on the Rex server
# the uid override file will be pushed out by Rex
# then the sssd daemon will be restarted

import sys
import pwd
from ldap3 import Server, ServerPool, Connection, Tls, SASL, KERBEROS, ALL
from pprint import pprint
# from ldap3.utils.log import set_library_log_detail_level, OFF, BASIC, NETWORK, EXTENDED



def bind_to_domain():
    if __debug__:
        print 'Trying to bind now'
    # adserver = Server('SERVER1.ourdom.bigcorp.net', get_info=ALL)
    adserver = Server('ourdom.bigcorp.net', use_ssl=True,get_info=ALL)
    # adconn = Connection(adserver,raise_exceptions=True)
    adconn = Connection(adserver)
    if __debug__:
        adconn.open()  # establish connection without performing any bind (equivalent to ANONYMOUS bind)
        print  'Can connect to AD server'
        #print 'AD server supports' ,(adserver.info.supported_sasl_mechanisms)

    try:
        adconn.bind()  # we could auto bind when setting up the connection object
    except:
        if __debug__:
            print 'Failed AD Bind'
        exit(1)
    return (adconn)


def is_ad_user(username):
    # the connection object adconn is global. Deliberately
    # We do not want to bind multiple times
    # we need to check that the user is in Managed or Non Managed
    # CN=myname,OU=Managed,OU=Users,OU=Bigcorp_Production,DC=ourdom,DC=bigcorp,DC=net
    # search_base = 'OU=Managed,OU=Users,OU=Bigcorp_Production,DC=ourdom,DC=bigcorp,DC=net'
    search_base = 'OU=Managed, OU=Users,OU=Bigcorp_Production,DC=ourdom,DC=bigcorp,DC=net'
    search_base = 'DC=ourdom,DC=bigcorp,DC=net'
    search_filter = '(CN=' + username + ')'
    # search_scope=ldap3.SUBTREE # we can have BASE LEVEL or SUBTREE
    if __debug__:
        print 'Searching for user', search_filter
        attrs = ['*']
        adconn.search(search_base, search_filter, attributes=attrs)
        pprint (adconn.entries)

    if adconn.search(search_base, search_filter):
        print username,  ' exists'
    else:
        print username, ' not in AD'

    return(True)







########################################################################
# Main
# should this really be global ??
global adconn  # does this have to be global?
# adconn=bind_to_domain() # connect to the AD server

adserver = Server('ourdom.bigcorp.net', use_ssl=True,get_info=ALL)
# adconn = Connection(adserver)
#adconn = (adserver, user='ourdom\myname', password='mypassword',raise_exceptions=True)
adconn = (adserver, user='ourdom\svc_bts_smb', password='mypassword',raise_exceptions=True)
adconn.open()  # establish connection without performing any bind (equivalent to ANONYMOUS bind)
adconn.bind()


# This is the 'master' passwd file on the Rexx server
existing_uids_file='/etc/passwd'
existing_uids=open(existing_uids_file, 'r') # open file read only

# define the output file which will be read in by sss_override
# This file will be pushed out to all workstations by Rexx
override_uids_file='/tmp/uids_override'
override_uids=open(override_uids_file,'w') #open a new file for write



# for user in existing_uids_file:
#    username,passwd,uid,gid,gecos,homedir,shell = user.split(':')

# use pwd.getpwdall. this function returns all local users in /etc/passwd
# this might be OK it depends where the Rexx server keeps
# the master list of users and groups
for user in pwd.getpwall():
    username,passwd,uid,gid,gecos,homedir,shell = user

    if uid < 1000: continue #do not process system accounts
    if uid > 9999: continue #do not process system accounts

    if __debug__:
         print 'User is', username, uid, gid, gecos

    # sss_override stops when it encounters a username not in the domain
    # We check if this account exists in Active Directory
    # Or is this an automated service use
    #if not is_ad_user(username): continue
    search_base = 'DC=ourdom,DC=bigcorp,DC=net'
    search_filter = '(CN=' + username + ')'
    if __debug__:
        print 'Searching for user', search_filter
        attrs = ['*']
        adconn.search(search_base, search_filter, attributes=attrs)
        pprint (adconn.entries)
    #
    override_uids.write("%s::%d:%d::%s::\n" %(username, uid, gid,homedir) )

existing_uids.close # Close input FILE
override_uids.close # close output FILE
#
# restart sssd if we have to !

adconn.unbind # close the connection to the AD server
