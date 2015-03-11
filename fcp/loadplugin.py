"""
load a freenet plugin

This is the guts of the command-line front-end app fcploadplugin
"""

#@+others
#@+node:imports
import argparse
import sys
import traceback
import os.path
from urlparse import urlparse

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

    # default job options
    verbosity = node.ERROR
    verbose = False

    parser = create_parser()
    args = parser.parse_args(argv)
    uri = args.plugin_uri

    keytypes = ["USK", "KSK", "SSK", "CHK"]

    if os.path.isfile(uri) \
    or os.path.islink(uri) and os.path.isfile(os.path.realpath(uri)):
        if uri.endswith(".jar"):
            plugin_uri = uri
    elif urlparse(uri).scheme != "":
        plugin_uri = uri
    else:
        if not uri.startswith("freenet:"):
            uri = "freenet:" + uri
        if uri[len("freenet:"):len("freenet:")+3] in keytypes:
            plugin_uri = uri

    try:
        plugin_uri
    except NameError:
        sys.stderr.write("The given plugin uri is not valid.\n")
        sys.exit(1)

    # try to create the node
    try:
        fcp_node = node.FCPNode(host=args.fcphost, port=args.fcpport, verbosity=verbosity,
                         logfile=sys.stderr)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        sys.stderr.write("Failed to connect to FCP service at %s:%d\n" % (args.fcphost, args.fcpport))
        sys.exit(2)

    # send the LoadPlugin request
    fcp_node.fcpLoadPlugin(plugin_uri)

    fcp_node.shutdown()

    # successful
    print "Plugin successfully loaded."

    # all done
    sys.exit(0)