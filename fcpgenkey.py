#!/usr/bin/env python
"""
fcpgenkey - a simple command-line program for freenet keypair generation
"""
import sys, os, getopt, traceback, mimetypes

import fcp

argv = sys.argv
argc = len(argv)
progname = argv[0]

def usage(msg=None, ret=1):
    """
    Prints usage message then exits
    """
    if msg:
        sys.stderr.write(msg+"\n")
    sys.stderr.write("Usage: %s [options]\n" % progname)
    sys.stderr.write("Type '%s -h' for help\n" % progname)
    sys.exit(ret)

def help():
    """
    print help options, then exit
    """
    print "%s: a simple command-line freenet keypair"  % progname
    print "generation command"
    print
    print "Generates a simple SSK keypair, and prints"
    print "public key, then private key, each on its own line"
    print
    print "Usage: %s [options]" % progname
    print
    print "Options:"
    print "  -h, -?, --help"
    print "     Print this help message"
    print "  -v, --verbose"
    print "     Print verbose progress messages to stderr"
    print "  -H, --fcpHost=<hostname>"
    print "     Connect to FCP service at host <hostname>"
    print "  -P, --fcpPort=<portnum>"
    print "     Connect to FCP service at port <portnum>"
    print
    print "Environment:"
    print "  Instead of specifying -H and/or -P, you can define the environment"
    print "  variables FCP_HOST and/or FCP_PORT respectively"

    sys.exit(0)

def main():
    """
    Front end for fcpget utility
    """
    # default job options
    verbosity = fcp.ERROR
    verbose = False
    fcpHost = fcp.node.defaultFCPHost
    fcpPort = fcp.node.defaultFCPPort
    mimetype = None

    opts = {
            "Verbosity" : 0,
            }

    # process command line switches
    try:
        cmdopts, args = getopt.getopt(
            sys.argv[1:],
            "?hvH:P:",
            ["help", "verbose", "fcpHost=", "fcpPort=",
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

        if o in ("-v", "--verbosity"):
            verbosity = fcp.node.DETAIL
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
        node = fcp.FCPNode(host=fcpHost, port=fcpPort, verbosity=verbosity,
                           logfile=sys.stderr)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        usage("Failed to connect to FCP service at %s:%s" % (fcpHost, fcpPort))

    # grab the keypair
    pub, priv = node.genkey()

    node.shutdown()

    # successful, return the uri
    print pub
    print priv

    # all done
    sys.exit(0)

if __name__ == '__main__':
    main()

