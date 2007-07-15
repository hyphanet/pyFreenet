#!/usr/bin/env python
"""
Update portions of the pyfcp files, specifically the refbot related ones at the moment

This is very much tied to the current way View CVS works, which we use so we
know what SVN versions we're updating to, etc.

This code was written by Zothar, November 2006, released under the GNU Lesser General
Public License.

No warranty, yada yada
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

has_platform_module = False;
try:
  import platform;
  has_platform_module = True;
except:
  pass;

base_url = "http://emu.freenetproject.org/cgi-bin/viewcvs.cgi/trunk/apps/pyFreenet/";
download_base_url = "http://emu.freenetproject.org/cgi-bin/viewcvs.cgi/*checkout*/trunk/apps/pyFreenet/";
# updater.py should be left out of files_to_update
files_to_update = [
  "fcp/node.py",
  "bogon-bn-agg.txt",
  "refbot.py",
  "minibot.py",
  ];
updater_backup_url = "https://emu.freenetproject.org/svn/trunk/apps/pyFreenet/updater.py";  # A second way to update ourself in case the first one changes URLs or something
updater_filename = "updater.py";
updater_updated_flagfile_name = "updater_updated.flag";
versions_filename = "updater_versions.dat";

def do_revision_substitution( downloaded_file_lines, revision ):
  substituted_file_lines = [];
  substituted_string = "$Revision: %d $" % ( revision );
  for downloaded_file_line in downloaded_file_lines:
    substituted_file_lines.append( downloaded_file_line.replace( "$Revision$", substituted_string ));
  return substituted_file_lines;

def download_file( download_base_url, filename, version ):
  print "Downloading %s r%d ..." % ( filename, version );
  download_url = "%s?rev=%d" % ( os.path.join( download_base_url, filename ), version );
  download_url_file = urllib2.urlopen(download_url);
  download_url_lines = download_url_file.readlines()
  download_url_file.close();
  return download_url_lines;

def get_remote_versions_data( url ):
  url_file = urllib2.urlopen(url);
  url_lines = url_file.readlines()
  url_file.close();
  return url_lines;

def my_exit( exit_status ):
  if( not has_platform_module or ( has_platform_module and "Windows" == platform.system())):
    raw_input( "Hit Enter or Return to continue..." );
  sys.exit( exit_status );

def needs_update( filename, local_versions, remote_versions ):
  if( not local_versions.has_key( filename )):
    local_versions[ filename ] = 0;
  if( remote_versions.has_key( filename )):
    if( local_versions[ filename ] < remote_versions[ filename ] ):
      return True;
    if( not os.path.exists( filename )):
      return True;
  return False;

def process_raw_remote_versions_data( remote_versions, input_lines, filename_prefix ):
  for input_line in input_lines:
    # This is very tied to the output of View CVS...
    input_line = input_line.strip();
    if(0 == len( input_line )):
      continue;
    searchstr = "<td><a name=\"";
    searchstrlen = len( searchstr );
    i = input_line.find( searchstr );
    if( -1 == i ):
      continue;
    buf = input_line[ ( i + searchstrlen ) : ];
    searchstr = '"';
    searchstrlen = len( searchstr );
    i = buf.find( searchstr );
    if( -1 == i ):
      continue;
    filename = buf[ :i ];
    filename = filename_prefix + filename;
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
    versions_file_line_fields = versions_file_line.split();
    if( 2 != len( versions_file_line_fields )):
      continue;
    filename = versions_file_line_fields[ 1 ];
    version = versions_file_line_fields[ 0 ];
    try:
      local_versions[ filename ] = int( version );
    except:
      continue;  # Ignore file versions we can't parse

def update_file_blindly( filename, url ):
  try:
    print "Downloading %s blindly from %s ..." % ( filename, url );
    downloaded_file_file = urllib2.urlopen(url);
    downloaded_file_lines = downloaded_file_file.readlines()
    downloaded_file_file.close();
  except:
    print "Couldn't fetch file.  Things must be messed up somewhere.  Try again later.";
    my_exit( 1 );
  write_file( filename, downloaded_file_lines );

def use_download_everything_mode():
  print;
  print;
  print "** Falling back to download everything mode.  Do not run updater.py again until you think the primary update mechanism is fixed or an update is otherwise needed. **";
  print;
  update_file_blindly( "fcp/node.py", "https://emu.freenetproject.org/svn/trunk/apps/pyFreenet/fcp/node.py" );
  update_file_blindly( "minibot.py", "https://emu.freenetproject.org/svn/trunk/apps/pyFreenet/minibot.py" );
  update_file_blindly( "refbot.py", "https://emu.freenetproject.org/svn/trunk/apps/pyFreenet/refbot.py" );
  print;
  print "**    Fell back to download everything mode.  Do not run updater.py again until you think the primary update mechanism is fixed or an update is otherwise needed. **";
  print;

def use_updater_backup_url( url ):
  try:
    print "Downloading the updater from the updater backup URL...";
    url_file = urllib2.urlopen(url);
    url_lines = url_file.readlines()
    url_file.close();
  except:
    print "Couldn't fetch the base URL information or the updater backup URL for some reason.  You may have to update the updater via other means or try again later.";
    my_exit( 1 );
  return url_lines;

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
os.chdir( os.path.dirname( os.path.abspath( sys.argv[ 0 ] )));

# We don't want the updater file in files_to_update
if( updater_filename in files_to_update ):
  files_to_update.remove( updater_filename );

local_versions = {};
remote_versions = {};
subdirs = [];
read_local_versions_file( local_versions, versions_filename );
if( not local_versions.has_key( updater_filename )):
  local_versions[ updater_filename ] = 0;
base_url_lines = [];
updater_backup_url_lines = [];
need_updater_backup_url = False;
had_updater_updated_flagfile = False;
if( os.path.exists( updater_updated_flagfile_name )):
  had_updater_updated_flagfile = True;
  os.remove( updater_updated_flagfile_name );
try:
  print "Downloading the base file list...";
  base_url_lines = get_remote_versions_data( base_url );
except:
  need_updater_backup_url = True;
  print "Base file list download failed.";
  if( not had_updater_updated_flagfile ):
    updater_backup_url_lines = use_updater_backup_url( updater_backup_url );
  else:
    use_download_everything_mode();
    my_exit( 0 );
if( 0 != len( base_url_lines )):  # If we could download the View CVS directory listing...
  print "Processing the base file list...";
  process_raw_remote_versions_data( remote_versions, base_url_lines, "" );
  if( 0 >= len( remote_versions.keys() )):
    need_updater_backup_url = True;
    print "Base file list parsed incorrectly."
    if( not had_updater_updated_flagfile ):
      updater_backup_url_lines = use_updater_backup_url( updater_backup_url );
    else:
      use_download_everything_mode();
      my_exit( 0 );
if( need_updater_backup_url ):
  print "Using the updater downloaded from the updater backup URL...";
  if( 0 != len( updater_backup_url_lines )):  # If we could download the updater from the backup URL
    write_file( updater_filename, updater_backup_url_lines );
    print "Writing updater updated flagfile...";
    write_file( updater_updated_flagfile_name, [ "updater updated\n" ] );
    print "Executing the backup updater URL updated updater.py...";
    execfile( updater_filename );
    my_exit( 0 );  # execfile() doesn't appear to return, but just in case...
  else:
    print "Couldn't fetch the base URL information and the updater backup URL returned no data.  You may have to update the updater via other means or try again later.";
    my_exit( 1 );
if( needs_update( updater_filename, local_versions, remote_versions )):
  try:
    downloaded_file_lines = download_file( download_base_url, updater_filename, remote_versions[ updater_filename ] );
  except:
    print "Couldn't fetch the updater directly.  You may have to update the updater via other means or try again later.";
    my_exit( 1 );
  write_file( updater_filename, downloaded_file_lines );
  local_versions[ updater_filename ] = remote_versions[ updater_filename ];
  print "Writing updated local versions data file...";
  write_local_versions_file( local_versions, versions_filename );
  print "Writing updater updated flagfile...";
  write_file( updater_updated_flagfile_name, [ "updater updated\n" ] );
  print "Executing the updated updater.py...";
  execfile( updater_filename );
  my_exit( 0 );  # execfile() doesn't appear to return, but just in case...
for file_to_update in files_to_update:
  if( -1 != file_to_update.find( "/" )):
    file_to_update_dir = os.path.dirname( file_to_update );
    if( not file_to_update_dir in subdirs ):
      subdirs.append( file_to_update_dir + "/" );
for subdir in subdirs:
  subdir_url = base_url + subdir;
  subdir_url_lines = [];
  try:
    print "Downloading the %s file list..." % ( subdir );
    subdir_url_lines = get_remote_versions_data( subdir_url );
  except:
    print "%s file list download failed." % ( subdir );
  if( 0 != len( subdir_url_lines )):  # If we could download the View CVS directory listing...
    print "Processing the %s file list..." % ( subdir );
    process_raw_remote_versions_data( remote_versions, subdir_url_lines, subdir );
updated_a_file_flag = False;
for file_to_update in files_to_update:
  if( needs_update( file_to_update, local_versions, remote_versions )):
    try:
      downloaded_file_lines = download_file( download_base_url, file_to_update, remote_versions[ file_to_update ] );
    except:
      print "Couldn't fetch the updater directly.  You may have to update the updater via other means or try again later.";
      my_exit( 1 );
    downloaded_file_lines = do_revision_substitution( downloaded_file_lines, remote_versions[ file_to_update ] );
    write_file( file_to_update, downloaded_file_lines );
    updated_a_file_flag = True;
    local_versions[ file_to_update ] = remote_versions[ file_to_update ];
# Always write the local versions data file so that running the updater will de-age the release, even when no changes have been committed in the last two weeks
print "Writing local versions data file...";
write_local_versions_file( local_versions, versions_filename );
my_exit( 0 );
