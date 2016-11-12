#@+leo-ver=4
#@+node:@file put.py
"""
put a key

This is the guts of the command-line front-end app fcpput
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
    sys.stderr.write("Usage: %s [options] key_uri [filename]\n" % progname)
    sys.stderr.write("Type '%s -h' for help\n" % progname)
    sys.exit(ret)

#@-node:usage
#@+node:help
def help():
    """
    print help options, then exit
    """
    print("%s: a simple command-line freenet key insertion command" % progname)
    print("Usage: %s [options] key_uri [<filename>]" % progname)
    print()
    print("Arguments:")
    print("  <key_uri>")
    print("     A freenet key URI, such as 'freenet:KSK@gpl.txt'")
    print("     Note that the 'freenet:' part may be omitted if you feel lazy")
    print("  <filename>")
    print("     The filename from which to source the key's data. If this filename")
    print("     is '-', or is not given, then the data will be sourced from")
    print("     standard input")
    print()
    print("Options:")
    print("  -h, -?, --help")
    print("     Print this help message")
    print("  -v, --verbose")
    print("     Print verbose progress messages to stderr, do -v twice for more detail")
    print("  -H, --fcpHost=<hostname>")
    print("     Connect to FCP service at host <hostname>")
    print("  -P, --fcpPort=<portnum>")
    print("     Connect to FCP service at port <portnum>")
    print("  -m, --mimetype=<mimetype>")
    print("     The mimetype under which to insert the key. If not given, then")
    print("     an attempt will be made to guess it from the filename. If no")
    print("     filename is given, or if this attempt fails, the mimetype")
    print("     'text/plain' will be used as a fallback")
    print("  -c, --compress")
    print("     Enable compression of inserted data (default is no compression)")
    print("  -d, --disk")
    print("     Try to have the node access file on disk directly , it will try then a fallback is provided")
    print("     nb:give the path relative to node filesystem not from where you're running this program")
    print("  -p, --persistence=")
    print("     Set the persistence type, one of 'connection', 'reboot' or 'forever'")
    print("  -g, --global")
    print("     Do it on the FCP global queue")
    print("  -n, --nowait")
    print("     Don't wait for completion, exit immediately")
    print("  -r, --priority")
    print("     Set the priority (0 highest, 6 lowest, default 3)")
    print("  -t, --timeout=")
    print("     Set the timeout, in seconds, for completion. Default one year")
    print("  -V, --version")
    print("     Print version number and exit")
    print()
    print("Environment:")
    print("  Instead of specifying -H and/or -P, you can define the environment")
    print("  variables FCP_HOST and/or FCP_PORT respectively")


#@-node:help
#@+node:main
def main():
    """
    Front end for fcpput utility
    """
    # default job options
    verbosity = node.ERROR
    verbose = False
    fcpHost = node.defaultFCPHost
    fcpPort = node.defaultFCPPort
    mimetype = None
    nowait = False

    opts = {
            "Verbosity" : 0,
            "persistence" : "connection",
            "async" : False,
            "priority" : 3,
            "MaxRetries" : -1,
           }

    # process command line switches
    try:
        cmdopts, args = getopt.getopt(
            sys.argv[1:],
            "?hvH:P:m:gcdp:nr:t:V",
            ["help", "verbose", "fcpHost=", "fcpPort=", "mimetype=", "global","compress","disk",
             "persistence=", "nowait",
             "priority=", "timeout=", "version",
             ]
            )
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    output = None
    verbose = False
    #print cmdopts

    makeDDARequest=False
    opts['nocompress'] = True

    for o, a in cmdopts:
        if o in ("-V", "--version"):
            print("This is %s, version %s" % (progname, node.fcpVersion))
            sys.exit(0)

        elif o in ("-?", "-h", "--help"):
            help()
            sys.exit(0)

        elif o in ("-v", "--verbosity"):
            if verbosity < node.DETAIL:
                verbosity = node.DETAIL
            else:
                verbosity += 1
            opts['Verbosity'] = 1023
            verbose = True

        elif o in ("-H", "--fcpHost"):
            fcpHost = a

        elif o in ("-P", "--fcpPort"):
            try:
                fcpPort = int(a)
            except:
                usage("Invalid fcpPort argument %s" % repr(a))

        elif o in ("-m", "--mimetype"):
            mimetype = a

        elif o in ("-c", "--compress"):
            opts['nocompress'] = False

        elif o in ("-d","--disk"):
            makeDDARequest=True

        elif o in ("-p", "--persistence"):
            if a not in ("connection", "reboot", "forever"):
                usage("Persistence must be one of 'connection', 'reboot', 'forever'")
            opts['persistence'] = a

        elif o in ("-g", "--global"):
            opts['Global'] = "true"

        elif o in ("-n", "--nowait"):
            opts['async'] = True
            nowait = True

        elif o in ("-r", "--priority"):
            try:
                pri = int(a)
                if pri < 0 or pri > 6:
                    raise hell
            except:
                usage("Invalid priority '%s'" % pri)
            opts['priority'] = int(a)

        elif o in ("-t", "--timeout"):
            try:
                timeout = node.parseTime(a)
            except:
                usage("Invalid timeout '%s'" % a)
            opts['timeout'] = timeout

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
        filename = os.path.basename(infile)
        if filename:
            mimetype = mimetypes.guess_type(filename)[0]

    if mimetype:
        # mimetype explicitly specified, or implied with input file,
        # stick it in.
        # otherwise, let FCPNode.put try to imply it from a uri's
        # 'file extension' suffix
        opts['mimetype'] = mimetype

    # try to create the node
    try:
        n = node.FCPNode(host=fcpHost, port=fcpPort, verbosity=verbosity,
                        logfile=sys.stderr)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        usage("Failed to connect to FCP service at %s:%s" % (fcpHost, fcpPort))


    TestDDARequest = False

    if makeDDARequest:
        if infile is not None:
            ddareq = {}
            ddafile = os.path.abspath(infile)

            ddareq["Directory"] = os.path.dirname(ddafile)
            ddareq["WantReadDirectory"] = True
            ddareq["WantWriteDirectory"] = False
            print("Absolute filepath used for node direct disk access :",ddareq["Directory"])
            print("File to insert :",os.path.basename(ddafile))
            TestDDARequest = n.testDDA(**ddareq)
            print("Result of dda request :", TestDDARequest)

            if TestDDARequest:
                opts["file"] = ddafile
                uri = n.put(uri,**opts)
            else:
                sys.stderr.write("%s: disk access failed to insert file %s fallback to direct\n" % (progname,ddafile) )
        else:
            sys.stderr.write("%s: disk access need a disk filename\n" % progname )

    # try to insert the key using "direct" way if dda has failed
    if not TestDDARequest:
        # grab the data
        if not infile:
            data = sys.stdin.read()
            # Encode data as bytes.
            data = data.encode('utf-8')
        else:
            try:
                data = open(infile, "rb").read()
            except:
                n.shutdown()
                usage("Failed to read input from file %s" % repr(infile))

        try:
            #print "opts=%s" % str(opts)
            uri = n.put(uri, data=data, **opts)
        except:
            if verbose:
                traceback.print_exc(file=sys.stderr)
            n.shutdown()
            sys.stderr.write("%s: Failed to insert key %s\n" % (progname, repr(uri)))
            sys.exit(1)

        if nowait:
            # got back a job ticket, wait till it has been sent
            uri.waitTillReqSent()
        else:
            # successful, return the uri
            sys.stdout.write(uri)
            sys.stdout.flush()

    n.shutdown()

    # all done
    sys.exit(0)

#@-node:main
#@-others

#@-node:@file put.py
#@-leo
