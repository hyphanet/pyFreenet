#!/usr/bin/env python
"""
Update portions of the pyfcp files, specifically the refbot related ones at the moment

This is very much tied to the current way View CVS works, which we use so we
know what SVN versions we're updating to, etc.
"""

import StringIO;
import base64;
import os;
import select;
import socket;
import sys;
import threading;
import time;
import traceback;
import urllib2;

print "Not implemented yet (updater.py from SVN)"
sys.exit( 1 );

base_url = "http://emu.freenetproject.org/cgi-bin/viewcvs.cgi/trunk/apps/pyFreenet/";
download_base_url = "http://emu.freenetproject.org/cgi-bin/viewcvs.cgi/*checkout*/trunk/apps/pyFreenet/";
# updater.py should be left out of files_to_update
files_to_update = [
  "fcp/node.py",
  "refbot.py",
  "minibot.py",
  ];
updater_backup_url = "https://emu.freenetproject.org/svn/trunk/apps/pyFreenet/updater.py";  # A second way to update ourself in case the first one changes URLs or something
updater_filename = "updater.py";
versions_filename = "updater_versions.dat";

def download_file( download_base_url, filename, version ):
  print "Downloading %s ..." % ( filename );
  download_url = "%s?rev=%d" % ( os.path.join( download_base_url, filename ), version );
  #print "download_file(): Not implemented yet: %s" % ( download_url );
  download_url_file = urllib2.urlopen(download_url);
  download_url_lines = download_url_file.readlines()
  download_url_file.close();
  return download_url_lines;

def needs_update( filename, local_versions, remote_versions ):
  if( not local_versions.has_key( filename )):
    local_versions[ filename ] = 0;
  if( remote_versions.has_key( filename )):
    if( local_versions[ filename ] < remote_versions[ filename ] ):
      return True;
  return False;

def process_raw_remote_versions_data( remote_versions, input_lines ):
  print "Processing the base file list...";
  for input_line in input_lines:
    # Yeah, this is very tied to the output of View CVS at the moment...
    input_line = input_line.strip();
    if(0 == len( input_line )):
      continue;
    searchstr = "<td><a name=\"";
    searchstrlen = len( searchstr );
    i = input_line.find( searchstr );
    if( -1 == i ):
      continue;
    #print "DEBUG: input_line: [%s]" % ( input_line );
    buf = input_line[ ( i + searchstrlen ) : ];
    #print "  DEBUG: buf: [%s]" % ( buf );
    searchstr = '"';
    searchstrlen = len( searchstr );
    i = buf.find( searchstr );
    if( -1 == i ):
      continue;
    filename = buf[ :i ];
    searchstr = "?rev=";
    searchstrlen = len( searchstr );
    i = buf.find( searchstr );
    if( -1 == i ):
      continue;
    buf = buf[ ( i + searchstrlen ) : ];
    searchstr = "&";
    searchstrlen = len( searchstr );
    i = buf.find( searchstr );
    if( -1 != i ):
      buf = buf[ :i ];
    #print "  DEBUG: buf: [%s]" % ( buf );
    try:
      version = int( buf );
      remote_versions[ filename ] = version;
    except:
      continue;  # We'll ignore something we can't parse and if we get nothing in remote_versions in the end, we can detect that as a problem

def read_local_versions_file( local_versions, versions_filename ):
  print "Reading local versions data file...";
  versions_file_lines = [];
  try:
    versions_file = file( versions_filename, "r" );
    versions_file_lines = versions_file.readlines();
    versions_file.close();
  except:
    pass;  # Ignore a non-existent versions_file
  for versions_file_line in versions_file_lines:
    versions_file_line = versions_file_line.strip();
    #print "DEBUG: versions_file_line: [%s]" % ( versions_file_line );
    versions_file_line_fields = versions_file_line.split();
    if( 2 != len( versions_file_line_fields )):
      continue;
    filename = versions_file_line_fields[ 1 ];
    version = versions_file_line_fields[ 0 ];
    #print "DEBUG: filename: %s  version: %s" % ( filename, version );
    try:
      local_versions[ filename ] = int( version );
    except:
      continue;  # Ignore file versions we can't parse

def write_file( updated_filename, updated_file_lines ):
  print "Writing updated %s ..." % ( updated_filename );
  updated_file = file( updated_filename, "w+" );
  updated_file.writelines( updated_file_lines );
  updated_file.close();

def write_local_versions_file( local_versions, versions_filename ):
  versions_file = file( versions_filename, "w+" );
  local_version_keys = local_versions.keys();
  local_version_keys.sort();
  for local_version_key in local_version_keys:
    versions_file.write( "%d %s\n" % ( local_versions[ local_version_key ], local_version_key ));
  versions_file.close();

# We want to work in the directory where pyfcp is installed
os.chdir( os.path.dirname( sys.argv[ 0 ] ));

# We dont' want the updater file in files_to_update
if( updater_filename in files_to_update ):
  files_to_update.remove( updater_filename );

local_versions = {};
remote_versions = {};
read_local_versions_file( local_versions, versions_filename );
if( not local_versions.has_key( updater_filename )):
  local_versions[ updater_filename ] = 0;
base_url_lines = [];
updater_backup_url_lines = [];
try:
  print "Downloading the base file list...";
  base_url_file = urllib2.urlopen(base_url);
  base_url_lines = base_url_file.readlines()
  base_url_file.close();
except:
  print "Base file list download failed.";
  try:
    print "Downloading the updater from the updater backup URL...";
    updater_backup_url_file = urllib2.urlopen(updater_backup_url);
    updater_backup_url_lines = updater_backup_url_file.readlines()
    updater_backup_url_file.close();
  except:
    print "Couldn't fetch the base URL information or the updater backup URL for some reason.  You may have to update the updater via other means or try again later.";
    sys.exit( 1 );
if( 0 != len( base_url_lines )):  # If we could download the View CVS directory listing...
  process_raw_remote_versions_data( remote_versions, base_url_lines );
else:
  print "Using the updater downloaded from the updater backup URL...";
  if( 0 != len( updater_backup_url_lines )):  # If we could download the updater from the backup URL
    for updater_backup_url_line in updater_backup_url_lines:
      print "DEBUG: updater_backup_url_line: [%s]" % ( updater_backup_url_line.rstrip() );
    write_file( updater_filename, updater_backup_url_lines );
    print "Executing the backup updater URL updated updater.py...";
    execfile( updater_filename );
    sys.exit( 0 );  # execfile() doesn't appear to return, but just in case...
  else:
    print "Couldn't fetch the base URL information and the updater backup URL returned no data.  You may have to update the updater via other means or try again later.";
    sys.exit( 1 );
#print "DEBUG: local_versions: [%s]" % ( local_versions );
#print "DEBUG: remote_versions: [%s]" % ( remote_versions );
if( needs_update( updater_filename, local_versions, remote_versions )):
  try:
    downloaded_file_lines = download_file( download_base_url, updater_filename, remote_versions[ updater_filename ] );
  except:
    print "Couldn't fetch the updater directly.  You may have to update the updater via other means or try again later.";
    sys.exit( 1 );
  #for downloaded_file_line in downloaded_file_lines:
  #  print "DEBUG: downloaded_file_line: [%s]" % ( downloaded_file_line.rstrip() );
  write_file( updater_filename, downloaded_file_lines );
  local_versions[ updater_filename ] = remote_versions[ updater_filename ];
  print "Writing updated local versions data file...";
  write_local_versions_file( local_versions, versions_filename );
  print "Executing the updated updater.py...";
  execfile( updater_filename );
  sys.exit( 0 );  # execfile() doesn't appear to return, but just in case...
for file_to_update in files_to_update:
  if( needs_update( file_to_update, local_versions, remote_versions )):
    print "DEBUG: %s needs update" % ( file_to_update );
print "Not implemented yet"
sys.exit( 1 );
