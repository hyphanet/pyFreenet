#!/usr/bin/env python
"""
An implementation of a freenet client library for
FCP v2

This can be imported as a module by client apps wanting
a simple Freenet FCP v2 interface, or it can be executed
to run an XML-RPC server talking to FCP (run with -h for more info)

Written by aum, May 2006, released under the GNU Lesser General
Public License.

No warranty, yada yada

Python hackers please feel free to hack constructively, but I
strongly request that you preserve the simplicity and not impose
any red tape on client writers.

"""

import sys, os, socket, time, thread, threading

from SimpleXMLRPCServer import SimpleXMLRPCServer

class ConnectionRefused(Exception):
    """
    cannot connect to given host/port
    """

class FCPException(Exception):

    def __init__(self, info=None):
        print "Creating fcp exception"
        if not info:
            info = {}
        self.info = info
        print "fcp exception created"

    def __str__(self):
        
        parts = []
        for k in ['header', 'ShortCodeDescription', 'CodeDescription']:
            if self.info.has_key(k):
                parts.append(str(self.info[k]))
        return ";".join(parts) or "??"

class FCPGetFailed(FCPException):
    pass

class FCPPutFailed(FCPException):
    pass

class FCPProtocolError(FCPException):
    pass

defaultFCPHost = "127.0.0.1"
defaultFCPPort = 9481

xmlrpcHost = "127.0.0.1"
xmlrpcPort = 19481

# list of keywords sent from node to client, which have
# int values
intKeys = [
    'DataLength', 'Code',
    ]

expectedVersion="2.0"

SILENT = 0
FATAL = 1
CRITICAL = 2
ERROR = 3
INFO = 4
DETAIL = 5
DEBUG = 6

class FCPNodeConnection:
    """
    Low-level transport for connections to
    FCP port
    """
    def __init__(self, **kw):
        """
        Create a connection object
        
        Arguments:
            - clientName - name of client to use with reqs, defaults to random
            - host - hostname, defaults to defaultFCPHost
            - port - port number, defaults to defaultFCPPort
            - logfile - a pathname or writable file object, to which log messages
              should be written, defaults to stdout
            - verbosity - how detailed the log messages should be, defaults to 0
              (silence)
        """
        self.name = kw.get('clientName', self._getUniqueId())
        self.host = kw.get('host', defaultFCPHost)
        self.port = kw.get('port', defaultFCPPort)
        
        logfile = kw.get('logfile', sys.stderr)
        if not hasattr(logfile, 'write'):
            # might be a pathname
            if not isinstance(logfile, str):
                raise Exception("Bad logfile, must be pathname or file object")
            logfile = file(logfile, "a")
        self.logfile = logfile
    
        self.verbosity = kw.get('verbosity', 0)
    
        # try to connect
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
    
        # the incoming response queues
        self.pendingResponses = {} # keyed by request ID
    
        # lock for socket operations
        self.socketLock = threading.Lock()
            
        # launch receiver thread
        #thread.start_new_thread(self.rxThread, ())
    
    def __del__(self):
        """
        object is getting cleaned up, so disconnect
        """
        if self.socket:
            self.socket.close()
            del self.socket
    
        if self.logfile not in [sys.stdout, sys.stderr]:
            self.logfile.close()
    
    # high level client methods
    
    def hello(self):
        
        self._sendMessage("ClientHello", 
                         Name=self.name,
                         ExpectedVersion=expectedVersion)
        
        resp = self._receiveMessage()
        return resp
    
    def get(self, uri, **kw):
        """
        Does a direct get, returning the value as a string
    
        Keywords:
            - DSOnly - whether to only check local datastore
            - file - if given, this is a pathname to which to store the retrieved key
        """
        opts = {}
        file = kw.pop("file", None)
        if file:
            opts['ReturnType'] = "disk"
            opts['File'] = file
        else:
            opts['ReturnType'] = "direct"
        
        opts['Identifier'] = self._getUniqueId()
        
        if kw.get("IgnoreDS", False):
            opts["IgnoreDS"] = "true"
        else:
            opts["IgnoreDS"] = "false"
        
        if kw.get("DSOnly", False):
            opts["DSOnly"] = "true"
        else:
            opts["DSOnly"] = "false"
        
        opts['URI'] = uri
        opts['Verbosity'] = "0"
    
        opts['MaxRetries'] = kw.get("MaxRetries", 3)
        opts['MaxSize'] = 10000000000
        opts['PriorityClass'] = 1
        opts['Global'] = "false"
    
        self._sendMessage("ClientGet", **opts)
       
    #ClientGet
    #IgnoreDS=false // true = ignore the datastore (in old FCP this was RemoveLocalKey)
    #DSOnly=false // true = only check the datastore, don't route (~= htl 0)
    #URI=KSK@gpl.txt // key to fetch
    #Identifier=Request Number One
    #Verbosity=0 // no status, just tell us when it's done
    #ReturnType=direct // return all at once over the FCP connection
    #MaxSize=100 // maximum size of returned data (all numbers in DECIMAL)
    #MaxTempSize=1000 // maximum size of intermediary data
    #MaxRetries=100 // automatic retry supported as an option; -1 means retry forever
    #PriorityClass=1 // priority class 1 = interactive
    #Persistence=reboot // continue until node is restarted; report progress while client is
    #	 connected, including if it reconnects after losing connection
    #ClientToken=hello // returned in PersistentGet, a hint to the client, so the client
    #	 doesn't need to maintain its own state
    #Global=false // see Persistence section below
    #EndMessage
    
        # get a response
        resp = self._receiveMessage()
        hdr = resp['header']
        if hdr == 'DataFound':
            if file:
                # already stored to disk, done
                resp['file'] = file
                return
            else:
                resp = self._receiveMessage()
                if resp['header'] == 'AllData':
                    return resp['Data']
                else:
                    raise FCPProtocolError(resp)
        elif hdr == 'GetFailed':
            raise FCPGetFailed(resp)
        elif hdr == 'ProtocolError':
            raise FCPProtocolError(resp)
        else:
            raise FCPException(resp)
    
    def put(self, uri, **kw):
        """
        Inserts a key
        
        Arguments:
            - uri - uri under which to insert the key
        
        Keywords:
            - file - path of file from which to read the key data
            - data - the raw data of the key as string
            - mimetype - the mime type, default text/plain
        """
    #ClientPut
    #URI=CHK@ // could as easily be an insertable SSK or KSK URI
    #Metadata.ContentType=text/html // MIME type; for text, if charset is not specified, node #should auto-detect it and force the auto-detected version
    #Identifier=Insert-1 // identifier, as always
    #Verbosity=0 // just report when complete
    #MaxRetries=999999 // lots of retries; -1 = retry forever
    #PriorityClass=1 // fproxy priority level
    #GetCHKOnly=false // true = don't insert the data, just return the key it would generate
    #Global=false // see Persistence section below
    #DontCompress=true // hint to node: don't try to compress the data, it's already compressed
    #ClientToken=Hello!!! // sent back to client on the PersistentPut if this is a persistent #request
    
    # the following fields decide where the data is to come from:
    
    #UploadFrom=direct // attached directly to this message
    #DataLength=100 // 100 bytes decimal
    #Data
    #<data>
    # or
    #UploadFrom=disk // upload a file from disk
    #Filename=/home/toad/something.html
    #End
    # or
    #UploadFrom=redirect // create a redirect to another key
    #TargetURI=KSK@gpl.txt // some other freenet URI
    #End
    
        opts = {}
        opts['URI'] = uri
        opts['Metadata.ContentType'] = kw.get("mimetype", "text/plain")
        id = self._getUniqueId()
        opts['Identifier'] = id
        opts['Verbosity'] = 0
        opts['MaxRetries'] = 3
        opts['PriorityClass'] = 1
        opts['GetCHKOnly'] = "false"
        opts['DontCompress'] = "false"
        
        if kw.has_key("file"):
            opts['UploadFrom'] = "disk"
            opts['Filename'] = kw['file']
            sendEnd = True
        elif kw.has_key("data"):
            opts["UploadFrom"] = "direct"
            opts["Data"] = kw['data']
            sendEnd = False
        elif kw.has_key("redirect"):
            opts["UploadFrom"] = "redirect"
            opts["TargetURI"] = kw['redirect']
            sendEnd = True
        else:
            raise Exception("Must specify file, data or redirect keywords")
    
        #print "sendEnd=%s" % sendEnd
        
        self._sendMessage("ClientPut", sendEnd, **opts)
    
        # expect URIGenerated
        resp1 = self._receiveMessage()
        hdr = resp1['header']
        if hdr != 'URIGenerated':
            raise FCPException(resp1)
    
        newUri = resp1['URI']
        
        # expect outcome
        resp2 = self._receiveMessage()
        hdr = resp2['header']
        if hdr == 'PutSuccessful':
            return resp2['URI']
        elif hdr == 'PutFailed':
            raise FCPPutFailed(resp2)
        elif hdr == 'ProtocolError':
            raise FCPProtocolError(resp2)
        else:
            raise FCPException(resp2)
    
    def genkey(self, id=None):
        """
        Generates and returns an SSK keypair
        """
        if not id:
            id = self._getUniqueId()
        
        self._sendMessage("GenerateSSK",
                         Identifier=id)
        
        while True:
            resp = self._receiveMessage()
            print resp
            if resp['header'] == 'SSKKeypair' and str(resp['Identifier']) == id:
                break
    
        return resp['RequestURI'], resp['InsertURI']
    
    
    
    
    # methods for receiver thread
    
    def _rxThread(self):
        """
        Receives all incoming messages
        """
        while self.running:
            self.socketLock.acquire()
            self.socket.settimeout(0.1)
            try:
                msg = self._receiveMessage()
            except socket.timeout:
                self.socketLock.release()
                continue
            
    
    # low level noce comms methods
    
    def _getUniqueId(self):
        return "id" + str(int(time.time() * 1000000))
    
    def _sendMessage(self, msgType, sendEndMessage=True, **kw):
        """
        low level message send
        
        Arguments:
            - msgType - one of the FCP message headers, such as 'ClientHello'
            - args - zero or more (keyword, value) tuples
        """
        if kw.has_key("Data"):
            data = kw.pop("Data")
        else:
            data = None
    
        log = self._log
        
        items = [msgType + "\n"]
        log(DETAIL, "CLIENT: %s" % msgType)
    
        #print "CLIENT: %s" % msgType
        for k, v in kw.items():
            #print "CLIENT: %s=%s" % (k,v)
            line = k + "=" + str(v)
            items.append(line + "\n")
            log(DETAIL, "CLIENT: %s" % line)
    
        if data != None:
            items.append("DataLength=%d\n" % len(data))
            log(DETAIL, "CLIENT: DataLength=%d" % len(data))
            items.append("Data\n")
            log(DETAIL, "CLIENT: ...data...")
            items.append(data)
    
        #print "sendEndMessage=%s" % sendEndMessage
    
        if sendEndMessage:
            items.append("EndMessage\n")
            log(DETAIL, "CLIENT: EndMessage")
        raw = "".join(items)
    
        self.socket.send(raw)
    
    def _receiveMessage(self):
        """
        Receives and returns a message as a dict
        
        The header keyword is included as key 'header'
        """
        log = self._log
    
        # shorthand, for reading n bytes
        def read(n):
            if n > 1:
                log(DEBUG, "read: want %d bytes" % n)
            chunks = []
            remaining = n
            while remaining > 0:
                chunk = self.socket.recv(remaining)
                chunklen = len(chunk)
                chunks.append(chunk)
                remaining -= chunklen
                if remaining > 0:
                    if n > 1:
                        log(DEBUG,
                            "wanted %s, got %s still need %s bytes" % (n, chunklen, remaining)
                            )
                    pass
            buf = "".join(chunks)
            return buf
    
        # read a line
        def readln():
            buf = []
            while True:
                c = read(1)
                buf.append(c)
                if c == '\n':
                    break
            ln = "".join(buf)
            log(DETAIL, "NODE: " + ln[:-1])
            return ln
    
        items = {}
    
        # read the header line
        while True:
            line = readln().strip()
            if line:
                items['header'] = line
                break
    
        # read the body
        while True:
            line = readln().strip()
            if line in ['End', 'EndMessage']:
                break
    
            if line == 'Data':
                # read the following data
                buf = read(items['DataLength'])
                items['Data'] = buf
                log(DETAIL, "NODE: ...<%d bytes of data>" % len(buf))
                break
            else:
                # it's a normal 'key=val' pair
                try:
                    k, v = line.split("=")
                except:
                    #print "unexpected: %s"%  line
                    raise
    
                # attempt int conversion
                try:
                    v = int(v)
                except:
                    pass
    
                items[k] = v
    
        # all done
        return items
    
    def _log(self, level, msg):
        """
        Logs a message. If level > verbosity, don't output it
        """
        if level > self.verbosity:
            return
    
        if not msg.endswith("\n"): msg += "\n"
        self.logfile.write(msg)
        self.logfile.flush()
    

class FreenetXMLRPCRequest:
    """
    Simple class which exposes basic primitives
    for freenet xmlrpc server
    """
    def __init__(self, **kw):
    
        self.kw = kw
    
    def _getNode(self):
        
        node = FCPNodeConnection(**self.kw)
        node.hello()
        return node
    
    def _hello(self):
        
        self.node.hello()
    
    def get(self, uri):
        """
        Gets and returns a uri directly
        """
        node = self._getNode()
    
        return node.get(uri)
    
    def getfile(self, uri, path):
        """
        Gets and returns a uri directly
        """
        node = self._getNode()
    
        return node.get(uri, file=path)
    
    def put(self, uri, data):
        """
        Inserts to node
        """
        node = self._getNode()
    
        return node.put(uri, data=data)
    
    def putfile(self, uri, path):
        """
        Inserts to node from a file
        """
        node = self._getNode()
    
        return node.put(uri, file=path)
    
    def genkey(self):
        
        node = self._getNode()
    
        return self.node.genkey()
    

def runServer(**kw):
    """
    Runs a basic XML-RPC server for FCP access
    """
    host = kw.get('host', xmlrpcHost)
    port = kw.get('port', xmlrpcPort)
    fcpHost = kw.get('fcpHost', defaultFCPHost)
    fcpPort = kw.get('fcpPort', defaultFCPPort)
    verbosity = kw.get('verbosity', SILENT)

    server = SimpleXMLRPCServer((xmlrpcHost, xmlrpcPort))
    inst = FreenetXMLRPCRequest(host=fcpHost, port=fcpPort, verbosity=verbosity)
    server.register_instance(inst)
    server.serve_forever()

def testServer():
    
    runServer(host="", fcpHost="10.0.0.1", verbosity=DETAIL)

def usage(msg="", ret=1):

    if msg:
        sys.stderr.write(msg+"\n")

    print "\n".join([
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
        "       set hostname of freenet FCP interface, default %s" % defaultFCPHost,
        "  --fcpport=",
        "       set port number of freenet FCP interface, default %s" % defaultFCPPort,
        ])

    sys.exit(ret)

def main():
    """
    When this script is executed, it runs the XML-RPC server
    """
    import getopt

    opts = {'verbosity': 0,
            'host':xmlrpcHost,
            'port':xmlrpcPort,
            'fcpHost':defaultFCPHost,
            'fcpPort':defaultFCPPort,
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
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
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
            try:
                opts['verbosity'] = int(a)
                #print "verbosity=%s" % opts['verbosity']
            except:
                usage("Invalid verbosity '%s'" % a)

    if opts['verbosity'] >= INFO:
        print "Launching Freenet XML-RPC server"
        print "Listening on %s:%s" % (opts['host'], opts['port'])
        print "Talking to Freenet FCP at %s:%s" % (opts['fcpHost'], opts['fcpPort'])

    try:
        runServer(**opts)
    except KeyboardInterrupt:
        print "Freenet XML-RPC server terminated by user"



if __name__ == '__main__':
    
    main()


