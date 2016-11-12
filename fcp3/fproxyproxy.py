#@+leo-ver=4
#@+node:@file fproxyproxy.py
"""
fproxyproxy

An http proxy atop fproxy which uses pyFreenet's 'name services'
"""

#@+others
#@+node:imports
import sys, os, getopt, traceback, mimetypes, time
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from http.client import HTTPConnection
import socket

from . import node
from .node import ERROR, INFO, DETAIL, DEBUG

#@-node:imports
#@+node:globals
progname = sys.argv[0]

#@-node:globals
#@+node:class Handler
class Handler(SimpleHTTPRequestHandler):
    """
    Handles each FProxyProxy client request
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, request, client_address, server):
        
        self.server = server
        SimpleHTTPRequestHandler.__init__(self, request, client_address, server)
    
    #@-node:__init__
    #@+node:do_GET
    def do_GET(self):
        
        print(("GET: client=%s path=%s" % (self.client_address, self.path)))
    
        #SimpleHTTPRequestHandler.do_GET(self)
    
        try:
            #mimetype, data = self.server.node.get(self.path[1:])
            #self.send_response(200)
            #self.send_header("Content-type", mimetype)
            #self.send_header("Content-Length", str(len(data)))
            #self.end_headers()
            #self.wfile.write(data)
            #self.wfile.flush()
    
            self.fproxyGet(self.path)
    
        except:
            traceback.print_exc()
            self.send_error(404, "File not found")
            return None
    
    #@-node:do_GET
    #@+node:fproxyGet
    def fproxyGet(self, path):
        """
        Fetches from fproxy, returns (status, mimetype, data)
        """
        server = self.server
        headers = self.headers
    
        print("--------------------------------------------")
        print(("** path=%s" % path))
    
        # first scenario - user is pointing their browser directly at
        # fproxyfproxy, barf!
        if not path.startswith("http://"):
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            data = "\n".join([
                "<html><head>",
                "<title>Access Denied</title>",
                "</head><body>",
                "<h1>Access Denied</h1>",
                "Sorry, but FProxyProxy is an http proxy server.<br>",
                "Please don't try to access it like a web server.",
                "</body></html>",
                "",
                ])
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Location", location)
            self.end_headers()
            self.wfile.write(data)
            self.wfile.flush()
            return
    
        # convert path to relative
        path = "/" + path[7:].split("/", 1)[-1]
        #print "** path=%s" % repr(path)
    
    
        try:
            # check host header
            hostname = headers.get("Host", 'fproxy')
            pathbits = path.split("/")
    
            print(("** hostname = %s" % hostname))
    
            # second scenario, user has just given a domain name without trailing /
            if len(pathbits) == 1:
                # redirect to force trailing slash
                location = path + "/"
                print(("** redirecting to: %s" % location))
    
                self.send_response(301)
                self.send_header("Content-type", "text/html")
                data = "\n".join([
                    "<html><head>",
                    "<title>Permanent redirect: new URI</title>",
                    "</head><body>",
                    "<h1>Permanent redirect: new URI</h1>",
                    "<a href=\"%s\">Click here</a>",
                    "</body></html>",
                    "",
                    ]) % location
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Location", location)
                self.end_headers()
                self.wfile.write(data)
                self.wfile.flush()
                return
    
            tail = "/".join(pathbits[1:])
    
            # third scenario - request into fproxy
            if hostname == 'fproxy':
    
                # tis an fproxy request, go straight through
                conn = HTTPConnection(server.fproxyHost, server.fproxyPort)
                conn.request("GET", path)
                resp = conn.getresponse()
                self.send_response(resp.status)
                self.send_header("Content-type",
                                 resp.getheader("Content-Type", "text/plain"))
                data = resp.read()
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                self.wfile.flush()
                conn.close()
                return
    
            else:
                # final scenario - some other domain, try lookup
                uri = server.node.namesiteLookup(hostname)
    
                if not uri:
                    # lookup failed, do the usual 404 thang
                    print(("** lookup of domain %s failed" % hostname))
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    data = "\n".join([
                        "<html><head>",
                        "<title>404 - Freenet name not found</title>",
                        "</head><body",
                        "<h1>404 - Freenet name not found</title>",
                        "The pyFreenet name service was unable to resolve ",
                        "the name %s" % hostname,
                        "<br><br>",
                        "You might like to find its freenet uri and try that ",
                        "within <a href=\"/fproxy/\">FProxy</a>",
                        "</body></html>",
                        "",
                        ])
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    self.wfile.flush()
    
                # lookup succeeded - ok to go now via fproxy
                conn = HTTPConnection(server.fproxyHost, server.fproxyPort)
                newpath = "/" + uri
                if tail:
                    if not newpath.endswith("/"):
                        newpath += "/"
                    newpath += tail
                print(("** newpath=%s" % newpath))
                conn.request("GET", newpath)
                resp = conn.getresponse()
                print(("** status=%s" % resp.status))
                self.send_response(resp.status)
                self.send_header("Content-type",
                                 resp.getheader("Content-Type", "text/plain"))
    
                # has fproxy sent us a redirect?
                if resp.status == 301:
                    # yuck, fproxy is telling us to redirect, which
                    # sadly means we have to lose the domain name
                    # from our browser address bar
                    location = resp.getheader("location")
                    newLocation = "http://fproxy" + location
                    print("*** redirected!!!")
                    print(("*** old location = %s" % location))
                    print(("***  --> %s" % newLocation))
                    self.send_header("Location", newLocation)
    
                # get the data from fproxy and send it up to the client
                data = resp.read()
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                self.wfile.flush()
                conn.close()
                return
    
            return
    
        except socket.error:
            raise
    
    #@-node:fproxyGet
    #@-others

#@-node:class Handler
#@+node:class FProxyProxy
class FProxyProxy(ThreadingMixIn, HTTPServer):
    """
    an http proxy that runs atop fproxy, and uses the pyFreenet name service
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, **kw):
        """
        runs the FProxyProxy service
        
        Keywords:
            - node - a live FCPNode object
            - fproxyHost - hostname of fproxy
            - fproxyPort - port of fproxy
            - listenHost - hostname to listen on for client HTTP connections
            - listenPort - port to listen on for client HTTP connections
        """
        for k in ['node', 'fproxyHost', 'fproxyPort', 'listenHost', 'listenPort']:
            setattr(self, k, kw[k])
    
        self.log = self.node._log
    
        HTTPServer.__init__(self, (self.listenHost, self.listenPort), Handler)
    
    #@-node:__init__
    #@+node:run
    def run(self):
        """
        Starts the proxy, runs forever till interrupted
        """
        log = self.log
        log(ERROR, "FproxyProxy listening on %s:%s" % (self.listenHost, self.listenPort))
        log(ERROR, "  -> forwarding requests to fproxy at %s:%s" % (
                    self.fproxyHost, self.fproxyPort))
    
        self.serve_forever()
    
    #@-node:run
    #@-others

#@-node:class FProxyProxy
#@+node:usage
def usage(msg=None, ret=1):
    """
    Prints usage message then exits
    """
    if msg:
        sys.stderr.write(msg+"\n")
    sys.stderr.write("Usage: %s [options] src-uri target-uri\n" % progname)
    sys.stderr.write("Type '%s -h' for help\n" % progname)
    sys.exit(ret)

#@-node:usage
#@+node:help
def help():
    """
    print help options, then exit
    """
    print(("%s: runs an http proxy atop fproxy,"  % progname))
    print("which uses pyFreenet 'name services'")
    print()
    print("Note - you should configure fproxyproxy as an http proxy")
    print("in your browser (best done via Firefox's 'switchproxy' extension")
    print()
    print(("Usage: %s [options] src-uri target-uri" % progname))
    print()
    print("Options:")
    print("  -h, -?, --help")
    print("     Print this help message")
    print("  -v, --verbose")
    print("     Print verbose progress messages to stderr")
    print("  -H, --fcpHost=<hostname>")
    print("     Connect to FCP service at host <hostname>")
    print("  -P, --fcpPort=<portnum>")
    print("     Connect to FCP service at port <portnum>")
    print("  -p, --fproxyAddress=[<hostname>][:<portnum>]")
    print("     Use fproxy service at <hostname>:<portnum>,")
    print("     default 127.0.0.1:8888")
    print("  -L, --listenAddress=[<hostname>][:<portnum>]")
    print("     Listen for http connections on <hostname>:<portnum>,")
    print("     default is 127.0.0.1:8889")
    print("  -V, --version")
    print("     Print version number and exit")
    print()
    print("Environment:")
    print("  Instead of specifying -H and/or -P, you can define the environment")
    print("  variables FCP_HOST and/or FCP_PORT respectively")

    sys.exit(0)

#@-node:help
#@+node:main
def main():
    """
    Front end for fproxyproxy utility
    """
    # default job options
    verbosity = node.ERROR
    verbose = False
    fcpHost = node.defaultFCPHost
    fcpPort = node.defaultFCPPort
    fproxyHost = os.environ.get("FPROXY_HOST", "127.0.0.1")
    fproxyPort = int(os.environ.get("FPROXY_PORT", 8888))
    listenHost = os.environ.get("FPROXYPROXY_HOST", "127.0.0.1")
    listenPort = int(os.environ.get("FPROXYPROXY_PORT", 8889))

    opts = {
            "Verbosity" : 0,
            }

    # process command line switches
    try:
        cmdopts, args = getopt.getopt(
            sys.argv[1:],
            "?hvH:P:Vp:L:",
            ["help", "verbose", "fcpHost=", "fcpPort=", "version",
             "listenAddress=", "fproxyAddress=",
             ]
            )
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    output = None
    verbose = False
    #print cmdopts
    for o, a in cmdopts:

        if o in ("-?", "-h", "--help"):
            help()

        if o in ("-V", "--version"):
            print(("This is %s, version %s" % (progname, node.fcpVersion)))
            sys.exit(0)

        if o in ("-v", "--verbosity"):
            verbosity = node.DETAIL
            opts['Verbosity'] = 1023
            verbose = True

        if o in ("-H", "--fcpHost"):
            fcpHost = a
        
        if o in ("-P", "--fcpPort"):
            try:
                fcpPort = int(a)
            except:
                usage("Invalid fcpPort argument %s" % repr(a))

        if o in ("-L", "--listenAddress"):
            parts = a.split(":")
            if len(parts) == 1:
                listenHost = parts[0]
            elif len(parts) == 2:
                if parts[0]:
                    listenHost = parts[0]
                if parts[1]:
                    listenPort = int(parts[1])
            else:
                usage("Invalid listen address '%s'" % a)

        if o in ("-p", "--fproxyAddress"):
            parts = a.split(":")
            if len(parts) == 1:
                fproxyHost = parts[0]
            elif len(parts) == 2:
                if parts[0]:
                    fproxyHost = parts[0]
                if parts[1]:
                    fproxyPort = int(parts[1])
            
    # try to create an FCP node, needed for name lookups
    try:
        n = node.FCPNode(host=fcpHost, port=fcpPort, verbosity=verbosity,
                         logfile=sys.stderr)
        log = n._log
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        usage("Failed to connect to FCP service at %s:%s" % (fcpHost, fcpPort))

    try:
        proxy = FProxyProxy(
                    node=n,
                    fproxyHost=fproxyHost, fproxyPort=fproxyPort,
                    listenHost=listenHost, listenPort=listenPort)
        proxy.run()
        sys.exit(0)
    except KeyboardInterrupt:
        print("fproxyproxy terminated by user")
        n.shutdown()
        sys.exit(0)
    except:
        traceback.print_exc()
        print("fproxyproxy terminated")
        n.shutdown()
        sys.exit(1)

#@-node:main
#@-others

#@-node:@file fproxyproxy.py
#@-leo
