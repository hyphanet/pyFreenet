#!/usr/bin/env python2

# CGI-based XML-RPC interface to FCP
# You can use this on your FCP server


from SimpleXMLRPCServer import CGIXMLRPCRequestHandler

import fcp
from fcp.xmlrpc import FreenetXMLRPCRequestHandler

# hostname and port of FCP interface
fcpHost = "10.0.0.1"
fcpPort = 9481

# verbosity for logging
verbosity = node.DETAIL

# where the logfile is
logfile = "/tmp/fcpxmlrpc.log"

def main():

    # create the fcp node interface
    node = fcp.FCPNode(host=fcpHost,
                                 port=fcpPort,
                                 verbosity=verbosity,
                                 logfile=logfile,
                                 )

    # create the request handler
    hdlr = FreenetXMLRPCRequestHandler(node)

    # create the handler
    handler = CGIXMLRPCRequestHandler()
    handler.register_introspection_functions()

    # link in the node wrapper
    handler.register_instance(hdlr)

    # now do the business
    handler.handle_request()

    node.shutdown()

if __name__ == '__main__':
    main()


import fcpxmlrpc

