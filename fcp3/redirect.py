#@+leo-ver=4
#@+node:@file redirect.py
"""
Insert a redirect from a uri to an existing URI

This is the guts of the command-line front-end app fcpredirect

Example usage:

$ fcpredirect KSK@darknet USK@PFeLTa1si2Ml5sDeUy7eDhPso6TPdmw-2gWfQ4Jg02w,3ocfrqgUMVWA2PeorZx40TW0c-FiIOL-TWKQHoDbVdE,AQABAAE/Index/35/

Inserts key 'KSK@darknet', as a redirect to the 'darknet index' freesite
"""

#@+others
#@+node:imports
import sys, os, getopt, traceback, mimetypes

from . import node

#@-node:imports
#@+node:globals
progname = sys.argv[0]

#@-node:globals
#@+node:usage
def usage(msg=None, ret=1):
    """
    Prints usage message then exits
    """
    if msg:
        sys.stderr.write(msg+"\n")
    sys.stderr.write("Usage: %s [options] src-uri target-uri\n" % progname)
    sys.stderr.write("Type '%s -h' for help\n" % progname)
    sys.exit(ret)

#@-node:usage
#@+node:help
def help():
    """
    print help options, then exit
    """
    print("%s: inserts a key, as a redirect to another key"  % progname)
    print()
    print("Usage: %s [options] src-uri target-uri" % progname)
    print()
    print("Options:")
    print("  -h, -?, --help")
    print("     Print this help message")
    print("  -v, --verbose")
    print("     Print verbose progress messages to stderr")
    print("  -H, --fcpHost=<hostname>")
    print("     Connect to FCP service at host <hostname>")
    print("  -P, --fcpPort=<portnum>")
    print("     Connect to FCP service at port <portnum>")
    print("  -V, --version")
    print("     Print version number and exit")
    print()
    print("Example:")
    print("  %s KSK@foo KSK@bar" % progname)
    print("    Inserts key KSK@foo, which when retrieved will redirect to KSK@bar")
    print("    Prints resulting URI (in this case KSK@foo) to stdout")
    print()
    print("Environment:")
    print("  Instead of specifying -H and/or -P, you can define the environment")
    print("  variables FCP_HOST and/or FCP_PORT respectively")

    sys.exit(0)

#@-node:help
#@+node:main
def main():
    """
    Front end for fcpget utility
    """
    # default job options
    verbosity = node.ERROR
    verbose = False
    fcpHost = node.defaultFCPHost
    fcpPort = node.defaultFCPPort

    opts = {
            "Verbosity" : 0,
            }

    # process command line switches
    try:
        cmdopts, args = getopt.getopt(
            sys.argv[1:],
            "?hvH:P:V",
            ["help", "verbose", "fcpHost=", "fcpPort=", "version",
             ]
            )
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    output = None
    verbose = False
    #print cmdopts
    for o, a in cmdopts:

        if o in ("-?", "-h", "--help"):
            help()

        if o in ("-V", "--version"):
            print("This is %s, version %s" % (progname, node.fcpVersion))
            sys.exit(0)

        if o in ("-v", "--verbosity"):
            verbosity = node.DETAIL
            opts['Verbosity'] = 1023
            verbose = True

        if o in ("-H", "--fcpHost"):
            fcpHost = a
        
        if o in ("-P", "--fcpPort"):
            try:
                fcpPort = int(a)
            except:
                usage("Invalid fcpPort argument %s" % repr(a))

    # try to create the node
    try:
        n = node.FCPNode(host=fcpHost, port=fcpPort, verbosity=verbosity,
                         logfile=sys.stderr)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        usage("Failed to connect to FCP service at %s:%s" % (fcpHost, fcpPort))

    # determine the uris
    if len(args) != 2:
        usage("Invalid number of arguments")
    uriSrc = args[0].strip()
    uriDest = args[1].strip()
    
    # do the invert
    uriPub = n.redirect(uriSrc, uriDest)

    n.shutdown()

    # successful, return the uri
    sys.stdout.write(uriPub)
    sys.stdout.flush()

    # all done
    sys.exit(0)

#@-node:main
#@-others

#@-node:@file redirect.py
#@-leo
