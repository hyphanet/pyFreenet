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

import sys, os, socket, time, thread
import threading, mimetypes, sha, Queue
import select, traceback

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

# where we can find the freenet node FCP port
defaultFCPHost = "127.0.0.1"
defaultFCPPort = 9481

# where to listen, for the xml-rpc server
xmlrpcHost = "127.0.0.1"
xmlrpcPort = 19481

# poll timeout period for manager thread
pollTimeout = 0.1
#pollTimeout = 3

# list of keywords sent from node to client, which have
# int values
intKeys = [
    'DataLength', 'Code',
    ]

# for the FCP 'ClientHello' handshake
expectedVersion="2.0"

# logger verbosity levels
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
        # grab and save parms
        self.name = kw.get('clientName', self._getUniqueId())
        self.host = kw.get('host', defaultFCPHost)
        self.port = kw.get('port', defaultFCPPort)
    
        # set up the logger
        logfile = kw.get('logfile', sys.stderr)
        if not hasattr(logfile, 'write'):
            # might be a pathname
            if not isinstance(logfile, str):
                raise Exception("Bad logfile, must be pathname or file object")
            logfile = file(logfile, "a")
        self.logfile = logfile
        self.verbosity = kw.get('verbosity', 0)
    
        # try to connect to node
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
    
        # now do the hello
        self._hello()
    
        # the pending job tickets
        self.jobs = {} # keyed by request ID
    
        # queue for incoming client requests
        self.clientReqQueue = Queue.Queue()
    
        # launch receiver thread
        self.running = True
        thread.start_new_thread(self._mgrThread, ())
    
    def __del__(self):
        """
        object is getting cleaned up, so disconnect
        """
        # terminate the node
        try:
            self.shutdown()
        except:
            traceback.print_exc()
            pass
    
    # high level client methods
    
    def _hello(self):
        
        self._txMsg("ClientHello", 
                         Name=self.name,
                         ExpectedVersion=expectedVersion)
        
        resp = self._rxMsg()
        return resp
    
    def genkey(self, **kw):
        """
        Generates and returns an SSK keypair
        
        Keywords:
            - async - whether to do this call asynchronously, and
              return a JobTicket object
        """
        id = self._getUniqueId()
        
        return self._submitCmd(id, "GenerateSSK", Identifier=id, **kw)
    
        #self._txMsg("GenerateSSK",
        #                 Identifier=id)
        #while True:
        #    resp = self._rxMsg()
        #    #print resp
        #    if resp['header'] == 'SSKKeypair' and str(resp['Identifier']) == id:
        #        break
        #return resp['RequestURI'], resp['InsertURI']
    
    def get(self, uri, **kw):
        """
        Does a direct get of a key
    
        Keywords:
            - async - whether to return immediately with a job ticket object, default
              False (wait for completion)
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
        # format the request
        opts = {}
    
        id = self._getUniqueId()
    
        opts['async'] = kw.pop('async', False)
    
        file = kw.pop("file", None)
        if file:
            opts['ReturnType'] = "disk"
            #opts['File'] = file
            opts['Filename'] = file
    
        elif opts.get('nodata', False):
            nodata = True
            opts['ReturnType'] = "none"
        else:
            nodata = False
            opts['ReturnType'] = "direct"
        
        opts['Identifier'] = id
        
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
    
        # now enqueue the request
        return self._submitCmd(id, "ClientGet", **opts)
    
    
    
        # ------------------------------------------------
        # DEPRECATED CODE!!
    
        self._txMsg("ClientGet", **opts)
       
    
        # get a response
        resp = self._rxMsg()
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
                resp = self._rxMsg()
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
            - async - whether to do the job asynchronously, returning a job ticket
              object (default False)
    
        Notes:
            - exactly one of 'file', 'data' or 'dir' keyword arguments must be present
        """
    
        # divert to putdir if dir keyword present
        if kw.has_key('dir'):
            return self.putdir(uri, **kw)
    
        opts = {}
    
        opts['async'] = kw.get('async', False)
    
        opts['URI'] = uri
        opts['Metadata.ContentType'] = kw.get("mimetype", "text/plain")
        id = self._getUniqueId()
        opts['Identifier'] = id
        opts['Verbosity'] = 0
        opts['MaxRetries'] = kw.get("maxretries", 3)
        opts['PriorityClass'] = kw.get("priority", 1)
        opts['GetCHKOnly'] = toBool(kw.get("chkonly", "false"))
        opts['DontCompress'] = toBool(kw.get("nocompress", "false"))
    
        if kw.has_key("file"):
            opts['UploadFrom'] = "disk"
            opts['Filename'] = kw['file']
            if not kw.has_key("mimetype"):
                opts['Metadata.ContentType'] = mimetypes.guess_type(kw['file'])[0] or "text/plain"
    
        elif kw.has_key("data"):
            opts["UploadFrom"] = "direct"
            opts["Data"] = kw['data']
    
        elif kw.has_key("redirect"):
            opts["UploadFrom"] = "redirect"
            opts["TargetURI"] = kw['redirect']
        else:
            raise Exception("Must specify file, data or redirect keywords")
    
        #print "sendEnd=%s" % sendEnd
    
        # now dispatch the job
        return self._submitCmd(id, "ClientPut", **opts)
    
    
        # ------------------------------------------------------------
        # DEPRECATED CODE
    
        # issue the command
        self._txMsg("ClientPut", **opts)
    
        # expect URIGenerated
        resp1 = self._rxMsg()
        hdr = resp1['header']
        if hdr != 'URIGenerated':
            raise FCPException(resp1)
    
        newUri = resp1['URI']
    
        # bail here if no data coming back
        if opts.get('UploadFrom', None) == 'redirect' or opts['GetCHKOnly'] == 'true':
            if not kw.has_key('redirect'):
                return newUri
        
        # expect outcome
        resp2 = self._rxMsg()
        hdr = resp2['header']
        if hdr == 'PutSuccessful':
            return resp2['URI']
        elif hdr == 'PutFailed':
            raise FCPPutFailed(resp2)
        elif hdr == 'ProtocolError':
            raise FCPProtocolError(resp2)
        else:
            raise FCPException(resp2)
    
    
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
    
            - async - default False - if True, return a job ticket
    
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
        #self._txMsg("ClientPutComplexDir", True, **opts)
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
    
        # now dispatch the job
        return self._submitCmd(id, "ClientPutComplexDir",
                               rawcmd=fullbuf,
                               async=kw.get('async', False),
                               )
    
        # ------------------------------------------------------------
        # DEPRECATED CODE
    
    
        self.socket.send(fullbuf)
    
        # expect URIGenerated
        resp1 = self._rxMsg()
        hdr = resp1['header']
        if hdr != 'URIGenerated':
            raise FCPException(resp1)
    
        newUri = resp1['URI']
    
        # expect outcome
        resp2 = self._rxMsg()
        hdr = resp2['header']
        if hdr == 'PutSuccessful':
            return resp2['URI']
        elif hdr == 'PutFailed':
            raise FCPPutFailed(resp2)
        elif hdr == 'ProtocolError':
            raise FCPProtocolError(resp2)
        else:
            raise FCPException(resp2)
    
    
    def shutdown(self):
        """
        Terminates the manager thread
        """
        self.running = False
    
        # give the manager thread a chance to bail out
        time.sleep(pollTimeout * 3)
    
        # shut down FCP connection
        if hasattr(self, 'socket'):
            self.socket.close()
            del self.socket
    
        # and close the logfile
        if self.logfile not in [sys.stdout, sys.stderr]:
            self.logfile.close()
    
    
    
    
    
    # methods for manager thread
    
    def _mgrThread(self):
        """
        Receives all incoming messages
        """
        log = self._log
        try:
            while self.running:
    
                log(DEBUG, "Top of manager thread")
    
                # try for incoming messages from node
                log(DEBUG, "Testing for incoming message")
                if self._msgIncoming():
                    log(DEBUG, "Retrieving incoming message")
                    msg = self._rxMsg()
                    log(DEBUG, "Got incoming message, dispatching")
                    self._on_rxMsg(msg)
                    log(DEBUG, "back from on_rxMsg")
                else:
                    log(DEBUG, "No incoming message from node")
        
                # try for incoming requests from clients
                log(DEBUG, "Testing for client req")
                try:
                    req = self.clientReqQueue.get(True, pollTimeout)
                    log(DEBUG, "Got client req, dispatching")
                    self._on_clientReq(req)
                    log(DEBUG, "Back from on_clientReq")
                except Queue.Empty:
                    log(DEBUG, "No incoming client req")
                    pass
    
            self._log(INFO, "Manager thread terminated normally")
            return
    
        except:
            traceback.print_exc()
            self._log(CRITICAL, "manager thread crashed")
    
    def _msgIncoming(self):
        """
        Returns True if a message is coming in from the node
        """
        return len(select.select([self.socket], [], [], pollTimeout)[0]) > 0
    
    def _submitCmd(self, id, cmd, **kw):
        """
        Submits a command for execution
        
        Arguments:
            - id - the command identifier
            - cmd - the command name, such as 'ClientPut'
        
        Keywords:
            - async - whether to return a JobTicket object, rather than
              the command result
            - rawcmd - a raw command buffer to send directly
            - options specific to command
        
        Returns:
            - if command is sent in sync mode, returns the result
            - if command is sent in async mode, returns a JobTicket
              object which the client can poll or block on later
        """
        async = kw.pop('async', False)
        job = JobTicket(id, cmd, kw)
        self.clientReqQueue.put(job)
    
        self._log(DEBUG, "_submitCmd: id=%s cmd=%s kw=%s" % (id, cmd, str(kw)[:256]))
    
        if async:
            return job
        else:
            return job.wait()
    
    def _on_rxMsg(self, msg):
        """
        Handler for incoming messages from node
        """
        log = self._log
    
        # find the job this relates to
        id = msg['Identifier']
        hdr = msg['header']
    
        job = self.jobs.get(id, None)
        
        # bail if job not known
        if not job:
            log(ERROR, "Received %s for unknown job %s" % (hdr, id))
            return
    
        # action from here depends on what kind of message we got
    
        # -----------------------------
        # handle GenerateSSK responses
    
        if hdr == 'SSKKeypair':
            # got requested keys back
            job._putResult((msg['RequestURI'], msg['InsertURI']))
    
            # and remove job from queue
            self.jobs.pop(id, None)
            return
    
        # -----------------------------
        # handle ClientGet responses
    
        if hdr == 'DataFound':
            mimetype = msg['Metadata.ContentType']
            if job.kw.has_key('Filename'):
                # already stored to disk, done
                #resp['file'] = file
                job._putResult((mimetype, job.kw['Filename']))
                del self.jobs[id]
                return
    
            elif job.kw['ReturnType'] == 'none':
                job._putResult((mimetype, 1))
                del self.jobs[id]
                return
    
            # otherwise, we're expecting an AllData and will react to it then
            else:
                job.mimetype = mimetype
                return
    
        if hdr == 'AllData':
            job._putResult((job.mimetype, msg['Data']))
            del self.jobs[id]
            return
    
        if hdr == 'GetFailed':
            # return an exception
            job._putResult(FCPGetFailed(msg))
            del self.jobs[id]
            return
    
        # -----------------------------
        # handle ClientPut responses
    
        if hdr == 'URIGenerated':
    
            job.uri = msg['URI']
            newUri = msg['URI']
    
            return
    
            # bail here if no data coming back
            if job.kw.get('GetCHKOnly', False) == 'true':
                # done - only wanted a CHK
                job._putResult(newUri)
                del self.jobs[id]
                return
    
        if hdr == 'PutSuccessful':
            job._putResult(msg['URI'])
            del self.jobs[id]
            return
    
        if hdr == 'PutFailed':
            job._putResult(FCPPutFailed(msg))
            del self.jobs[id]
            return
    
        # -----------------------------
        # handle progress messages
    
        if hdr == 'StartedCompression':
            job.notify(msg)
            return
    
        if hdr == 'FinishedCompression':
            job.notify(msg)
            return
    
        if hdr == 'SimpleProgress':
            return
    
        # -----------------------------
        # handle persistent job messages
    
        if hdr == 'PersistentGet':
            return
    
        if hdr == 'PersistentPut':
            return
    
        if hdr == 'EndListPersistentRequests':
            return
    
        if hdr == 'PersistentPutDir':
            return
    
        # -----------------------------
        # handle various errors
    
        if hdr == 'ProtocolError':
            job._putResult(FCPProtocolError(msg))
            del self.jobs[id]
            return
    
        if hdr == 'IdentifierCollision':
            log(ERROR, "IdentifierCollision on id %s ???" % id)
            job._putResult(Exception("Duplicate job identifier %s" % id))
            del self.jobs[id]
            return
    
        # -----------------------------
        # wtf is happening here?!?
    
        log(ERROR, "Unknown message type from node: %s" % hdr)
        job._putResult(FCPException(msg))
        del self.jobs[id]
        return
    
    def _on_clientReq(self, req):
        """
        handler for incoming requests from clients
        """
        id = req.id
        cmd = req.cmd
        kw = req.kw
    
        # register the req
        self.jobs[id] = req
        
        # now can send, since we're the only one who will
        self._txMsg(cmd, **kw)
    
    
    # low level noce comms methods
    
    def _getUniqueId(self):
        return "id" + str(int(time.time() * 1000000))
    
    def _txMsg(self, msgType, **kw):
        """
        low level message send
        
        Arguments:
            - msgType - one of the FCP message headers, such as 'ClientHello'
            - args - zero or more (keyword, value) tuples
        Keywords:
            - rawcmd - if given, this is the raw buffer to send
        """
        log = self._log
    
        # just send the raw command, if given    
        rawcmd = kw.get('rawcmd', None)
        if rawcmd:
            self.socket.send(rawcmd)
            log(DETAIL, "CLIENT: %s" % rawcmd)
            return
    
        if kw.has_key("Data"):
            data = kw.pop("Data")
            sendEndMessage = False
        else:
            data = None
            sendEndMessage = True
    
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
    
    def _rxMsg(self):
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
    
    def _log(self, level, msg):
        """
        Logs a message. If level > verbosity, don't output it
        """
        if level > self.verbosity:
            return
    
        if not msg.endswith("\n"): msg += "\n"
        self.logfile.write(msg)
        self.logfile.flush()
    

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
    def __init__(self, id, cmd, kw):
        """
        You should never instantiate a JobTicket object yourself
        """
        self.id = id
        self.cmd = cmd
        self.kw = kw
    
        self.lock = threading.Lock()
        self.lock.acquire()
        self.result = None
    
    def isComplete(self):
        """
        Returns True if the job has been completed
        """
        return self.result != None
    
    def wait(self, timeout=None):
        """
        Waits forever (or for a given timeout) for a job to complete
        """
        self.lock.acquire()
        self.lock.release()
        if isinstance(self.result, Exception):
            raise self.result
        else:
            return self.result
    
    def _putResult(self, result):
        """
        Called by manager thread to indicate job is complete,
        and submit a result to be picked up by client
        """
        self.result = result
        self.lock.release()
    

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
    
    def hello(self):
        """
        pings the FCP interface. just creates the connection,
        sends a hello, then closes
        """
        if options==None:
            options = {}
    
        node = self._getNode()
    
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
    server.register_introspection_methods()
    server.serve_forever()

def testServer():
    
    runServer(host="", fcpHost="10.0.0.1", verbosity=DETAIL)


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

def guessMimetype(filename):
    """
    Returns a guess of a mimetype based on a filename's extension
    """
    m = mimetypes.guess_type(filename, False)[0]
    if m == None:
        m = "text/plain"
    return m

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


