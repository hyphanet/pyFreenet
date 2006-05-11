#!/usr/bin/env python
#@+leo-ver=4
#@+node:@file fcp.py
#@@first
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

#@+others
#@+node:imports
import sys, os, socket, time, thread, threading, mimetypes, sha

from SimpleXMLRPCServer import SimpleXMLRPCServer

#@-node:imports
#@+node:exceptions
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

#@-node:exceptions
#@+node:globals
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

#@-node:globals
#@+node:class FCPNodeConnection
class FCPNodeConnection:
    """
    Low-level transport for connections to
    FCP port
    """
    #@    @+others
    #@+node:__init__
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
    
        # now do the hello
        self.hello()
    
        # the incoming response queues
        self.pendingResponses = {} # keyed by request ID
    
        # lock for socket operations
        self.socketLock = threading.Lock()
    
        # launch receiver thread
        #thread.start_new_thread(self.rxThread, ())
    
    #@-node:__init__
    #@+node:__del__
    def __del__(self):
        """
        object is getting cleaned up, so disconnect
        """
        if self.socket:
            self.socket.close()
            del self.socket
    
        if self.logfile not in [sys.stdout, sys.stderr]:
            self.logfile.close()
    
    #@-node:__del__
    #@+node:High Level Methods
    # high level client methods
    
    #@+others
    #@+node:hello
    def hello(self):
        
        self._sendMessage("ClientHello", 
                         Name=self.name,
                         ExpectedVersion=expectedVersion)
        
        resp = self._receiveMessage()
        return resp
    
    #@-node:hello
    #@+node:get
    def get(self, uri, **kw):
        """
        Does a direct get of a key
    
        Keywords:
            - dsnly - whether to only check local datastore
            - ignoreds - don't check local datastore
            - file - if given, this is a pathname to which to store the retrieved key
            - nodata - if true, no data will be returned. This can be a useful
              test of whether a key is retrievable, without having to consume resources
              by retrieving it
    
        Returns a 2-tuple, depending on keyword args:
            - if 'file' is given, returns (mimetype, pathname) if key is returned
            - if 'file' is not given, returns (mimetype, data) if key is returned
            - if 'dontReturnData' is true, returns (mimetype, 1) if key is returned
        If key is not found, raises an exception
        """
        opts = {}
    
        file = kw.pop("file", None)
        if file:
            opts['ReturnType'] = "disk"
            opts['File'] = file
    
        elif opts.get('nodata', False):
            nodata = True
            opts['ReturnType'] = "none"
        else:
            nodata = False
            opts['ReturnType'] = "direct"
        
        opts['Identifier'] = self._getUniqueId()
        
        if kw.get("ignoreds", False):
            opts["IgnoreDS"] = "true"
        else:
            opts["IgnoreDS"] = "false"
        
        if kw.get("dsonly", False):
            opts["DSOnly"] = "true"
        else:
            opts["DSOnly"] = "false"
        
        opts['URI'] = uri
        opts['Verbosity'] = "0"
    
        opts['MaxRetries'] = kw.get("maxretries", 3)
        opts['MaxSize'] = kw.get("maxsize", "1000000000000")
        opts['PriorityClass'] = int(kw.get("priority", 1))
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
            mimetype = resp['Metadata.ContentType']
            if file:
                # already stored to disk, done
                resp['file'] = file
                return (mimetype, file)
            elif nodata:
                return (mimetype, 1)
            else:
                resp = self._receiveMessage()
                if resp['header'] == 'AllData':
                    return (mimetype, resp['Data'])
                else:
                    raise FCPProtocolError(resp)
        elif hdr == 'GetFailed':
            raise FCPGetFailed(resp)
        elif hdr == 'ProtocolError':
            raise FCPProtocolError(resp)
        else:
            raise FCPException(resp)
    
    #@-node:get
    #@+node:put
    def put(self, uri="CHK@", **kw):
        """
        Inserts a key
        
        Arguments:
            - uri - uri under which to insert the key
        
        Keywords - you must specify one of the following to choose an insert mode:
            - file - path of file from which to read the key data
            - data - the raw data of the key as string
            - dir - the directory to insert, for freesite insertion
            - redirect - the target URI to redirect to
    
        Keywords for 'dir' mode:
            - name - name of the freesite, the 'sitename' in SSK@privkey/sitename'
            - usk - whether to insert as a USK (USK@privkey/sitename/version/), default False
            - version - valid if usk is true, default 0
    
        Keywords for 'file' and 'data' modes:
            - chkonly - only generate CHK, don't insert - default false
            - dontcompress - do not compress on insert - default false
    
        Keywords for 'file', 'data' and 'redirect' modes:
            - mimetype - the mime type, default text/plain
    
        Keywords valid for all modes:
            - maxretries - maximum number of retries, default 3
            - priority - default 1
    
        Notes:
            - exactly one of 'file', 'data' or 'dir' keyword arguments must be present
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
    
        # divert to putdir if dir keyword present
        if kw.has_key('dir'):
            return self.putdir(uri, **kw)
    
        opts = {}
        opts['URI'] = uri
        opts['Metadata.ContentType'] = kw.get("mimetype", "text/plain")
        id = self._getUniqueId()
        opts['Identifier'] = id
        opts['Verbosity'] = 0
        opts['MaxRetries'] = kw.get("maxretries", 3)
        opts['PriorityClass'] = kw.get("priority", 1)
        opts['GetCHKOnly'] = toBool(kw.get("chkonly", "false"))
        opts['DontCompress'] = toBool(kw.get("nocompress", "false"))
    
        # if inserting a freesite, scan the directory and insert each bit piecemeal
        if kw.has_key("dir"):
            if kw.get('usk', False):
                uri = uri.replace("SSK@", "USK@")
            if not uri.endswith("/"):
                uri = uri + "/"
    
            # form a base privkey-based URI
            siteuri = uri + "%s/%s/" % (kw['sitename'], kw.get('version', 1))
    
            opts['UploadFrom'] = "disk"
    
            # upload all files in turn - rework this later when queueing is implemented
            files = readdir(kw['dir'])
            for f in files:
                thisuri = siteuri + f['relpath']
                opts['file'] = f['fullpath']
                opts['mimetype'] = f['mimetype']
                self.put(thisuri, **opts)
    
            # last bit - insert index.html
            opts['file'] = os.path.join(kw['dir'], "index.html")
            thisuri = siteuri + "index.html"
            opts['mimetype'] = "text/html"
            self.put(thisuri, **opts)
            
            return uri
    
        elif kw.has_key("file"):
            opts['UploadFrom'] = "disk"
            opts['Filename'] = kw['file']
            if not kw.has_key("mimetype"):
                opts['Metadata.ContentType'] = mimetypes.guess_type(kw['file'])[0] or "text/plain"
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
    
        # issue the command
        self._sendMessage("ClientPut", sendEnd, **opts)
    
        # expect URIGenerated
        resp1 = self._receiveMessage()
        hdr = resp1['header']
        if hdr != 'URIGenerated':
            raise FCPException(resp1)
    
        newUri = resp1['URI']
    
        # bail here if no data coming back
        if opts.get('UploadFrom', None) == 'redirect' or opts['GetCHKOnly'] == 'true':
            if not kw.has_key('redirect'):
                return newUri
        
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
    
    #@-node:put
    #@+node:putdir
    def putdir(self, uri, **kw):
        """
        Inserts a freesite
    
        Arguments:
            - uri - uri under which to insert the key
        
        Keywords:
            - dir - the directory to insert - mandatory, no default.
              This directory must contain a toplevel index.html file
            - name - the name of the freesite, defaults to 'freesite'
            - usk - set to True to insert as USK (Default false)
            - version - the USK version number, default 0
    
            - maxretries - maximum number of retries, default 3
            - priority - default 1
    
        Returns:
            - the URI under which the freesite can be retrieved
        """
        # alloc a job ID for FCP
        id = self._getUniqueId()
    
        # get keyword args
        dir = kw['dir']
        sitename = kw.get('name', 'freesite')
        usk = kw.get('usk', False)
        version = kw.get('version', 0)
        maxretries = kw.get('maxretries', 3)
        priority = kw.get('priority', 1)
    
        # derive final URI for insert
        uriFull = uri + sitename + "/"
        if kw.get('usk', False):
            uriFull += "%d/" % int(version)
            uriFull = uriFull.replace("SSK@", "USK@")
    
        # issue the command
        #self._sendMessage("ClientPutComplexDir", True, **opts)
        msgLines = ["ClientPutComplexDir",
                    "Identifier=%s" % id,
                    "Verbosity=0",
                    "MaxRetries=%s" % maxretries,
                    "PriorityClass=%s" % priority,
                    "URI=%s" % uriFull,
                    ]
        n = 0
        manifest = readdir(kw['dir'])
    
        default = None
        for file in manifest:
            relpath = file['relpath']
            fullpath = file['fullpath']
            mimetype = file['mimetype']
    
            if relpath == 'index.html':
                default = file
            print "n=%s relpath=%s" % (repr(n), repr(relpath))
    
            msgLines.extend(["Files.%d.Name=%s" % (n, relpath),
                             "Files.%d.UploadFrom=disk" % n,
                             "Files.%d.Filename=%s" % (n, fullpath),
                             ])
            n += 1
    
        # now, add the default file
        msgLines.extend(["Files.%d.Name=" % n,
                         "Files.%d.UploadFrom=disk" % n,
                         "Files.%d.Filename=%s" % (n, default['fullpath']),
                         ])
    
        msgLines.append("EndMessage")
        
        for line in msgLines:
            self._log(DETAIL, line)
        fullbuf = "\n".join(msgLines) + "\n"
        self.socket.send(fullbuf)
    
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
    
    #@-node:putdir
    #@+node:genkey
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
            #print resp
            if resp['header'] == 'SSKKeypair' and str(resp['Identifier']) == id:
                break
    
        return resp['RequestURI'], resp['InsertURI']
    
    #@-node:genkey
    #@-others
    
    
    
    #@-node:High Level Methods
    #@+node:Receiver Thread
    # methods for receiver thread
    
    #@+others
    #@+node:_rxThread
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
            
    #@-node:_rxThread
    #@-others
    
    #@-node:Receiver Thread
    #@+node:Low Level Methods
    # low level noce comms methods
    
    #@+others
    #@+node:_getUniqueId
    def _getUniqueId(self):
        return "id" + str(int(time.time() * 1000000))
    
    #@-node:_getUniqueId
    #@+node:_sendMessage
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
    
    #@-node:_sendMessage
    #@+node:_receiveMessage
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
                if chunk:
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
    
    #@-node:_receiveMessage
    #@+node:_log
    def _log(self, level, msg):
        """
        Logs a message. If level > verbosity, don't output it
        """
        if level > self.verbosity:
            return
    
        if not msg.endswith("\n"): msg += "\n"
        self.logfile.write(msg)
        self.logfile.flush()
    
    #@-node:_log
    #@-others
    #@-node:Low Level Methods
    #@+node:class JobTicket
    class JobTicket:
        """
        A JobTicket is an object returned to clients making
        asynchronous requests. It puts them in control of how
        they manage n concurrent requests.
        
        When you as a client receive a JobTicket, you can choose to:
            - block, awaiting completion of the job
            - poll the job for completion status
            - receive a callback upon completion
        """
        #@    @+others
        #@+node:__init__
        def __init__(self, id):
            """
            You should never instantiate a JobTicket object yourself
            """
            self.id = id
            self.queue = Queue.Queue()
        
        #@-node:__init__
        #@+node:isDone
        def isComplete(self):
            """
            Returns True if the job has been completed
            """
        
        #@-node:isDone
        #@+node:wait
        def wait(self, timeout=None):
            """
            Waits forever (or for a given timeout) for a job to complete
            """
        #@-node:wait
        #@-others
    
    #@-node:class JobTicket
    #@-others

#@-node:class FCPNodeConnection
#@+node:XML-RPC Server
#@+others
#@+node:class FreenetXMLRPCRequest
class FreenetXMLRPCRequest:
    """
    Simple class which exposes basic primitives
    for freenet xmlrpc server
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, **kw):
    
        self.kw = kw
    
    #@-node:__init__
    #@+node:_getNode
    def _getNode(self):
        
        node = FCPNodeConnection(**self.kw)
        node.hello()
        return node
    
    #@-node:_getNode
    #@+node:_hello
    def _hello(self):
        
        self.node.hello()
    
    #@-node:_hello
    #@+node:hello
    def hello(self):
        """
        pings the FCP interface. just creates the connection,
        sends a hello, then closes
        """
        if options==None:
            options = {}
    
        node = self._getNode()
    
    #@-node:hello
    #@+node:get
    def get(self, uri, options=None):
        """
        Performs a fetch of a key
    
        Arguments:
            - uri - the URI to retrieve
            - options - a mapping (dict) object containing various
              options - refer to FCPNodeConnection.get documentation
        """
        if options==None:
            options = {}
    
        node = self._getNode()
    
        return node.get(uri, **options)
    
    #@-node:get
    #@+node:put
    def put(self, uri, options=None):
        """
        Inserts data to node
    
        Arguments:
            - uri - the URI to insert under
            - options - a mapping (dict) object containing various
              options - refer to FCPNodeConnection.get documentation
        """
        if options==None:
            options = {}
    
        node = self._getNode()
    
        return node.put(uri, data=data, **options)
    
    #@-node:put
    #@+node:genkey
    def genkey(self):
        
        node = self._getNode()
    
        return self.node.genkey()
    
    #@-node:genkey
    #@-others

#@-node:class FreenetXMLRPCRequest
#@+node:runServer
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
    server.register_introspection_methods()
    server.serve_forever()

#@-node:runServer
#@+node:testServer
def testServer():
    
    runServer(host="", fcpHost="10.0.0.1", verbosity=DETAIL)

#@-node:testServer
#@-others

#@-node:XML-RPC Server
#@+node:util funcs
#@+others
#@+node:toBool
def toBool(arg):
    try:
        arg = int(arg)
        if arg:
            return "true"
    except:
        pass
    
    if isinstance(arg, str):
        if arg.strip().lower()[0] == 't':
            return "true"
        else:
            return "false"
    
    if arg:
        return True
    else:
        return False

#@-node:toBool
#@+node:readdir
def readdir(dirpath, prefix='', gethashes=False):
    """
    Reads a directory, returning a sequence of file dicts.

    Arguments:
      - dirpath - relative or absolute pathname of directory to scan
      - gethashes - also include a 'hash' key in each file dict, being
        the SHA1 hash of the file's name and contents
      
    Each returned dict in the sequence has the keys:
      - fullpath - usable for opening/reading file
      - relpath - relative path of file (the part after 'dirpath'),
        for the 'SSK@blahblah//relpath' URI
      - mimetype - guestimated mimetype for file
    """

    #set_trace()
    #print "dirpath=%s, prefix='%s'" % (dirpath, prefix)
    entries = []
    for f in os.listdir(dirpath):
        relpath = prefix + f
        fullpath = dirpath + "/" + f
        if f == '.freesiterc':
            continue
        if os.path.isdir(fullpath):
            entries.extend(readdir(dirpath+"/"+f, relpath + "/", gethashes))
        else:
            #entries[relpath] = {'mimetype':'blah/shit', 'fullpath':dirpath+"/"+relpath}
            fullpath = dirpath + "/" + f
            entry = {'relpath' :relpath,
                     'fullpath':fullpath,
                     'mimetype':guessMimetype(f)
                     }
            if gethashes:
                h = sha.new(relpath)
                fobj = file(fullpath, "rb")
                while True:
                    buf = fobj.read(262144)
                    if len(buf) == 0:
                        break
                    h.update(buf)
                fobj.close()
                entry['hash'] = h.hexdigest()
            entries.append(entry)
    entries.sort(lambda f1,f2: cmp(f1['relpath'], f2['relpath']))

    return entries

#@-node:readdir
#@+node:guessMimetype
def guessMimetype(filename):
    """
    Returns a guess of a mimetype based on a filename's extension
    """
    m = mimetypes.guess_type(filename, False)[0]
    if m == None:
        m = "text/plain"
    return m
#@-node:guessMimetype
#@-others

#@-node:util funcs
#@+node:usage
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

#@-node:usage
#@+node:main
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



#@-node:main
#@+node:mainline
if __name__ == '__main__':
    
    main()

#@-node:mainline
#@-others

#@-node:@file fcp.py
#@-leo
