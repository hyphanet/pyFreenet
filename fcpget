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
    print "     Print verbose progress messages to stderr, do -v twice for more detail"
    print "  -H, --fcpHost=<hostname>"
    print "     Connect to FCP service at host <hostname>"
    print "  -P, --fcpPort=<portnum>"
    print "     Connect to FCP service at port <portnum>"
    print "  -p, --persistence="
    print "     Set the persistence type, one of 'connection', 'reboot' or 'forever'"
    print "  -g, --global"
    print "     Do it on the FCP global queue"
    print "  -r, --priority"
    print "     Set the priority (0 highest, 6 lowest, default 3)"
    print "  -t, --timeout="
    print "     Set the timeout, in seconds, for completion. Default one year"
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
    #verbose = False
    fcpHost = fcp.node.defaultFCPHost
    fcpPort = fcp.node.defaultFCPPort
    Global = False
    verbosity = fcp.node.ERROR

    opts = {
            "Verbosity" : 0,
            "persistence" : "connection",
            "priority" : 3,
            }

    # process command line switches
    try:
        cmdopts, args = getopt.getopt(
            sys.argv[1:],
            "?hvH:P:gp:r:t:",
            ["help", "verbose", "fcpHost=", "fcpPort=", "global", "persistence=",
             "priority=", "timeout=",
             ]
            )
    except getopt.GetoptError:
        #traceback.print_exc()
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
            if verbosity < fcp.node.DETAIL:
                verbosity = fcp.node.DETAIL
            else:
                verbosity += 1
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
            opts['persistence'] = a

        if o in ("-g", "--global"):
            opts['Global'] = "true"

        if o in ("-r", "--priority"):
            try:
                pri = int(a)
                if pri < 0 or pri > 6:
                    raise hell
            except:
                usage("Invalid priority '%s'" % pri)
            opts['priority'] = int(a)

        if o in ("-t", "--timeout"):
            try:
                timeout = fcp.node.parseTime(a)
            except:
                usage("Invalid timeout '%s'" % a)
            opts['timeout'] = timeout
            
            print "timeout=%s" % timeout

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
                           Global=Global,
                           verbosity=verbosity,
                           logfile=sys.stderr)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        usage("Failed to connect to FCP service at %s:%s" % (fcpHost, fcpPort))

    # try to retrieve the key
    try:
        #print "opts=%s" % opts
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

