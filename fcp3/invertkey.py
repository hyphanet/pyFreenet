#@+leo-ver=4
#@+node:@file invertkey.py
"""
invert an SSK/USK private key to its public equivalent

This is the guts of the command-line front-end app fcpinvertkey
"""

#@+others
#@+node:imports
import argparse
import sys
import traceback

from . import node
from .arguments import add_default_arguments

#@-node:imports
#@+node:create_parser
def create_parser():
    '''
    Creates an argparse parser.
    '''
    parser = argparse.ArgumentParser(
        prog='fcpinvertkey',
        description='Convert a freenet SSK/USK private URI into its public equivalent.'
    )
    add_default_arguments(parser)

    parser.add_argument(
        'uri',
        nargs='?',
        help='''
            A freenet SSK/USK private URI
        ''',
    )

    return parser

#@-node:create_parser
#@+node:main
def main():
    """
    Front end for fcpget utility
    """
    parser = create_parser()
    args = parser.parse_args()

    # default job options
    verbose = len(args.verbose) > 0
    verbosity = node.ERROR + sum(args.verbose)

    # try to create the node
    try:
        n = node.FCPNode(host=args.fcpHost, port=args.fcpPort, verbosity=verbosity,
                         logfile=sys.stderr)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        sys.stderr.write("Failed to connect to FCP service at %s:%s\n" % (args.fcpHost, args.fcpPort))

    # determine the uri
    if not args.uri:
        args.uri = input('Enter a URI: ')

    uri = args.uri.strip()

    # do the invert
    uriPub = n.invertprivate(args.uri)

    n.shutdown()

    # successful, return the uri
    sys.stdout.write(uriPub)
    sys.stdout.flush()

    # all done
    sys.exit(0)

#@-node:main
#@-others

#@-node:@file invertkey.py
#@-leo
