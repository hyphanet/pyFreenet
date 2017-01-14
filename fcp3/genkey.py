#@+leo-ver=4
#@+node:@file genkey.py
"""
generate a keypair

This is the guts of the command-line front-end app fcpgenkey
"""

#@+others
#@+node:imports
import argparse
import sys
import traceback

from . import node
from .arguments import add_default_arguments

#@-node:imports
#@+node:globals

#@-node:globals
#@+node:usage
def create_parser():
    '''
    Creates an argparse parser.
    '''
    parser = argparse.ArgumentParser(
        prog='fcpgenkey',
        description='''
            A simple command-line freenet keypair generation command.

            Generates a simple SSK keypair, and prints
            public key, then private key, each on its own line.
        ''',
    )
    add_default_arguments(parser)

    return parser

#@-node:help
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
        fcp_node = node.FCPNode(host=args.fcpHost, port=args.fcpPort, verbosity=verbosity,
                         logfile=sys.stderr)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        sys.stderr.write("Failed to connect to FCP service at %s:%d\n" % (args.fcpHost, args.fcpPort))
        sys.exit(1)

    # grab the keypair
    pub, priv = fcp_node.genkey()

    fcp_node.shutdown()

    # successful, return the uri
    print(pub)
    print(priv)

    # all done
    sys.exit(0)

#@-node:main
#@-others

#@-node:@file genkey.py
#@-leo
