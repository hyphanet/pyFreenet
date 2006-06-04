#!/usr/bin/env python
"""
fcpget - a simple command-line program for freenet key retrieval
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
    print "%s: a simple command-line freenet key retrieval command" % progname
    print "Usage: %s [options] key_uri [<filename>]" % progname
    print
    print "Arguments:"
    print "  <key_uri>"
    print "     A freenet key URI, such as 'freenet:KSK@gpl.txt'"
    print "     Note that the 'freenet:' part may be omitted if you feel lazy"
    print "  <filename>"
    print "     The filename to which to write the key's data. Note that if"
    print "     this filename has no extension (eg .txt), a file extension"
    print "     will be guessed based on the key's returned mimetype."
    print "     If this argument is not given, the key's data will be"
    print "     printed to standard output"
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
    Global = False

    opts = {
            "Verbosity" : 0,
            "Persistence" : "connection",
            }

    # process command line switches
    try:
        cmdopts, args = getopt.getopt(
            sys.argv[1:],
            "?hvH:P:g",
            ["help", "verbose", "fcpHost=", "fcpPort=", "global", "persistence=",
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

    # determine where to put output
    if nargs == 1:
        outfile = None
    else:
        outfile = args[1]

    # try to create the node
    try:
        node = fcp.FCPNode(host=fcpHost,
                           port=fcpPort,
                           verbosity=verbosity,
                           Global=Global,
                           logfile=sys.stderr)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        usage("Failed to connect to FCP service at %s:%s" % (fcpHost, fcpPort))

    # try to retrieve the key
    try:
        mimetype, data = node.get(uri, **opts)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        node.shutdown()
        sys.stderr.write("%s: Failed to retrieve key %s\n" % (progname, repr(uri)))
        sys.exit(1)

    node.shutdown()

    # try to dispose of the data
    if outfile:
        # figure out an extension, if none given
        base, ext = os.path.splitext(outfile)
        if not ext:
            ext = mimetypes.guess_extension(mimetype)
            if not ext:
                ext = ""
            outfile = base + ext

        # try to save to file
        try:           
            f = file(outfile, "wb")
            f.write(data)
            f.close()
            if verbose:
                sys.stderr.write("Saved key to file %s\n" % outfile)
        except:
            # save failed
            if verbose:
                traceback.print_exc(file=sys.stderr)
            usage("Failed to write data to output file %s" % repr(outfile))
    else:
        # no output file given, dump to stdout
        sys.stdout.write(data)
        sys.stdout.flush()

    # all done
    sys.exit(0)

if __name__ == '__main__':
    main()

