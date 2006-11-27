#!/usr/bin/env python
"""
Update portions of the pyfcp files, specifically the refbot related ones at the moment
"""

import base64
import StringIO
import sys, time, traceback, time
import socket, select
import threading
import os #not necessary but later on I am going to use a few features from this
import urllib2

print "Not implemented yet (updater.py from SVN)"
sys.exit( 1 );

# This file is just here so that the updater has something to self-update to while it's being developed

base_url = "http://emu.freenetproject.org/cgi-bin/view-cvs/trunk/apps/pyFreenet/";
files_to_update = [
  "fcp/node.py",
  "refbot.py",
  "minbot.py",
  ];
updater_backup_url = "https://emu.freenetproject.org/svn/trunk/apps/pyFreenet/updater.py";  # A second way to update ourself in case the first one changes URLs or something
versions_filename = "updater_versions.dat";

versions_file_lines = [];
try:
  versions_file = file( versions_filename, "r" );
  versions_file_lines = versions_file.readlines();
  version_file.close();
except:
  pass;  # Ignore a non-existent versions_file
local_versions = {};
for versions_file_line in versions_file_lines:
  versions_file_line = version_file_line.strip();
  versions_file_line_fields = version_file_line.split();
  if( 2 != versions_file_line_fields ):
    continue;
  filename = versions_file_line_fields[ 1 ];
  version = versions_file_line_fields[ 1 ];
  try:
    local_versions[ filename ] = int( version );
  except:
    pass;  # Ignore file versions we can't parse
if(not local_versions.has_key( "updater.py" )):
  local_versions[ "updater.py" ] = 0;
base_url_lines = [];
updater_backup_url_lines = [];
try:
  base_url_file = urllib2.urlopen(base_url);
  base_url_lines = base_url_file.readlines()
  base_url_file.close();
except:
  try:
    updater_backup_url_file = urllib2.urlopen(updater_backup_url);
    updater_backup_url_lines = updater_backup_url_file.readlines()
    updater_backup_url_file.close();
  except:
    print "Couldn't fetch fetch the base URL information or the updater backup URL for some reason.  You may have to update the updater via other means or try again later.";
    sys.exit( 1 );
if( 0 != len( base_url_lines )):  # If we could download the View CVS directory listing...
  for base_url_line in base_url_lines:
    base_url_line = base_url_line.strip();
    print "DEBUG: base_url_line: [%s]" % ( base_url_line );
else:
  if( 0 != len( updater_backup_url_lines )):  # If we could download the updater from the backup URL
    for updater_backup_url_line in updater_backup_url_lines:
      updater_backup_url_line = updater_backup_url_line.rstrip();
      print "DEBUG: updater_backup_url_line: [%s]" % ( updater_backup_url_line );
  else:
    print "Couldn't fetch fetch the base URL information and the updater backup URL returned no data.  You may have to update the updater via other means or try again later.";
    sys.exit( 1 );
print "Not implemented yet"
sys.exit( 1 );
