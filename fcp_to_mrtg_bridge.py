#!/usr/bin/env python2
"""
Output specified node stats in a format expected by MRTG

This code was written by Zothar, April 2007, released under the GNU Lesser General
Public License.

No warranty, yada yada

Note: MRTG doesn't seem to handle non-integer numbers as anything but truncated (rounded?) integers

"""

import fcp;
import sys;

stat_fields = [];

host = "127.0.0.1";
port = 9481;

list_fields_flag = False;

def usage():
  print "Usage: %s [<host>[:<port>]] <stat_field1>,<stat_field2>" % ( sys.argv[ 0 ] );
  print "       %s [<host>[:<port>]] --list-fields" % ( sys.argv[ 0 ] );
  print;
  print "Example:";
  print "  %s averagePingTime,runningThreadCount" % ( sys.argv[ 0 ] );

argv = sys.argv;
arg0 = argv[ 0 ];
argv = argv[ 1: ];
argc = len( argv );
if( 0 == argc ):
  usage();
  sys.exit( 1 );
for arg in argv:
  if( "--" == arg[ :2 ] ):
    option = arg[ 2: ];
    if( "list-fields" == option ):
      list_fields_flag = True;
    else:
      print "Unknown option: %s" % ( arg );
      print;
      usage();
      sys.exit( 1 );
  i = arg.find( ":" );
  if( -1 != i ):
    argfields = arg.split( ":" );
    if( 2 != len( argfields )):
      usage();
      sys.exit( 1 );
    host = argfields[ 0 ];
    port = int( argfields[ 1 ] );
    continue;
  i = arg.find( "," );
  if( -1 != i ):
    argfields = arg.split( "," );
    for argfield in argfields:
      if( 0 == len( argfield )):
        continue;
      stat_fields.append( argfield );
    continue;
  i = arg.find( "." );
  if( -1 != i ):
    host = arg;
    continue;
  stat_fields.append( arg );

if( 2 != len( stat_fields ) and not list_fields_flag ):
  print "Must specify two stat_fields when not using --list-fields";
  print;
  usage();
  sys.exit( 1 );

f = fcp.FCPNode( host = host, port = port );
entry = f.refstats( WithVolatile = True );
f.shutdown();
if( list_fields_flag ):
  keys = entry.keys();
  keys.sort();
  print "Volatile fields:";
  for key in keys:
    if( not key.startswith( "volatile." )):
      continue;
    print key[ 9: ];
  print;
  print "non-volatile fields:"
  for key in keys:
    if( key.startswith( "volatile." )):
      continue;
    print key;
else:
  for stat_field in stat_fields:
    try:
      datum_string = entry[ "volatile." + stat_field ];
    except KeyError, msg:
      try:
        datum_string = entry[ stat_field ];
      except KeyError, msg:
        print "0";
        continue;
    datum = float( datum_string );
    try:
      test_datum = int( datum );
    except ValueError, msg:
      test_datum = None;
    if( test_datum == datum ):
      datum = test_datum;
    print "%s" % ( datum );
  print "%s" % ( entry[ "volatile.uptimeSeconds" ] );
  print "%s" % ( entry[ "myName" ] );
