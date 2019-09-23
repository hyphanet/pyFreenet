"""
Upload a file.

This is the guts of the command-line front-end app fcpupload.

It is adapted from put.py, just with nicer defaults and feedback.
"""

import sys, os, getopt, traceback, mimetypes, argparse, logging

from . import node

import freenet3 as freenet

progname = sys.argv[0]

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
    # TODO: Switch to argparse. That would save at least half the file.
    print("\n".join(("%s: a simple command-line freenet key insertion command" % progname,
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
                     "  variables FCP_HOST and/or FCP_PORT respectively")))


def parse_args():
    parser = argparse.ArgumentParser("a simple command-line freenet key insertion command")
    parser.add_argument("files", metavar="FILE", nargs="+",
                        help="")
    parser.add_argument("-w", "--wait", action="store_true",
                        help="wait for completion")
    parser.add_argument("--spawn", action="store_true",
                        help="if no node is available, automatically spawn one. Only works on GNU/Linux right now")
    parser.add_argument("-e", "--realtime", action="store_true",
                        help="Use the realtime queue (fast for small files)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="activate progress messages to stderr")
    parser.add_argument("-V", "--version", action="store_true",
                        help="activate progress messages to stderr")
    parser.add_argument("-H", "--fcpHost", metavar="hostname", default=node.defaultFCPHost,
                        help="Connect to FCP service at the given host")
    parser.add_argument("-P", "--fcpPort", metavar="portnum", default=node.defaultFCPPort,
                        help="Connect to FCP service at the given port")
    parser.add_argument("-p", "--priority", type=int, default=3,
                        help="Set the priority (highest reasonable: 1, lowest: 6, default: 3)")
    parser.add_argument("-m", "--mimetype", metavar="MIMETYPE", default=None,
                        help="The mimetype under which to insert the key. If not given, then an attempt will be made to guess it from the filename. If no filename is given, or if this attempt fails, the mimetype 'text/plain' will be used as a fallback")
    
    
    
    return parser.parse_args()
    
def main():
    """
    Front end for fcpput utility
    """
    args = parse_args()
    if args.version:
        print("This is %s, version %s" % (progname, node.fcpVersion))
        sys.exit(0)

    # spawning requires waiting
    if args.spawn:
        args.wait = args.spawn
    spawned = False
    
    # default job options

    verbosity = (0 if not args.verbose else 6)
    opts = {
        "Verbosity": verbosity,
        "persistence": "forever",
        "priority": args.priority,
        "async": not args.wait,
        "Global": "true",
        "MaxRetries": -1,
    }

    makeDDARequest=True

    nargs = len(args.files)
    if nargs < 1 or nargs > 2:
        usage("Invalid number of arguments")

    keytypes = ["USK", "KSK", "SSK", "CHK"]
    if nargs == 2:
        infile = args.files[1]
        uri = args.files[0]
        if not uri.startswith("freenet:"):
            uri = "freenet:" + uri
        if not uri[len("freenet:"):len("freenet:")+3] in keytypes:
            print(uri, uri[len("freenet:"):len("freenet:")+4])
            usage("The first argument must be a key. Example: CHK@/<filename>")
    else:
        # if no infile is given, automatically upload to a CHK key.
        infile = args.files[0]
        uri = "freenet:CHK@/" + node.toUrlsafe(infile)
        
    # if we got an infile, but the key does not have the filename, use that filename for the uri.
    if infile and uri[-2:] == "@/" and uri[:3] in keytypes:
        uri += node.toUrlsafe(infile)


    # figure out a mimetype if none present
    mimetype = args.mimetype
    if infile and mimetype is None:
        base, ext = os.path.splitext(infile)
        if ext:
            mimetype = mimetypes.guess_type(ext)[0]

    if mimetype:
        # mimetype explicitly specified, or implied with input file,
        # stick it in.
        # otherwise, let FCPNode.put try to imply it from a uri's
        # 'file extension' suffix
        opts['mimetype'] = mimetype

    # spawn a node
    if args.spawn:
        try: # first check if there is already a working node on the fcp port
            with node.FCPNode(port=args.fcpPort) as n:
                n.shutdown() # close the fcp connection
        except ConnectionRefusedError:
            freenet.spawn.spawn_node(args.fcpPort)
            spawned = True # need to teardown the node afterwards
        
    # try to create the node
    try:
        n = node.FCPNode(host=args.fcpHost, port=args.fcpPort, verbosity=verbosity,
                        logfile=sys.stderr)
    except:
        if args.verbose:
            traceback.print_exc(file=sys.stderr)
        usage("Failed to connect to FCP service at %s:%s" % (args.fcpHost, args.fcpPort))

    TestDDARequest = False

    #: The key of the uploaded file.
    freenet_uri = None
    
    if makeDDARequest:
        if infile is not None:
            ddareq = {}
            ddafile = os.path.abspath(infile)
            ddareq["Directory"] = os.path.dirname(ddafile)
            ddareq["WantReadDirectory"] = True
            ddareq["WantWriteDirectory"] = False
            logging.info("Absolute filepath for node direct disk access: %s",
                         ddareq["Directory"])
            logging.info("File to insert: %s", os.path.basename(ddafile))
            TestDDARequest = n.testDDA(**ddareq)

    if TestDDARequest:
        opts["file"] = ddafile # ddafile=abspath(infile)
    else:
        # try to insert the key using "direct" way if dda has failed
        sys.stderr.write("%s: disk access failed to insert file %s fallback to direct\n" % (progname,ddafile) )
        # grab the data
        if not infile:
            data = sys.stdin.read()
            # Encode data
            data = data.encode('utf-8')
        else:
            try:
                data = open(infile, "rb").read()
            except:
                n.shutdown()
                usage("Failed to read input from file %s" % repr(infile))

        # print "opts=%s" % str(opts)
        opts["data"] = data
        n.listenGlobal()

    try:
        putres = n.put(uri, **opts)
    except Exception:
        if args.verbose:
            traceback.print_exc(file=sys.stderr)
        sys.stderr.write("%s: Failed to insert key %s\n" % (
            progname, repr(uri)))
        n.shutdown()
        sys.exit(1)        
    except:
        if args.verbose:
            traceback.print_exc(file=sys.stderr)
        n.shutdown()
        sys.exit(1)        

    
    if args.wait:
        # successful, return the uri
        print(putres)
    else:
        # got back a job ticket, wait till it has been sent
        putres.waitTillReqSent()
        # generate the CHK if we do not wait for completion
        opts["chkonly"] = True
        opts["async"] = False
        # force the node to be fast
        opts["priority"] = 0
        opts["realtime"] = True
        opts["persistence"] = "connection"
        opts["Global"] = False
        freenet_uri = n.put(uri,**opts)
        print(freenet_uri)

    n.shutdown()

    if spawned:
        freenet.spawn.teardown_node(args.fcpPort)
        
    # all done
    sys.exit(0)
