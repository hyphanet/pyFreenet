#!/usr/bin/env python
"""
fcpput - a simple command-line program for freenet key insertion
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
    sys.stderr.write("Usage: %s [options] key_uri [filename]\n" % progname)
    sys.stderr.write("Type '%s -h' for help\n" % progname)
    sys.exit(ret)

def help():
    """
    print help options, then exit
    """
    print "%s: a simple command-line freenet key insertion command" % progname
    print "Usage: %s [options] key_uri [<filename>]" % progname
    print
    print "Arguments:"
    print "  <key_uri>"
    print "     A freenet key URI, such as 'freenet:KSK@gpl.txt'"
    print "     Note that the 'freenet:' part may be omitted if you feel lazy"
    print "  <filename>"
    print "     The filename from which to source the key's data. If this filename"
    print "     is '-', or is not given, then the data will be sourced from"
    print "     standard input"
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
    print "  -m, --mimetype=<mimetype>"
    print "     The mimetype under which to insert the key. If not given, then"
    print "     an attempt will be made to guess it from the filename. If no"
    print "     filename is given, or if this attempt fails, the mimetype"
    print "     'text/plain' will be used as a fallback"
    print "  -p, --persistence="
    print "     Set the persistence type, one of 'connection', 'reboot' or 'forever'"
    print "  -g, --global"
    print "     Do it on the FCP global queue"
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
            "persistence" : "connection",
            }

    # process command line switches
    try:
        cmdopts, args = getopt.getopt(
            sys.argv[1:],
            "?hvH:P:m:gp:",
            ["help", "verbose", "fcpHost=", "fcpPort=", "mimetype=", "global",
             "persistence=",
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

        if o in ("-m", "--mimetype"):
            mimetype = a

        if o in ("-p", "--persistence"):
            if a not in ("connection", "reboot", "forever"):
                usage("Persistence must be one of 'connection', 'reboot', 'forever'")
            opts['Persistence'] = a

        if o in ("-g", "--global"):
            opts['Global'] = "true"

    # process args    
    nargs = len(args)
    if nargs < 1 or nargs > 2:
        usage("Invalid number of arguments")
    
    uri = args[0]
    if not uri.startswith("freenet:"):
        uri = "freenet:" + uri

    # determine where to get input
    if nargs == 1 or args[1] == '-':
        infile = None
    else:
        infile = args[1]

    # figure out a mimetype if none present
    if infile and not mimetype:
        base, ext = os.path.splitext(infile)
        if ext:
            mimetype = mimetypes.guess_type(ext)[0]

    if mimetype:
        # mimetype explicitly specified, or implied with input file,
        # stick it in.
        # otherwise, let FCPNode.put try to imply it from a uri's
        # 'file extension' suffix
        opts['mimetype'] = mimetype

    # try to create the node
    try:
        node = fcp.FCPNode(host=fcpHost, port=fcpPort, verbosity=verbosity,
                           logfile=sys.stderr)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        usage("Failed to connect to FCP service at %s:%s" % (fcpHost, fcpPort))

    # grab the data
    if not infile:
        data = sys.stdin.read()
    else:
        try:
            data = file(infile, "rb").read()
        except:
            node.shutdown()
            usage("Failed to read input from file %s" % repr(infile))

    # try to insert the key
    try:
        print "opts=%s" % str(opts)
        uri = node.put(uri, data=data, **opts)
        node.shutdown()
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        node.shutdown()
        sys.stderr.write("%s: Failed to insert key %s\n" % (progname, repr(uri)))
        sys.exit(1)

    # successful, return the uri
    sys.stdout.write(uri)
    sys.stdout.flush()

    # all done
    sys.exit(0)

if __name__ == '__main__':
    main()

