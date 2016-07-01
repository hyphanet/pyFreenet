#!/usr/bin/env python
"""
Output specified node stats in a format expected by rrdtool

This code was written by Zothar, April 2007, released under the GNU Lesser General
Public License.

No warranty, yada yada

Example usage: rrdtool update freenet.rrd `/usr/local/pyFreenet/fcp_to_rrdtool_bridge.py averagePingTime,RunningThreadCount,location,locationChangePerSession`
"""

import fcp;
import sys;

stat_fields = [];

host = "127.0.0.1";
port = 9481;

list_fields_flag = False;

def usage():
  print("Usage: %s [<host>[:<port>]] [<stat_field>[,<stat_field> ...]]" % ( sys.argv[ 0 ] ));
  print("       %s [<host>[:<port>]] --list-fields" % ( sys.argv[ 0 ] ));
  print();
  print("Example:");
  print("  %s averagePingTime,runningThreadCount,location,locationChangePerSession" % ( sys.argv[ 0 ] ));

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
      print("Unknown option: %s" % ( arg ));
      print();
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

if( 0 == len( stat_fields ) and not list_fields_flag ):
  print("Must specify stat_fields when not using --list-fields");
  print();
  usage();
  sys.exit( 1 );

f = fcp.FCPNode( host = host, port = port );
entry = f.refstats( WithVolatile = True );
f.shutdown();
if( list_fields_flag ):
  keys = list(entry.keys());
  keys.sort();
  print("Volatile fields:");
  for key in keys:
    if( not key.startswith( "volatile." )):
      continue;
    print(key[ 9: ]);
  print();
  print("non-volatile fields:")
  for key in keys:
    if( key.startswith( "volatile." )):
      continue;
    print(key);
else:
  field_count = 0;
  sys.stdout.write( "N" );
  for stat_field in stat_fields:
    try:
      datum_string = entry[ "volatile." + stat_field ];
    except KeyError as msg:
      try:
        datum_string = entry[ stat_field ];
      except KeyError as msg:
        datum_string = "0";
    field_count += 1;
    if( "true" == datum_string ):
      datum = 1.0;
    elif( "false" == datum_string ):
      datum = 0.0;
    else:
      datum = float( datum_string );
      try:
        test_datum = int( datum );
      except ValueError as msg:
        test_datum = None;
      if( test_datum == datum ):
        datum = test_datum;
    sys.stdout.write( ":%s" % ( datum ));
  sys.stdout.write( "\n" );
  sys.stdout.flush();
