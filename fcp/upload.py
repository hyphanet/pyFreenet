#@+leo-ver=4
#@+node:@file put.py
"""
Upload a file.

This is the guts of the command-line front-end app fcpupload.

It is adapted from put.py, just with nicer defaults and feedback.
"""

#@+others
#@+node:imports
import sys, os, getopt, traceback, mimetypes

import node

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
    # TODO: Switch to argparse. That would save at least half the file.
    print "\n".join(("%s: a simple command-line freenet key insertion command" % progname,
                     "Usage: %s [options] <filename>" % progname,
                     "",
                     "Arguments:",
                     "  <key_uri>",
                     "     A freenet key URI, such as 'freenet:KSK@gpl.txt'",
                     "     Note that the 'freenet:' part may be omitted if you feel lazy",
                     "  <filename>",
                     "     The filename from which to source the key's data. If this filename",
                     "     is '-', or is not given, then the data will be sourced from",
                     "     standard input",
                     "",
                     "Options:",
                     "  -h, -?, --help",
                     "     Print this help message",
                     "  -v, --verbose",
                     "     Print verbose progress messages to stderr, do -v twice for more detail",
                     "  -H, --fcpHost=<hostname>",
                     "     Connect to FCP service at host <hostname>",
                     "  -P, --fcpPort=<portnum>",
                     "     Connect to FCP service at port <portnum>",
                     "  -m, --mimetype=<mimetype>",
                     "     The mimetype under which to insert the key. If not given, then",
                     "     an attempt will be made to guess it from the filename. If no",
                     "     filename is given, or if this attempt fails, the mimetype",
                     "     'text/plain' will be used as a fallback",
                     "  -c, --compress",
                     "     Enable compression of inserted data (default is no compression)",
                     "  -d, --disk",
                     "     Try to have the node access file on disk directly , it will try then a fallback is provided",
                     "     nb:give the path relative to node filesystem not from where you're running this program",
                     "        For the direct access to succeed, the absolute path seen by the node and by this script must be the same",
                     "  -p, --persistence=",
                     "     Set the persistence type, one of 'connection', 'reboot' or 'forever'",
                     "  -g, --global",
                     "     Do it on the FCP global queue",
                     "  -w, --wait",
                     "     Wait for completion",
                     "  -r, --priority",
                     "     Set the priority (0 highest, 6 lowest, default 3)",
                     "  -e, --realtime",
                     "     Use the realtime queue (fast for small files)",
                     "  -t, --timeout=",
                     "     Set the timeout, in seconds, for completion. Default one year",
                     "  -V, --version",
                     "     Print version number and exit",
                     "",
                     "Environment:",
                     "  Instead of specifying -H and/or -P, you can define the environment",
                     "  variables FCP_HOST and/or FCP_PORT respectively"))


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
    wait = False

    opts = {
            "Verbosity" : 0,
            "persistence" : "forever",
            "async" : True,
            "priority" : 3,
            "Global": "true",
            "MaxRetries" : -1,
           }

    # process command line switches
    try:
        cmdopts, args = getopt.getopt(
            sys.argv[1:],
            "?hvH:P:m:gcdp:wr:et:V",
            ["help", "verbose", "fcpHost=", "fcpPort=", "mimetype=", "global","compress","disk",
             "persistence=", "wait",
             "priority=", "realtime", "timeout=", "version",
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
            print "This is %s, version %s" % (progname, node.fcpVersion)
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

        elif o in ("-w", "--wait"):
            opts['async'] = False
            wait = True

        elif o in ("-r", "--priority"):
            try:
                pri = int(a)
                if pri < 0 or pri > 6:
                    raise hell
            except:
                usage("Invalid priority '%s'" % pri)
            opts['priority'] = int(a)

        elif o in ("-e", "--realtime"):
            opts['realtime'] = True

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

    keytypes = ["USK", "KSK", "SSK", "CHK"]
    if nargs == 2:
        infile = args[1]
        uri = args[0]
        if not uri.startswith("freenet:"):
            uri = "freenet:" + uri
        if not uri[len("freenet:"):len("freenet:")+3] in keytypes:
            print uri, uri[len("freenet:"):len("freenet:")+4]
            usage("The first argument must be a key. Example: CHK@/<filename>")
    else:
        # if no infile is given, automatically upload to a CHK key.
        infile = args[0]
        uri = "freenet:CHK@/" + node.toUrlsafe(infile)
        
    # if we got an infile, but the key does not have the filename, use that filename for the uri.
    if infile and uri[-2:] == "@/" and uri[:3] in keytypes:
        uri += node.toUrlsafe(infile)


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
        n = node.FCPNode(host=fcpHost, port=fcpPort, verbosity=verbosity,
                        logfile=sys.stderr)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        usage("Failed to connect to FCP service at %s:%s" % (fcpHost, fcpPort))

    # FIXME: Throw out all the TestDDARequest stuff. It is not needed for putting a single file.
    TestDDARequest=False

    #: The key of the uploaded file.
    freenet_uri = None
    
    if makeDDARequest:
        if infile is not None:
            ddareq=dict()
            ddafile = os.path.abspath(infile)
            ddareq["Directory"]= os.path.dirname(ddafile)
            # FIXME: This does not work. The only reason why testDDA
            # works is because there is an alternate way of specifying
            # a content hash, and that way works.
            ddareq["WantReadDirectory"]="True"
            ddareq["WantWriteDirectory"]="false"
            print "Absolute filepath used for node direct disk access :",ddareq["Directory"]
            print "File to insert :",os.path.basename( ddafile )
            TestDDARequest=n.testDDA(**ddareq)

            if TestDDARequest:
                opts["file"]=ddafile
                putres = n.put(uri,**opts)
            else:
                sys.stderr.write("%s: disk access failed to insert file %s fallback to direct\n" % (progname,ddafile) )
        else:
            sys.stderr.write("%s: disk access needs a disk filename\n" % progname )

    # try to insert the key using "direct" way if dda has failed
    if not TestDDARequest:
        # grab the data
        if not infile:
            data = sys.stdin.read()
        else:
            try:
                data = file(infile, "rb").read()
            except:
                n.shutdown()
                usage("Failed to read input from file %s" % repr(infile))

        try:
            #print "opts=%s" % str(opts)
            # give it the file anyway: Put is more intelligent than this script.
            opts["data"] = data
            if infile:
                opts["file"] = infile
            n.listenGlobal()
            putres = n.put(uri, **opts)
            if not wait:
                opts["chkonly"] = True
                opts["async"] = False
                # force the node to be fast
                opts["priority"] = 0
                opts["realtime"] = True
                opts["persistence"] = "connection"
                opts["Global"] = False
                freenet_uri = n.put(uri,**opts)

        except:
            if verbose:
                traceback.print_exc(file=sys.stderr)
            n.shutdown()
            sys.stderr.write("%s: Failed to insert key %s\n" % (progname, repr(uri)))
            sys.exit(1)

        if not wait:
            # got back a job ticket, wait till it has been sent
            putres.waitTillReqSent()
        else:
            # successful, return the uri
            sys.stdout.write(putres)
            sys.stdout.flush()

    n.shutdown()

    # output the key of the file
    if not wait:
        print freenet_uri
    # all done
    sys.exit(0)

#@-node:main
#@-others

#@-node:@file put.py
#@-leo
