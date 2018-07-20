#!/usr/bin/python -O
# -O optimisation option switches off debug

# This script should be run when a new Unix user is added to the passwd file
# The script creates a file named /etc/sssd/overrides
# There is one line for each local Unix user
# The overrides file is read in when the sssd.service is started by systemd
# This is defined in the sssd.service unit file as an ExecPostAction

# see  man sss_override  for documentation
#
#        user-import FILE
#           Import user overrides from FILE. Data format is similar to the
#           standard passwd file. The format is:
#           original_name:name:uid:gid:gecos:home:shell
#
#           where original_name is original name of the user whose attributes
#           should be overriden.
#           The rest of fields correspond to new values. You can
#           omit a value simply by leaving corresponding field empty.
#
#           Examples:
#
#           ckent:superman::::::
#           ckent@krypton.com::501:501:Superman:/home/earth:/bin/bash

# import sys
import pwd
import os.path
import subprocess
# from pprint import pprint

# check that the sss_override program is installed
if not (os.path.isfile("/usr/sbin/sss_override")):
    print "Please install the sssd_tools package"
    exit(1)

# check that this script is being run with root privileges
if os.geteuid() != 0:
    print "Run create-sssd-overrides.py as root"
    exit(1)

# This is the file of usernames uids and gids which we create
# this can be read into another system
overfile = "/etc/sssd/overrides"

DEVNULL = open(os.devnull, 'w')

# the user accounts are in the /etc/passwd file
# tt may be better to just parse the passwd file
for user in pwd.getpwall():
    username, passwd, uid, gid, gecos, homedir, shell = user
    # by design Kerberos accounts are >= 900
    if uid < 899: continue  # do not process system accounts

    # Kerberos accounts also have shadow passwords character is *
    # system accounts have x as a password
    if passwd is 'x': continue  # do not process system accounts

    # deactivated users have the string deactivated in their homedir
    if 'deactivated' in homedir: continue
    if __debug__:
        print username, passwd, uid, gid

    # We run the sss_override utility for this user
    # If the username is not known in AD this will fail
    # We COULD do an LDAP search at this point -but quicker to just let it fail
    # The failure does not matter
    #
    # Note the command uses the name in uppercase
    # sss_override USERNAME -n username -u uid -g gid
    #
    try:
        subprocess.check_call("/usr/sbin/sss_override user-add %s -n %s -u %d -g %d -h %s"
                    %(username.upper(), username, uid, gid, homedir),
                    stdout=DEVNULL, stderr=DEVNULL, shell=True)
    except subprocess.CalledProcessError:
        # if this script is automated the output probably goes to the bit bucket
        print 'sss_override command fails for user ', username
        # if __debug__:
        #     print 'sss_override command fails for user ', username
# show us the user overrides which have been made
if __debug__:
    print 'The overrides are now set to'
    subprocess.call("/usr/sbin/sss_override user-find", shell=True)

# restart sssd. This is a good idea.
# sss_override prompts for a restart if it is needed
subprocess.call("/bin/systemctl restart sssd.service", shell=True)

# create a file with the overrides
# this file can be read in on another system using sss_override user-import
# The format of the file is similar as that of /etc/passwd:
# original_name:name:uid:gid:gecos:home:shell:base64_encoded_certificate
# Each line is prefixed with the original name field
# The password field is removed
# It is suffixed with a certificate field
subprocess.call("/usr/sbin/sss_override user-export %s" %(overfile), shell=True)
