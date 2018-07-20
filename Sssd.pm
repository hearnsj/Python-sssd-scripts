package Sssd;

use Rex -base;

desc "Configure ssd authentication";
#
task "Install", => sub {
  #
  my $hostname = run "/bin/hostname -s";
  #
  install package => ["sssd","sssd-tools","packagekit",
                       "libnss-sss","libpam-sss","adcli","realmd","msktutil"];
  # sssd is a meta package
  # We need to use apt to install this specific version
  # version 1.15.0-3ubuntu2~ubuntu16.04.1~ppa1
  # apt install sssd = 1.15.0-3ubuntu2~ubuntu16.04.1~ppa1
  # the main configuration file for sssd
  file "/etc/sssd/sssd.conf",
      source => "files/sssd/etc/sssd/sssd.conf",
      owner => "root",
      mode  => "600";
  #
  # used once when using realmd to join the AD realm
  # remember we need to replace the sssd.conf which is made by realmd
  # with our custom sssd.conf
  file "/etc/realmd.conf",
      source => "files/sssd/etc/realmd.conf";
  #
  # nsswitch.conf defines the sources for userids groupids
  # Note:  sudoers files
  # If sss is added to sudoers there are errors reported on our systems
  file "/etc/nsswitch.conf",
       source => "files/sssd/etc/nsswitch.conf";
  #
  # cron job to update the computer account every 30 days
  # Enable the update and configure an option which gives $HOSTNAME
  file "/etc/default/msktutil",
      source => "files/sssd/etc/default/msktutil",
      owner => "root", mode  => "644";
  #
  # disable apport error reporting
  # this stops the popup windows which invite the user to send error reports
  file "/etc/default/apport",
      source => "files/sssd/etc/default/apport",
      owner => "root", mode  => "644";

  # this file defines the mappings between the AD uids and groupids
  # and the existing userids/groupids which we have in /etc/passwd
  # the file is read in by sss_override
  file "/etc/sssd/overrides",
      source => "files/sssd/etc/sssd/overrides",
      owner => "root",
      mode  => "664";
  #
  # this script creates the overrides file
  file "/usr/local/sbin/create-sssd-overrides.py",
      source => "files/sssd/usr/local/sbin/create-sssd-overrides.py",
      owner => "root",
      mode  => "744";


  # An edit to the sssd service unit file
  # We run sss_override after the sssd.service starts
  # This is a local change to the service file so should go to /etc/systemd/system
  file "/etc/systemd/system/sssd.service",
      source => "files/sssd/etc/systemd/system/sssd.service";
  #
  # configure the lightdm window manager
  # create a configuration file directory
  file "/etc/lightdm/lightdm.conf.d",
      ensure => "directory",
      owner  => "root",
      group  => "root",
      mode   => "755";
  # this configuration means that a list of users is NOT presented
  # the user must put in their username and password
  file "/etc/lightdm/lightdm.conf.d/50-unity-greeter.conf",
      source => "files/sssd/etc/lightdm/lightdm.conf.d/50-unity-greeter.conf",
      owner => "root",
      group => "root",
      mode  => "664";
  #
  # Now we must configure the PAM modules to use sss authentication
  #
  # We can run the pam-auth-update utility
  # This uses the definitions in  /usr/share/pam-configs
  # This is the correct way to do this task
  # /usr/sbin/pam-auth-update --force --package
  #
  # Or we could copy the correct set of PAM files from the Rex master
  #
  file "/etc/pam.d/common-account",
    source => "files/sssd/etc/pam.d/common-account",
    owner => "root", group => "root", mode => 644;
  #
  file "/etc/pam.d/common-auth",
    source => "files/sssd/etc/pam.d/common-auth",
    owner => "root", group => "root", mode => 644;
  #
  file "/etc/pam.d/common-password",
    source => "files/sssd/etc/pam.d/common-password",
    owner => "root", group => "root", mode => 644;
  #
  file "/etc/pam.d/common-session",
    source => "files/sssd/etc/pam.d/common-session",
    owner => "root", group => "root", mode => 644;
  #
  file "/etc/pam.d/common-session-noninteractive",
    source => "files/sssd/etc/pam.d/common-session-noninteractive",
    owner => "root", group => "root", mode => 644;
  #
  # We could automate the realm join here
  # run "echo password | /usr/sbin/realm join --user=svc_bts_smb  ourdom.bigcorp.net "
  # This is necessary - we need this key to renew the machine password every 30 days
  #run "echo password | /usr/bin/kinit svc_bts_smb";
  # Allow all logins from the realm
  run "/usr/sbin/realm permit  -a -R ourdom.bigcorp.net";
  #
  # Get a ticket for this host principal
  # This is not correct. The \ will not be correctly quoted here
  my $principal = uc $hostname.'\\$@ourdom.bigcorp.NET'; #hostname in upper case
  run "/usr/bin/kinit -k $principal";
  # We should start or restart the sssd daemon at this point
  run "systemctl stop  sssd.service";
  run "systemctl start sssd.service";
  #
  };

1;
