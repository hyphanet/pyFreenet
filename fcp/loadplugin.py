"""
load a freenet plugin

This is the guts of the command-line front-end app fcploadplugin
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
        prog='fcploadplugin',
        description='''
            A simple command-line freenet load plugin command.

            Loads a plugin to the running node.
        ''',
    )
    add_default_arguments(parser)

    parser.add_argument(
        'plugin_uri',
        help='''
            A URI that points to the plugin location. 
        ''',
    )

    return parser

#@-node:help
#@+node:main
def main(argv=sys.argv[1:]):
    """
    Front end for fcploadplugin utility
    """

    parser = create_parser()
    args = parser.parse_args()

    plugin_uri = args.plugin_uri

    # default job options
    verbosity = node.ERROR
    verbose = False

    parser = create_parser()
    args = parser.parse_args(argv)

    # try to create the node
    try:
        fcp_node = node.FCPNode(host=args.fcphost, port=args.fcpport, verbosity=verbosity,
                         logfile=sys.stderr)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        sys.stderr.write("Failed to connect to FCP service at %s:%d\n" % (args.fcphost, args.fcpport))
        sys.exit(1)

    # send the LoadPlugin request
    fcp_node.fcpLoadPlugin(plugin_uri)

    fcp_node.shutdown()

    # successful
    print "Plugin successfully loaded."

    # all done
    sys.exit(0)