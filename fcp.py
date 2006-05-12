#!/usr/bin/env python
"""
An implementation of a freenet client library for
FCP v2, offering considerable flexibility.

Clients should instantiate FCPNodeConnection, then execute
its methods to perform tasks with FCP.

This module was written by aum, May 2006, released under the GNU Lesser General
Public License.

No warranty, yada yada

"""

import sys, os, socket, time, thread
import threading, mimetypes, sha, Queue
import select, traceback

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
    Represents an interface to a freenet node via its FCP port,
    and exposes primitives for the basic genkey, get, put and putdir
    operations.
    
    Only one instance of FCPNodeConnection is needed across an entire
    running client application, because its methods are quite thread-safe.
    Creating 2 or more instances is a waste of resources.

    Clients, when invoking methods, have several options regarding flow
    control and event notification:

        - synchronous call (the default). Here, no pending status messages
          will ever be seen, and the call will only control when it has
          completed (successfully, or otherwise)
        
        - asynchronous call - this is invoked by passing the keyword argument
          'async=True' to any of the main primitives. When a primitive is invoked
          asynchronously, it will return a 'job ticket object' immediately. This
          job ticket has methods for polling for job completion, or blocking
          awaiting completion
        
        - setting a callback. You can pass to any of the primitives a
          'callback=somefunc' keyword arg, where 'somefunc' is a callable object
           conforming to::
               
               def somefunc(status, value):
                   ...
          
          The callback function will be invoked when a primitive succeeds or fails,
          as well as when a pending message is received from the node.
          
          The 'status' argument passed will be one of:
              - 'successful' - the primitive succeeded, and 'value' will contain
                the result of the primitive
              - 'pending' - the primitive is still executing, and 'value' will
                contain the raw pending message sent back from the node, as a
                dict
              - 'failed' - the primitive failed, and as with 'pending', the
                argument 'value' contains a dict containing the message fields
                sent back from the node

          Note that callbacks can be set in both synchronous and asynchronous
          calling modes.

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
    
    def genkey(self, **kw):
        """
        Generates and returns an SSK keypair
        
        Keywords:
            - async - whether to do this call asynchronously, and
              return a JobTicket object
            - callback - if given, this should be a callable which accepts 2
              arguments:
                  - status - will be one of 'successful', 'failed' or 'pending'
                  - value - depends on status:
                      - if status is 'successful', this will contain the value
                        returned from the command
                      - if status is 'failed' or 'pending', this will contain
                        a dict containing the response from node
        """
        id = self._getUniqueId()
        
        return self._submitCmd(id, "GenerateSSK", Identifier=id, **kw)
    
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
        self._log(INFO, "get: uri=%s" % uri)
    
        # ---------------------------------
        # format the request
        opts = {}
    
        id = self._getUniqueId()
    
        opts['async'] = kw.pop('async', False)
        if kw.has_key('callback'):
            opts['callback'] = kw['callback']
    
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
    
        # ---------------------------------
        # now enqueue the request
        return self._submitCmd(id, "ClientGet", **opts)
    
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
        self._log(INFO, "put: uri=%s" % uri)
    
        # divert to putdir if dir keyword present
        if kw.has_key('dir'):
            return self.putdir(uri, **kw)
    
        # ---------------------------------
        # format the request
        opts = {}
    
        opts['async'] = kw.get('async', False)
        if kw.has_key('callback'):
            opts['callback'] = kw['callback']
    
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
    
        # ---------------------------------
        # now dispatch the job
        return self._submitCmd(id, "ClientPut", **opts)
    
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
        self._log(INFO, "putdir: uri=%s dir=%s" % (uri, kw['dir']))
    
        # -------------------------------------
        # format the command
        # 
        # note that with this primitive, we have to format the command
        # buffer ourselves, not just drop it through as a bunch of keywords,
        # since we want to control the order of keyword lines
    
        # get keyword args
        dir = kw['dir']
        sitename = kw.get('name', 'freesite')
        usk = kw.get('usk', False)
        version = kw.get('version', 0)
        maxretries = kw.get('maxretries', 3)
        priority = kw.get('priority', 1)
    
        id = self._getUniqueId()
    
        # derive final URI for insert
        uriFull = uri + sitename + "/"
        if kw.get('usk', False):
            uriFull += "%d/" % int(version)
            uriFull = uriFull.replace("SSK@", "USK@")
    
        # build a big command buffer
        msgLines = ["ClientPutComplexDir",
                    "Identifier=%s" % id,
                    "Verbosity=0",
                    "MaxRetries=%s" % maxretries,
                    "PriorityClass=%s" % priority,
                    "URI=%s" % uriFull,
                    ]
    
        # scan directory and add its files
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
    
        # --------------------------------------
        # now dispatch the job
        return self._submitCmd(id, "ClientPutComplexDir",
                               rawcmd=fullbuf,
                               async=kw.get('async', False),
                               callback=kw.get('callback', False),
                               )
    
    def shutdown(self):
        """
        Terminates the manager thread
        
        You should explicitly shutdown any existing nodes
        before exiting your client application
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
        This thread is the nucleus of pyfcp, and coordinates incoming
        client commands and incoming node responses
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
            - callback - a function taking 2 args 'status' and 'value'.
              Status is one of 'successful', 'pending' or 'failed'.
              value is the primitive return value if successful, or the raw
              node message if pending or failed
            - rawcmd - a raw command buffer to send directly
            - options specific to command such as 'URI'
        
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
        Handles incoming messages from node
        
        If an incoming message represents the termination of a command,
        the job ticket object will be notified accordingly
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
            keys = (msg['RequestURI'], msg['InsertURI'])
            job.callback('successful', keys)
            job._putResult(keys)
    
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
                result = (mimetype, job.kw['Filename'])
                job.callback('successful', result)
                job._putResult(result)
                del self.jobs[id]
                return
    
            elif job.kw['ReturnType'] == 'none':
                result = (mimetype, 1)
                job.callback('successful', result)
                job._putResult(result)
                del self.jobs[id]
                return
    
            # otherwise, we're expecting an AllData and will react to it then
            else:
                job.callback('pending', msg)
                job.mimetype = mimetype
                return
    
        if hdr == 'AllData':
            result = (job.mimetype, msg['Data'])
            job.callback('successful', result)
            job._putResult(result)
            del self.jobs[id]
            return
    
        if hdr == 'GetFailed':
            # return an exception
            job.callback("failed", msg)
            job._putResult(FCPGetFailed(msg))
            del self.jobs[id]
            return
    
        # -----------------------------
        # handle ClientPut responses
    
        if hdr == 'URIGenerated':
    
            job.uri = msg['URI']
            newUri = msg['URI']
            job.callback('pending', msg)
    
            return
    
            # bail here if no data coming back
            if job.kw.get('GetCHKOnly', False) == 'true':
                # done - only wanted a CHK
                job._putResult(newUri)
                del self.jobs[id]
                return
    
        if hdr == 'PutSuccessful':
            result = msg['URI']
            job.callback('successful', result)
            job._putResult(result)
            del self.jobs[id]
            return
    
        if hdr == 'PutFailed':
            job.callback('failed', msg)
            job._putResult(FCPPutFailed(msg))
            del self.jobs[id]
            return
    
        # -----------------------------
        # handle progress messages
    
        if hdr == 'StartedCompression':
            job.callback('pending', msg)
            return
    
        if hdr == 'FinishedCompression':
            job.callback('pending', msg)
            return
    
        if hdr == 'SimpleProgress':
            job.callback('pending', msg)
            return
    
        # -----------------------------
        # handle persistent job messages
    
        if hdr == 'PersistentGet':
            job.callback('pending', msg)
            return
    
        if hdr == 'PersistentPut':
            job.callback('pending', msg)
            return
    
        if hdr == 'EndListPersistentRequests':
            job.callback('pending', msg)
            return
    
        if hdr == 'PersistentPutDir':
            job.callback('pending', msg)
            return
    
        # -----------------------------
        # handle various errors
    
        if hdr == 'ProtocolError':
            job.callback('failed', msg)
            job._putResult(FCPProtocolError(msg))
            del self.jobs[id]
            return
    
        if hdr == 'IdentifierCollision':
            log(ERROR, "IdentifierCollision on id %s ???" % id)
            job.callback('failed', msg)
            job._putResult(Exception("Duplicate job identifier %s" % id))
            del self.jobs[id]
            return
    
        # -----------------------------
        # wtf is happening here?!?
    
        log(ERROR, "Unknown message type from node: %s" % hdr)
        job.callback('failed', msg)
        job._putResult(FCPException(msg))
        del self.jobs[id]
        return
    
    def _on_clientReq(self, req):
        """
        takes an incoming requests from client and transmits it to
        the fcp port, and also registers it so the manager thread
        can action responses from the fcp port.
        """
        id = req.id
        cmd = req.cmd
        kw = req.kw
    
        # register the req
        self.jobs[id] = req
        
        # now can send, since we're the only one who will
        self._txMsg(cmd, **kw)
    
    
    # low level noce comms methods
    
    def _hello(self):
        """
        perform the initial FCP protocol handshake
        """
        self._txMsg("ClientHello", 
                         Name=self.name,
                         ExpectedVersion=expectedVersion)
        
        resp = self._rxMsg()
        return resp
    
    def _getUniqueId(self):
        """
        Allocate a unique ID for a request
        """
        return "id" + str(int(time.time() * 1000000))
    
    def _txMsg(self, msgType, **kw):
        """
        low level message send
        
        Arguments:
            - msgType - one of the FCP message headers, such as 'ClientHello'
            - args - zero or more (keyword, value) tuples
        Keywords:
            - rawcmd - if given, this is the raw buffer to send
            - other keywords depend on the value of msgType
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
    
        callback = kw.pop('callback', None)
        if callback:
            self.callback = callback
    
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
    
    def callback(self, status, value):
        """
        This will be replaced in job ticket instances wherever
        user provides callback arguments
        """
        # no action needed
    
    def _putResult(self, result):
        """
        Called by manager thread to indicate job is complete,
        and submit a result to be picked up by client
        """
        self.result = result
        self.lock.release()
    

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


