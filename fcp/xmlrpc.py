#! /usr/bin/env python
"""
fcpxmlrpc.py

Exposes some pyFreenet primitives over an XML-RPC service
"""

# standard library imports
import sys
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn

# FCP imports
from . import node

# where to listen, for the xml-rpc server
xmlrpcHost = "127.0.0.1"
xmlrpcPort = 19481

class FCPXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    """
    Multi-threaded XML-RPC server for freenet FCP access
    """
    def __init__(self, **kw):
        """
        Creates the xml-rpc server
    
        Keywords:
            - host - hostname to listen on for xml-rpc requests, default 127.0.0.1
            - port - port  to listen on for xml-rpc requests, default 19481
            - fcpHost - hostname where FCP port is
            - fcpPort - port where FCP port is
            - verbosity - verbosity of output messages, 0 (silent) through 6 (noisy),
              default 4. Refer verbosity constants in fcp module
        """
        # create the server
        host = kw.get('host', xmlrpcHost)
        port = kw.get('port', xmlrpcPort)
    
        SimpleXMLRPCServer.__init__(self, (host, port))
    
        # create the fcp node interface
        fcpHost = kw.get('fcpHost', node.defaultFCPHost)
        fcpPort = kw.get('fcpPort', node.defaultFCPPort)
        verbosity = kw.get('verbosity', node.SILENT)
    
        self.node = node.FCPNode(host=fcpHost,
                                 port=fcpPort,
                                 verbosity=verbosity,
                                 )
    
        # create the request handler
        hdlr = FreenetXMLRPCRequestHandler(self.node)
    
        # link in the request handler object
        self.register_instance(hdlr)
        self.register_introspection_functions()
    
    def run(self):
        """
        Launch the server to run forever
        """
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            self.node.shutdown()
            raise
    

class FreenetXMLRPCRequestHandler:
    """
    Simple class which exposes basic primitives
    for freenet xmlrpc server
    """
    def __init__(self, fcpnode):
    
        self.node = fcpnode
    
    
    def get(self, uri, options=None):
        """
        Performs a fetch of a key
    
        Arguments:
            - uri - the URI to retrieve
            - options - a mapping (dict) object containing various
              options - refer to FCPNode.get documentation
        """
        if options is None:
            options = {}
        
        if 'file' in options:
            raise Exception("file option not available over XML-RPC")
        if 'dir' in options:
            raise Exception("dir option not available over XML-RPC")
    
        return self.node.get(uri, **options)
    
    def put(self, uri, options=None):
        """
        Inserts data to node
    
        Arguments:
            - uri - the URI to insert under
            - options - a mapping (dict) object containing various options,
              refer to FCPNode.get documentation
        """
        if options is None:
            options = {}
    
        if 'file' in options:
            raise Exception("file option not available over XML-RPC")
        if 'dir' in options:
            raise Exception("dir option not available over XML-RPC")
    
        return self.node.put(uri, data=data, **options)
    
    def genkey(self):
        
        return self.node.genkey()
    

def usage(msg="", ret=1):

    if msg:
        sys.stderr.write(msg+"\n")

    print("\n".join([
        "Freenet XML-RPC Server",
        "Usage: %s [options]" % sys.argv[0],
        "Options:",
        "  -h, --help",
        "       show this usage message",
        "  -v, --verbosity=",
        "       set verbosity level, values are:",
        "         0 (SILENT) show only 1 line for incoming hits",
        "         1 (FATAL) show only fatal messages",
        "         2 (CRITICAL) show only major failures",
        "         3 (ERROR) show significant errors",
        "         4 (INFO) show basic request details",
        "         5 (DETAIL) show FCP dialogue",
        "         6 (DEBUG) show ridiculous amounts of debug info",
        "  --host=",
        "       listen hostname for xml-rpc requests, default %s" % xmlrpcHost,
        "  --port=",
        "       listen port number for xml-rpc requests, default %s" % xmlrpcPort,
        "  --fcphost=",
        "       set hostname of freenet FCP interface, default %s" \
             % node.defaultFCPHost,
        "  --fcpport=",
        "       set port number of freenet FCP interface, default %s" \
             % node.defaultFCPPort,
        ]))

    sys.exit(ret)

def testServer():
    
    runServer(host="", fcpHost="127.0.0.1", verbosity=DETAIL)

def runServer(**kw):
    """
    Creates and runs a basic XML-RPC server for FCP access
    
    For keyword parameters, refer FCPXMLRPCServer constructor
    """
    FCPXMLRPCServer(**kw).run()

def main():
    """
    When this script is executed, it runs the XML-RPC server
    """
    import getopt

    opts = {'verbosity': node.INFO,
            'host':xmlrpcHost,
            'port':xmlrpcPort,
            'fcpHost':node.defaultFCPHost,
            'fcpPort':node.defaultFCPPort,
            }

    try:
        cmdopts, args = getopt.getopt(sys.argv[1:],
                                   "?hv:",
                                   ["help", "verbosity=", "host=", "port=",
                                    "fcphost=", "fcpport="])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    output = None
    verbose = False
    #print cmdopts
    for o, a in cmdopts:
        if o in ("-h", "--help"):
            usage(ret=0)
        elif o == "--host":
            opts['host'] = a
        elif o == "--port":
            try:
                opts['port'] = int(a)
            except:
                usage("Invalid port number '%s'" % a)
        elif o == "--fcphost":
            opts['fcpHost'] = a
        elif o == "--fcpport":
            opts['fcpPort'] = a
        elif o in ['-v', '--verbosity']:
            print("setting verbosity")
            try:
                opts['verbosity'] = int(a)
                #print "verbosity=%s" % opts['verbosity']
            except:
                usage("Invalid verbosity '%s'" % a)

    #print "Verbosity=%s" % opts['verbosity']

    if opts['verbosity'] >= node.INFO:
        print("Launching Freenet XML-RPC server")
        print("Listening on %s:%s" % (opts['host'], opts['port']))
        print("Talking to Freenet FCP at %s:%s" % (opts['fcpHost'], opts['fcpPort']))

    try:
        runServer(**opts)
    except KeyboardInterrupt:
        print("Freenet XML-RPC server terminated by user")



if __name__ == '__main__':
    
    main()

