#@+leo-ver=4
#@+node:@file get.py
"""
get a key

This is the guts of the command-line front-end app fcpget
"""

#@+others
#@+node:imports
import argparse
import sys, traceback

from . import node
from .arguments import add_default_arguments

#@-node:imports
#@+node:globals
progname = sys.argv[0]

#@-node:globals

def create_parser():
    '''
    Creates an argparse parser.
    '''
    parser = argparse.ArgumentParser(
        prog='fcpget',
        description='A simple command-line freenet key retrieval command'
    )
    add_default_arguments(parser)

    parser.add_argument(
        'key_uri',
        help='''
            A freenet key URI, such as 'freenet:KSK@gpl.txt'.
            Note that the 'freenet:' part may be omitted if you feel lazy
        ''',
    )

    parser.add_argument(
        'outfile',
        nargs='?',
        type=argparse.FileType('wb'),
        default=sys.stdout.buffer,
        help='''
        The filename to which to write the key's data.
        If this argument is not given, the key's data will be
        printed to standard output.
        ''',
    )

    parser.add_argument(
        '--priority',
        '-r',
        type=int,
        choices=list(range(0, 6+1)),
        default=3,
        help='Set the priority (0 highest, 6 lowest, default 3)',
    )

    parser.add_argument(
        '--global',
        '-g',
        dest='global_queue',
        default=False,
        action='store_true',
        help='Do it on the FCP global queue.',
    )

    parser.add_argument(
        '--persistence',
        '-p',
        default='connection',
        choices=('connection', 'reboot', 'forever'),
        help='Set the persistence type, one of "connection", "reboot" or "forever"',
    )


    return parser



#@-node:help
#@+node:main
def main(argv=sys.argv[1:]):
    """
    Front end for fcpget utility
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # default job options
    verbose = len(args.verbose) > 0
    verbosity = node.ERROR + sum(args.verbose)

    opts = {
            "Verbosity" : (7 if not verbose else 1023),
            }


    uri = args.key_uri
    if not uri.startswith("freenet:"):
        uri = "freenet:" + uri

    opts['priority'] = args.priority
    if args.global_queue:
        opts['Global'] = 'true'
    opts['persistence'] = args.persistence
    opts['timeout'] = args.timeout

    # try to create the node
    try:
        fcp_node = node.FCPNode(host=args.fcpHost,
                         port=args.fcpPort,
                         Global=args.global_queue,
                         verbosity=verbosity,
                         logfile=sys.stderr)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        sys.stderr.write("Failed to connect to FCP service at %s:%s\n" % (args.fcpHost, args.fcpPort))
        sys.exit(1)

    # try to retrieve the key
    try:
        # print "opts=%s" % opts
        mimetype, data, msg = fcp_node.get(uri, **opts)
        fcp_node.shutdown()
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        sys.stderr.write("%s: Failed to retrieve key %s\n" % (progname, repr(uri)))
        fcp_node.shutdown()
        sys.exit(1)

    # try to dispose of the data

    # try to save to file
    try:
        args.outfile.write(data)
        args.outfile.close()
        if verbose:
            sys.stderr.write("Saved key to file %s\n" % args.outfile)
    except:
        # save failed
        if verbose:
            traceback.print_exc(file=sys.stderr)
        sys.stderr.write("Failed to write data to output file %s\n" % repr(args.outfile))

    # all done
    try:
        fcp_node.shutdown()
    except:
        pass
    sys.exit(0)

#@-node:main
#@-others

#@-node:@file get.py
#@-leo
