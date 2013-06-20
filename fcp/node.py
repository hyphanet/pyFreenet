#!/usr/bin/env python
# encoding: utf-8
#@+leo-ver=4
#@+node:@file node.py
#@@first
"""
An implementation of a freenet client library for
FCP v2, offering considerable flexibility.

Clients should instantiate FCPNode, then execute
its methods to perform tasks with FCP.

This module was written by aum, May 2006, released under the GNU Lesser General
Public License.

No warranty, yada yada

For FCP documentation, see http://wiki.freenetproject.org/FCPv2

"""

#@+others
#@+node:imports
import Queue
import base64
import mimetypes
import os
import pprint
import random
import select
# [sha](http://docs.python.org/2/library/sha.html) has been deprecated
# in favor of [hashlib](http://docs.python.org/2/library/hashlib.html)
# since Python 2.5.
# on pyhton < 2.5, distutils will automatically install hashlib from pypi.
import hashlib
import socket
import stat
import sys
import tempfile
import thread
import threading
import time
import traceback

import pseudopythonparser

#@-node:imports
#@+node:exceptions
class ConnectionRefused(Exception):
    """
    cannot connect to given host/port
    """

class PrivacyRisk(Exception):
    """
    The following code would pose a privacy risk
    """

class FCPException(Exception):
    
    def __init__(self, info=None, **kw):
        #print "Creating fcp exception"
        if not info:
            info = kw
        self.info = info
        #print "fcp exception created"
        Exception.__init__(self, str(info))
    
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

class FCPNodeFailure(Exception):
    """
    node seems to have died
    """

class FCPSendTimeout(FCPException):
    """
    timed out waiting for command to be sent to node
    """
    pass

class FCPNodeTimeout(FCPException):
    """
    timed out waiting for node to respond
    """

class FCPNameLookupFailure(Exception):
    """
    name services name lookup failed
    """

#@-node:exceptions
#@+node:globals
# where we can find the freenet node FCP port
defaultFCPHost = "127.0.0.1"
defaultFCPPort = 9481
defaultFProxyHost = "127.0.0.1"
defaultFProxyPort = 8888

# may set environment vars for FCP host/port
if os.environ.has_key("FCP_HOST"):
    defaultFCPHost = os.environ["FCP_HOST"].strip()
if os.environ.has_key("FCP_PORT"):
    defaultFCPPort = int(os.environ["FCP_PORT"].strip())

# ditto for fproxy host/port
if os.environ.has_key("FPROXY_HOST"):
    defaultFProxyHost = os.environ["FPROXY_HOST"].strip()
if os.environ.has_key("FPROXY_PORT"):
    defaultFProxyPort = int(os.environ["FPROXY_PORT"].strip())

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
NOISY = 7

# peer note types
PEER_NOTE_PRIVATE_DARKNET_COMMENT = 1

defaultVerbosity = ERROR

ONE_YEAR = 86400 * 365

#@<<fcp_version>>
#@+node:<<fcp_version>>
fcpVersion = "0.2.5"

#@-node:<<fcp_version>>
#@nl

#@-node:globals
#@+node:class FCPNode
class FCPNode:
    """
    Represents an interface to a freenet node via its FCP port,
    and exposes primitives for the basic genkey, get, put and putdir
    operations as well as peer management primitives.
    
    Only one instance of FCPNode is needed across an entire
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
          conforming to 'def somefunc(status, value)'
          
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
    
    svnLongRevision = "$Revision$"
    svnRevision = svnLongRevision[ 11 : -2 ]
    
    #@    @+others
    #@+node:attribs
    noCloseSocket = True
    
    nodeIsAlive = False
    
    nodeVersion = None;
    nodeFCPVersion = None;
    nodeBuild = None;
    nodeRevision = None;
    nodeExtBuild = None;
    nodeExtRevision = None;
    nodeIsTestnet = None;
    
    #@-node:attribs
    #@+node:__init__
    def __init__(self, **kw):
        """
        Create a connection object
        
        Keyword Arguments:
            - name - name of client to use with reqs, defaults to random. This
              is crucial if you plan on making persistent requests
            - host - hostname, defaults to environment variable FCP_HOST, and
              if this doesn't exist, then defaultFCPHost
            - port - port number, defaults to environment variable FCP_PORT, and
              if this doesn't exist, then defaultFCPPort
            - logfile - a pathname or writable file object, to which log messages
              should be written, defaults to stdout unless logfunc is specified
            - logfunc - a function to which log messages should be written or None
              for no such function should be used, defaults to None
            - verbosity - how detailed the log messages should be, defaults to 0
              (silence)
            - socketTimeout - value to pass to socket object's settimeout() if
              available and the value is not None, defaults to None
    
        Attributes of interest:
            - jobs - a dict of currently running jobs (persistent and nonpersistent).
              keys are job ids and values are JobTicket objects
    
        Notes:
            - when the connection is created, a 'hello' handshake takes place.
              After that handshake, the node sends back a list of outstanding persistent
              requests left over from the last connection (based on the value of
              the 'name' keyword passed into this constructor).
              
              This object then wraps all this info into JobTicket instances and stores
              them in the self.persistentJobs dict
                                                           
        """
        # Be sure that we have all of our attributes during __init__
        self.running = False
        self.nodeIsAlive = False
        
        # grab and save parms
        env = os.environ
        self.name = kw.get('name', self._getUniqueId())
        self.host = kw.get('host', env.get("FCP_HOST", defaultFCPHost))
        self.port = kw.get('port', env.get("FCP_PORT", defaultFCPPort))
        self.port = int(self.port)
        self.socketTimeout = kw.get('socketTimeout', None)
        
        #: The id for the connection
        self.connectionidentifier = None
    
        # set up the logger
        logfile = kw.get('logfile', None)
        logfunc = kw.get('logfunc', None)
        if(None == logfile and None == logfunc):
            logfile = sys.stdout
        if(None != logfile and not hasattr(logfile, 'write')):
            # might be a pathname
            if not isinstance(logfile, str):
                raise Exception("Bad logfile '%s', must be pathname or file object" % logfile)
            logfile = file(logfile, "a")
        self.logfile = logfile
        self.logfunc = logfunc
        self.verbosity = kw.get('verbosity', defaultVerbosity)
    
        # try to connect to node
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if(None != self.socketTimeout):
            try:
                self.socket.settimeout(self.socketTimeout)
            except Exception, e:
                # Socket timeout setting is not available until Python 2.3, so ignore exceptions
                pass
        try:
            self.socket.connect((self.host, self.port))
        except Exception, e:
            raise Exception("Failed to connect to %s:%s - %s" % (self.host,
                                                                 self.port,
                                                                 e))
    
        # now do the hello
        self._hello()
        self.nodeIsAlive = True
    
        # the pending job tickets
        self.jobs = {} # keyed by request ID
        self.keepJobs = [] # job ids that should never be removed from self.jobs
    
        # queue for incoming client requests
        self.clientReqQueue = Queue.Queue()
    
        # launch receiver thread
        self.running = True
        self.shutdownLock = threading.Lock()
        thread.start_new_thread(self._mgrThread, ())
    
        # and set up the name service
        namesitefile = kw.get('namesitefile', None)
        self.namesiteInit(namesitefile)
    
    #@-node:__init__
    #@+node:__del__
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
    
    #@-node:__del__
    #@+node:FCP Primitives
    # basic FCP primitives
    
    #@+others
    #@+node:genkey
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
            - usk - default False - if True, returns USK uris
            - name - the path to put at end, optional
        """
        id = kw.pop("id", None)
        if not id:
            id = self._getUniqueId()
        
        pub, priv = self._submitCmd(id, "GenerateSSK", Identifier=id, **kw)
    
        name = kw.get("name", None)
        if name:
            pub = pub + name
            priv = priv + name
    
            if kw.get("usk", False):
                pub = pub.replace("SSK@", "USK@")+"/0"
                priv = priv.replace("SSK@", "USK@")+"/0"
    
        return pub, priv
    
    #@-node:genkey
    
    def fcpPluginMessage(self, **kw):
        """
        Sends an FCPPluginMessage and returns FCPPluginReply message contents
        
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
            - plugin_name - A name to identify the plugin. The same as class name
              shown on plugins page.
            - plugin_params - a dict() containing the key-value pairs to be sent
              to the plugin as parameters
        """
        
        id = kw.pop("id", None)
        if not id:
            id = self._getUniqueId()
            
        params = dict(PluginName = kw.get('plugin_name'),
                      Identifier = id,
                      async      = kw.get('async',False),
                      callback   = kw.get('callback',None))
        
        for key, val in kw.get('plugin_params',{}).iteritems():
            params.update({'Param.%s' % str(key) : val})
        
        return self._submitCmd(id, "FCPPluginMessage", **params)
    
    #@+node:get
    def get(self, uri, **kw):
        """
        Does a direct get of a key
    
        Keywords:
            - async - whether to return immediately with a job ticket object, default
              False (wait for completion)
            - persistence - default 'connection' - the kind of persistence for
              this request. If 'reboot' or 'forever', this job will be able to
              be recalled in subsequent FCP sessions. Other valid values are
              'reboot' and 'forever', as per FCP spec
            - Global - default false - if evaluates to true, puts this request
              on the global queue. Note the capital G in Global. If you set this,
              persistence must be 'reboot' or 'forever'
            - Verbosity - default 0 - sets the Verbosity mask passed in the
              FCP message - case-sensitive
            - priority - the PriorityClass for retrieval, default 2, may be between
              0 (highest) to 6 (lowest)
    
            - dsnly - whether to only check local datastore
            - ignoreds - don't check local datastore
    
            - file - if given, this is a pathname to which to store the retrieved key
            - followRedirect - follow a redirect if true, otherwise fail the get
            - nodata - if true, no data will be returned. This can be a useful
              test of whether a key is retrievable, without having to consume
              resources by retrieving it
            - stream - if given, this is a writeable file object, to which the
              received data should be written a chunk at a time
            - timeout - timeout for completion, in seconds, default one year
    
        Returns a 3-tuple, depending on keyword args:
            - if 'file' is given, returns (mimetype, pathname) if key is returned
            - if 'file' is not given, returns (mimetype, data, msg) if key is returned
            - if 'nodata' is true, returns (mimetype, 1) if key is returned
            - if 'stream' is given, returns (mimetype, None) if key is returned,
              because all the data will have been written to the stream
        If key is not found, raises an exception
        """
        self._log(INFO, "get: uri=%s" % uri)
    
        self._log(DETAIL, "get: kw=%s" % kw)
    
        # ---------------------------------
        # format the request
        opts = {}
    
        id = kw.pop("id", None)
        if not id:
            id = self._getUniqueId()
    
        opts['async'] = kw.pop('async', False)
        opts['followRedirect'] = kw.pop('followRedirect', False)
        opts['waituntilsent'] = kw.get('waituntilsent', False)
        if kw.has_key('callback'):
            opts['callback'] = kw['callback']
        opts['Persistence'] = kw.pop('persistence', 'connection')
        if kw.get('Global', False):
            print "global get"
            opts['Global'] = "true"
        else:
            opts['Global'] = "false"
    
        opts['Verbosity'] = kw.get('Verbosity', 0)
    
        if opts['Global'] == 'true' and opts['Persistence'] == 'connection':
            raise Exception("Global requests must be persistent")
    
        file = kw.pop("file", None)
        if file:
            # make sure we have an absolute path
            file = os.path.abspath(file)
            opts['ReturnType'] = "disk"
            #opts['File'] = file
            opts['Filename'] = file
            # need to do a TestDDARequest to have a chance of a
            # successful get to file.
            self.testDDA(Directory=os.path.dirname(file), 
                         WantWriteDirectory=True)
    
        elif kw.get('nodata', False):
            nodata = True
            opts['ReturnType'] = "none"
        elif kw.has_key('stream'):
            opts['ReturnType'] = "direct"
            opts['stream'] = kw['stream']
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
        
    #    if uri.startswith("freenet:CHK@") or uri.startswith("CHK@"):
    #        uri = os.path.splitext(uri)[0]
    
        # process uri, including possible namesite lookups
        uri = uri.split("freenet:")[-1]
        if len(uri) < 5 or (uri[:4] not in ('SSK@', 'KSK@', 'CHK@', 'USK@', 'SVK@')):
            # we seem to have a 'domain name' uri
            try:
                domain, rest = uri.split("/", 1)
            except:
                domain = uri
                rest = ''
            
            tgtUri = self.namesiteLookup(domain)
            if not tgtUri:
                raise FCPNameLookupFailure(
                        "Failed to resolve freenet domain '%s'" % domain)
            if rest:
                uri = (tgtUri + "/" + rest).replace("//", "/")
            else:
                uri = tgtUri
            
        opts['URI'] = uri
    
        opts['MaxRetries'] = kw.get("maxretries", -1)
        opts['MaxSize'] = kw.get("maxsize", "1000000000000")
        opts['PriorityClass'] = int(kw.get("priority", 2))
    
        opts['timeout'] = int(kw.pop("timeout", ONE_YEAR))
    
        #print "get: opts=%s" % opts
    
        # ---------------------------------
        # now enqueue the request
        return self._submitCmd(id, "ClientGet", **opts)
    
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
            - async - whether to do the job asynchronously, returning a job ticket
              object (default False)
            - waituntilsent - default False, if True, and if async=True, waits
              until the command has been sent to the node before returning a 
              job object
            - persistence - default 'connection' - the kind of persistence for
              this request. If 'reboot' or 'forever', this job will be able to
              be recalled in subsequent FCP sessions. Other valid values are
              'reboot' and 'forever', as per FCP spec
            - Global - default false - if evaluates to true, puts this request
              on the global queue. Note the capital G in Global. If you set this,
              persistence must be 'reboot' or 'forever'
            - Verbosity - default 0 - sets the Verbosity mask passed in the
              FCP message - case-sensitive
    
            - maxretries - maximum number of retries, default 3
            - priority - the PriorityClass for retrieval, default 3, may be between
              0 (highest) to 6 (lowest)
            - realtime true/false - sets the RealTimeRequest flag.
    
            - timeout - timeout for completion, in seconds, default one year
    
        Notes:
            - exactly one of 'file', 'data' or 'dir' keyword arguments must be present
        """
        # divert to putdir if dir keyword present
        if kw.has_key('dir'):
            self._log(DETAIL, "put => putdir")
            return self.putdir(uri, **kw)
    
        # ---------------------------------
        # format the request
        opts = {}
    
        opts['async'] = kw.get('async', False)
        opts['waituntilsent'] = kw.get('waituntilsent', False)
        opts['keep'] = kw.get('keep', False)
        if kw.has_key('callback'):
            opts['callback'] = kw['callback']
    
        self._log(DETAIL, "put: uri=%s async=%s waituntilsent=%s" % (
                            uri, opts['async'], opts['waituntilsent']))
    
        opts['Persistence'] = kw.pop('persistence', 'connection')
        if kw.get('Global', False):
            opts['Global'] = "true"
        else:
            opts['Global'] = "false"
    
        if opts['Global'] == 'true' and opts['Persistence'] == 'connection':
            raise Exception("Global requests must be persistent")
    
        # process uri, including possible namesite lookups
        uri = uri.split("freenet:")[-1]
        if len(uri) < 4 or (uri[:4] not in ('SSK@', 'KSK@', 'CHK@', 'USK@', 'SVK@')):
            # we seem to have a 'domain name' uri
            try:
                domain, rest = uri.split("/", 1)
            except:
                domain = uri
                rest = ''
            
            tgtUri = self.namesiteLookup(domain)
            if not tgtUri:
                raise FCPNameLookupFailure(
                        "Failed to resolve freenet domain '%s'" % domain)
            if rest:
                uri = (tgtUri + "/" + rest).replace("//", "/")
            else:
                uri = tgtUri
    
        opts['URI'] = uri
        
        # determine a mimetype
        mimetype = kw.get("mimetype", None)
        if kw.has_key('mimetype'):
            # got an explicit mimetype - use it
            mimetype = kw['mimetype']
        else:
            # not explicitly given - figure one out
            ext = os.path.splitext(uri)[1]
            if not ext:
                # no CHK@ file extension, try for filename
                if kw.has_key('file'):
                    # try to grab a file extension from inserted file
                    ext = os.path.splitext(kw['file'])[1]
                if not ext:
                    # last resort fallback
                    ext = ".txt"
    
            # got some kind of 'file extension', convert to mimetype
            try:
                mimetype = mimetypes.guess_type(ext)[0] or "text/plain"
            except:
                mimetype = "text/plain"
    
        # now can specify the mimetype
        opts['Metadata.ContentType'] = mimetype
    
        id = kw.pop("id", None)
        if not id:
            id = self._getUniqueId()
        opts['Identifier'] = id
    
        chkOnly = toBool(kw.get("chkonly", "false"))
    
        opts['Verbosity'] = kw.get('Verbosity', 0)
        opts['MaxRetries'] = kw.get("maxretries", -1)
        opts['PriorityClass'] = kw.get("priority", 3)
        opts['RealTimeFlag'] = toBool(kw.get("realtime", "false"))
        opts['GetCHKOnly'] = chkOnly
        opts['DontCompress'] = toBool(kw.get("nocompress", "false"))
        
        if kw.has_key("file"):
            filepath = os.path.abspath(kw['file'])
            opts['UploadFrom'] = "disk"
            opts['Filename'] = filepath
            if not kw.has_key("mimetype"):
                opts['Metadata.ContentType'] = mimetypes.guess_type(kw['file'])[0] or "text/plain"
            # TODO: Add a base64 encoded sha256 hash of the file
            opts['FileHash'] = base64.encodestring(
                sha256dda(self.connectionidentifier, id, 
                          path=filepath))
    
        elif kw.has_key("data"):
            opts["UploadFrom"] = "direct"
            opts["Data"] = kw['data']
            targetFilename = kw.get('name')
            if targetFilename:
                opts["TargetFilename"] = targetFilename
    
        elif kw.has_key("redirect"):
            opts["UploadFrom"] = "redirect"
            opts["TargetURI"] = kw['redirect']
        elif chkOnly != "true":
            raise Exception("Must specify file, data or redirect keywords")
    
        opts['timeout'] = int(kw.get("timeout", ONE_YEAR))
    
        #print "sendEnd=%s" % sendEnd
    
        # ---------------------------------
        # now dispatch the job
        return self._submitCmd(id, "ClientPut", **opts)
    
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
            
            - filebyfile - default False - if True, manually inserts
              each constituent file, then performs the ClientPutComplexDir
              as a manifest full of redirects. You *must* use this mode
              if inserting from across a LAN
    
            - maxretries - maximum number of retries, default 3
            - priority - the PriorityClass for retrieval, default 2, may be between
              0 (highest) to 6 (lowest)
    
            - id - the job identifier, for persistent requests
            - async - default False - if True, return immediately with a job ticket
            - persistence - default 'connection' - the kind of persistence for
              this request. If 'reboot' or 'forever', this job will be able to
              be recalled in subsequent FCP sessions. Other valid values are
              'reboot' and 'forever', as per FCP spec
            - Global - default false - if evaluates to true, puts this request
              on the global queue. Note the capital G in Global. If you set this,
              persistence must be 'reboot' or 'forever'
            - Verbosity - default 0 - sets the Verbosity mask passed in the
              FCP message - case-sensitive
            - allatonce - default False - if set, and if filebyfile is set, then
              all files of the site will be inserted simultaneously, which can give
              a nice speed-up for small to moderate sites, but cruel choking on
              large sites; use with care
            - globalqueue - perform the inserts on the global queue, which will
              survive node reboots
    
            - timeout - timeout for completion, in seconds, default one year
    
    
        Returns:
            - the URI under which the freesite can be retrieved
        """
        log = self._log
        log(INFO, "putdir: uri=%s dir=%s" % (uri, kw['dir']))
    
        #@    <<process keyword args>>
        #@+node:<<process keyword args>>
        # --------------------------------------------------------------
        # process keyword args
        
        chkonly = False
        #chkonly = True
        
        # get keyword args
        dir = kw['dir']
        sitename = kw.get('name', 'freesite')
        usk = kw.get('usk', False)
        version = kw.get('version', 0)
        maxretries = kw.get('maxretries', 3)
        priority = kw.get('priority', 4)
        Verbosity = kw.get('Verbosity', 0)
        
        filebyfile = kw.get('filebyfile', False)
        
        #if filebyfile:
        #    raise Hell
        
        if kw.has_key('allatonce'):
            allAtOnce = kw['allatonce']
            filebyfile = True
        else:
            allAtOnce = False
        
        if kw.has_key('maxconcurrent'):
            maxConcurrent = kw['maxconcurrent']
            filebyfile = True
            allAtOnce = True
        else:
            maxConcurrent = 10
        
        if kw.get('globalqueue', False):
            globalMode = True
            globalWord = "true"
            persistence = "forever"
        else:
            globalMode = False
            globalWord = "false"
            persistence = "connection"
        
        id = kw.pop("id", None)
        if not id:
            id = self._getUniqueId()
        
        # derive final URI for insert
        uriFull = uri + sitename + "/"
        if kw.get('usk', False):
            uriFull += "%d/" % int(version)
            uriFull = uriFull.replace("SSK@", "USK@")
            while uriFull.endswith("/"):
                uriFull = uriFull[:-1]
        
        manifestDict = kw.get('manifest', None)
        
        #@-node:<<process keyword args>>
        #@nl
    
        #@    <<get inventory>>
        #@+node:<<get inventory>>
        # --------------------------------------------------------------
        # procure a manifest dict, whether supplied by caller or derived
        if manifestDict:
            # work from the manifest provided by caller
            #print "got manifest kwd"
            #print manifestDict
            manifest = []
            for relpath, attrDict in manifestDict.items():
                if attrDict['changed'] or (relpath == "index.html"):
                    attrDict['relpath'] = relpath
                    attrDict['fullpath'] = os.path.join(dir, relpath)
                    manifest.append(attrDict)
        else:
            # build manifest by reading the directory
            #print "no manifest kwd"
            manifest = readdir(kw['dir'])
            manifestDict = {}
            for rec in manifest:
                manifestDict[rec['relpath']] = rec
            #print manifestDict
        
        #@-node:<<get inventory>>
        #@nl
        
        #@    <<global mode>>
        #@+node:<<global mode>>
        if 0:
            #@    <<derive chks>>
            #@+node:<<derive chks>>
            # --------------------------------------------------------------
            # derive CHKs for all items
            
            log(INFO, "putdir: determining chks for all files")
            
            for filerec in manifest:
                
                # get the record and its fields
                relpath = filerec['relpath']
                fullpath = filerec['fullpath']
                mimetype = filerec['mimetype']
            
                # get raw file contents
                raw = file(fullpath, "rb").read()
            
                # determine CHK
                uri = self.put("CHK@",
                               data=raw,
                               mimetype=mimetype,
                               Verbosity=Verbosity,
                               chkonly=True,
                               priority=priority,
                               )
            
                if uri != filerec.get('uri', None):
                    filerec['changed'] = True
                    filerec['uri'] = uri
            
                log(INFO, "%s -> %s" % (relpath, uri))
            
            #@-node:<<derive chks>>
            #@nl
        
            #@    <<build chk-based manifest>>
            #@+node:<<build chk-based manifest>>
            if filebyfile:
                
                # --------------------------------------------------------------
                # now can build up a command buffer to insert the manifest
                # since we know all the file chks
                msgLines = ["ClientPutComplexDir",
                            "Identifier=%s" % id,
                            "Verbosity=%s" % Verbosity,
                            "MaxRetries=%s" % maxretries,
                            "PriorityClass=%s" % priority,
                            "URI=%s" % uriFull,
                            #"Persistence=%s" % kw.get("persistence", "connection"),
                            "DefaultName=index.html",
                            ]
                # support global queue option
                if globalMode:
                    msgLines.extend([
                        "Persistence=forever",
                        "Global=true",
                        ])
                else:
                    msgLines.extend([
                        "Persistence=connection",
                        "Global=false",
                        ])
                
                # add each file's entry to the command buffer
                n = 0
                default = None
                for filerec in manifest:
                    relpath = filerec['relpath']
                    mimetype = filerec['mimetype']
                
                    log(DETAIL, "n=%s relpath=%s" % (repr(n), repr(relpath)))
                
                    msgLines.extend(["Files.%d.Name=%s" % (n, relpath),
                                     "Files.%d.UploadFrom=redirect" % n,
                                     "Files.%d.TargetURI=%s" % (n, filerec['uri']),
                                    ])
                    n += 1
                
                # finish the command buffer
                msgLines.append("EndMessage")
                manifestInsertCmdBuf = "\n".join(msgLines) + "\n"
                
                # gotta log the command buffer here, since it's not sent via .put()
                for line in msgLines:
                    log(DETAIL, line)
            
                #raise Exception("debugging")
            
            #@-node:<<build chk-based manifest>>
            #@nl
            
        #@-node:<<global mode>>
        #@nl
    
        #@    <<single-file inserts>>
        #@+node:<<single-file inserts>>
        # --------------------------------------------------------------
        # for file-by-file mode, queue up the inserts and await completion
        jobs = []
        #allAtOnce = False
        
        if filebyfile:
            
            log(INFO, "putdir: starting file-by-file inserts")
        
            lastProgressMsgTime = time.time()
        
            # insert each file, one at a time
            nTotal = len(manifest)
        
            # output status messages, and manage concurrent inserts
            while True:
                # get progress counts
                nQueued = len(jobs)
                nComplete = len(
                                filter(
                                    lambda j: j.isComplete(),
                                    jobs
                                    )
                                )
                nWaiting = nTotal - nQueued
                nInserting = nQueued - nComplete
        
                # spit a progress message every 10 seconds
                now = time.time()
                if now - lastProgressMsgTime >= 10:
                    lastProgressMsgTime = time.time()
                    log(INFO,
                        "putdir: waiting=%s inserting=%s done=%s total=%s" % (
                            nWaiting, nInserting, nComplete, nTotal)
                        )
        
                # can bail if all done
                if nComplete == nTotal:
                    log(INFO, "putdir: all inserts completed (or failed)")
                    break
        
                # wait and go round again if concurrent inserts are maxed
                if nInserting >= maxConcurrent:
                    time.sleep(1)
                    continue
        
                # just go round again if manifest is empty (all remaining are in progress)
                if len(manifest) == 0:
                    time.sleep(1)
                    continue
        
                # got >0 waiting jobs and >0 spare slots, so we can submit a new one
                filerec = manifest.pop(0)
                relpath = filerec['relpath']
                fullpath = filerec['fullpath']
                mimetype = filerec['mimetype']
        
                #manifestDict[relpath] = filerec
        
                log(INFO, "Launching insert of %s" % relpath)
        
        
                # gotta suck raw data, since we might be inserting to a remote FCP
                # service (which means we can't use 'file=' (UploadFrom=pathmae) keyword)
                raw = file(fullpath, "rb").read()
        
                print "globalMode=%s persistence=%s" % (globalMode, persistence)
        
                # fire up the insert job asynchronously
                job = self.put("CHK@",
                               data=raw,
                               mimetype=mimetype,
                               async=1,
                               waituntilsent=1,
                               Verbosity=Verbosity,
                               chkonly=chkonly,
                               priority=priority,
                               Global=globalMode,
                               Persistence=persistence,
                               )
                jobs.append(job)
                filerec['job'] = job
                job.filerec = filerec
        
                # wait for that job to finish if we are in the slow 'one at a time' mode
                if not allAtOnce:
                    job.wait()
                    log(INFO, "Insert finished for %s" % relpath)
        
            # all done
            log(INFO, "All raw files now inserted (or failed)")
        
        
        #@-node:<<single-file inserts>>
        #@nl
        
        #@    <<build manifest insertion cmd>>
        #@+node:<<build manifest insertion cmd>>
        # --------------------------------------------------------------
        # now can build up a command buffer to insert the manifest
        msgLines = ["ClientPutComplexDir",
                    "Identifier=%s" % id,
                    "Verbosity=%s" % Verbosity,
                    "MaxRetries=%s" % maxretries,
                    "PriorityClass=%s" % priority,
                    "URI=%s" % uriFull,
                    #"Persistence=%s" % kw.get("persistence", "connection"),
                    "DefaultName=index.html",
                    ]
        # support global queue option
        if kw.get('Global', False):
            msgLines.extend([
                "Persistence=forever",
                "Global=true",
                ])
        else:
            msgLines.extend([
                "Persistence=connection",
                "Global=false",
                ])
        
        # add each file's entry to the command buffer
        n = 0
        default = None
        for job in jobs:
            filerec = job.filerec
            relpath = filerec['relpath']
            fullpath = filerec['fullpath']
            mimetype = filerec['mimetype']
        
            # don't add if the file failed to insert
            if filebyfile:
                if isinstance(filerec['job'].result, Exception):
                    log(ERROR, "File %s failed to insert" % relpath)
                    continue
        
            log(DETAIL, "n=%s relpath=%s" % (repr(n), repr(relpath)))
        
            msgLines.extend(["Files.%d.Name=%s" % (n, relpath),
                             ])
            if filebyfile:
                #uri = filerec['uri'] or filerec['job'].result
                uri = job.result
                if not uri:
                    raise Exception("Can't find a URI for file %s" % filerec['relpath'])
        
                msgLines.extend(["Files.%d.UploadFrom=redirect" % n,
                                 "Files.%d.TargetURI=%s" % (n, uri),
                                ])
            else:
                msgLines.extend(["Files.%d.UploadFrom=disk" % n,
                                 "Files.%d.Filename=%s" % (n, fullpath),
                                ])
            n += 1
        
        # finish the command buffer
        msgLines.append("EndMessage")
        manifestInsertCmdBuf = "\n".join(msgLines) + "\n"
        
        # gotta log the command buffer here, since it's not sent via .put()
        for line in msgLines:
            log(DETAIL, line)
        
        #@-node:<<build manifest insertion cmd>>
        #@nl
        
        #@    <<insert manifest>>
        #@+node:<<insert manifest>>
        # --------------------------------------------------------------
        # now dispatch the manifest insertion job
        if chkonly:
            finalResult = "no_uri"
        else:
            finalResult = self._submitCmd(
                            id, "ClientPutComplexDir",
                            rawcmd=manifestInsertCmdBuf,
                            async=kw.get('async', False),
                            waituntilsent=kw.get('waituntilsent', False),
                            callback=kw.get('callback', False),
                            #Persistence=kw.get('Persistence', 'connection'),
                            )
        
        #@-node:<<insert manifest>>
        #@nl
        
        # finally all done, return result or job ticket
        return finalResult
    
    def modifyconfig(self, **kw):
        """
        Modifies node configuration
        
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
            - keywords, which are the same as for the FCP message and documented in the wiki: http://wiki.freenetproject.org/FCP2p0ModifyConfig
        """
        return self._submitCmd("__global", "ModifyConfig", **kw)
    
    #@-node:putdir
    #@+node:getconfig
    def getconfig(self, **kw):
        """
        Gets node configuration
        
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
            - WithCurrent - default False - if True, the current configuration settings will be returned in the "current" tree of the ConfigData message fieldset
            - WithShortDescription - default False - if True, the configuration setting short descriptions will be returned in the "shortDescription" tree of the ConfigData message fieldset
            - other keywords, which are the same as for the FCP message and documented in the wiki: http://wiki.freenetproject.org/FCP2p0GetConfig
        """
        
        return self._submitCmd("__global", "GetConfig", **kw)
    
    #@-node:getconfig
    #@+node:invertprivate
    def invertprivate(self, privatekey):
        """
        Converts an SSK or USK private key to a public equivalent
        """
        privatekey = privatekey.strip().split("freenet:")[-1]
    
        isUsk = privatekey.startswith("USK@")
        
        if isUsk:
            privatekey = privatekey.replace("USK@", "SSK@")
    
        bits = privatekey.split("/", 1)
        mainUri = bits[0]
    
        uri = self.put(mainUri+"/foo", data="bar", chkonly=1)
    
        uri = uri.split("/")[0]
        uri = "/".join([uri] + bits[1:])
    
        if isUsk:
            uri = uri.replace("SSK@", "USK@")
    
        return uri
    
    #@-node:invertprivate
    #@+node:redirect
    def redirect(self, srcKey, destKey, **kw):
        """
        Inserts key srcKey, as a redirect to destKey.
        srcKey must be a KSK, or a path-less SSK or USK (and not a CHK)
        """
        uri = self.put(srcKey, redirect=destKey, **kw)
    
        return uri
    
    #@-node:redirect
    #@+node:genchk
    def genchk(self, **kw):
        """
        Returns the CHK URI under which a data item would be
        inserted.
        
        Keywords - you must specify one of the following:
            - file - path of file from which to read the key data
            - data - the raw data of the key as string
    
        Keywords - optional:
            - mimetype - defaults to text/plain - THIS AFFECTS THE CHK!!
        """
        return self.put(chkonly=True, **kw)
    
    #@-node:genchk
    #@+node:listpeers
    def listpeers(self, **kw):
        """
        Gets the list of peers from the node
        
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
            - WithMetadata - default False - if True, returns a peer's metadata
            - WithVolatile - default False - if True, returns a peer's volatile info
        """
        
        return self._submitCmd("__global", "ListPeers", **kw)
    
    #@-node:listpeers
    #@+node:listpeernotes
    def listpeernotes(self, **kw):
        """
        Gets the list of peer notes for a given peer from the node
        
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
            - NodeIdentifier - one of name, identity or IP:port for the desired peer
        """
        
        return self._submitCmd("__global", "ListPeerNotes", **kw)
    
    #@-node:listpeernotes
    #@+node:refstats
    def refstats(self, **kw):
        """
        Gets node reference and possibly node statistics.
        
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
            - GiveOpennetRef - default False - if True, return the node's Opennet reference rather than the node's Darknet reference
            - WithPrivate - default False - if True, includes the node's private node reference fields
            - WithVolatile - default False - if True, returns a node's volatile info
        """
        
        return self._submitCmd("__global", "GetNode", **kw)
    
    #@-node:refstats
    #@+node:testDDA
    def testDDA(self, **kw):
        """
        Test for Direct Disk Access capability on a directory (can the node and the FCP client both access the same directory?)
        
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
            - Directory - directory to test
            - WithReadDirectory - default False - if True, want node to read from directory for a put operation
            - WithWriteDirectory - default False - if True, want node to write to directory for a get operation
        """
        
        requestResult = self._submitCmd("__global", "TestDDARequest", **kw)
        writeFilename = None;
        kw = {};
        kw[ 'Directory' ] = requestResult[ 'Directory' ];
        if( requestResult.has_key( 'ReadFilename' )):
            readFilename = requestResult[ 'ReadFilename' ];
            readFile = open( readFilename, 'rb' );
            readFileContents = readFile.read();
            readFile.close();
            kw[ 'ReadFilename' ] = readFilename;
            kw[ 'ReadContent' ] = readFileContents;
            
        if( requestResult.has_key( 'WriteFilename' ) and requestResult.has_key( 'ContentToWrite' )):
            writeFilename = requestResult[ 'WriteFilename' ];
            contentToWrite = requestResult[ 'ContentToWrite' ];
            writeFile = open( writeFilename, 'w+b' );
            writeFileContents = writeFile.write( contentToWrite );
            writeFile.close();
            writeFileStatObject = os.stat( writeFilename );
            writeFileMode = writeFileStatObject.st_mode;
            os.chmod( writeFilename, writeFileMode | stat.S_IREAD | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH );
            
        responseResult = self._submitCmd("__global", "TestDDAResponse", **kw)
        if( None != writeFilename ):
            try:
                os.remove( writeFilename );
            except OSError, msg:
                pass;
        return responseResult;
    
    #@-node:testDDA
    #@+node:addpeer
    def addpeer(self, **kw):
        """
        Add a peer to the node
        
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
            - File - filepath of a file containing a noderef in the node's directory
            - URL - URL of a copy of a peer's noderef to add
            - kwdict - If neither File nor URL are provided, the fields of a noderef can be passed in the form of a Python dictionary using the kwdict keyword
        """
        
        return self._submitCmd("__global", "AddPeer", **kw)
    
    #@-node:addpeer
    #@+node:listpeer
    def listpeer(self, **kw):
        """
        Modify settings on one of the node's peers
        
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
            - NodeIdentifier - one of name (except for opennet peers), identity or IP:port for the desired peer
        """
        
        return self._submitCmd("__global", "ListPeer", **kw)
    
    #@-node:listpeer
    #@+node:modifypeer
    def modifypeer(self, **kw):
        """
        Modify settings on one of the node's peers
        
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
            - IsDisabled - default False - enables or disabled the peer accordingly
            - IsListenOnly - default False - sets ListenOnly on the peer
            - NodeIdentifier - one of name, identity or IP:port for the desired peer
        """
        
        return self._submitCmd("__global", "ModifyPeer", **kw)
    
    #@-node:modifypeer
    #@+node:modifypeernote
    def modifypeernote(self, **kw):
        """
        Modify settings on one of the node's peers
        
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
            - NodeIdentifier - one of name, identity or IP:port for the desired peer
            - NoteText - base64 encoded string of the desired peer note text
            - PeerNoteType - code number of peer note type: currently only private peer note is supported by the node with code number 1 
        """
        
        return self._submitCmd("__global", "ModifyPeerNote", **kw)
    
    #@-node:modifypeernote
    #@+node:removepeer
    def removepeer(self, **kw):
        """
        Removes a peer from the node
        
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
            - NodeIdentifier - one of name, identity or IP:port for the desired peer
        """
        
        return self._submitCmd("__global", "RemovePeer", **kw)
    
    #@-node:removepeer
    #@-others
    
    #@-node:FCP Primitives
    #@+node:Namesite primitives
    # methods for namesites
    
    #@+others
    #@+node:namesiteInit
    def namesiteInit(self, path):
        """
        Initialise the namesites layer and load our namesites list
        """
        if path:
            self.namesiteFile = path
        else:
            self.namesiteFile = os.path.join(os.path.expanduser("~"), ".freenames")
    
        self.namesiteLocals = []
        self.namesitePeers = []
    
        # create empty file 
        if os.path.isfile(self.namesiteFile):
            self.namesiteLoad()
        else:
            self.namesiteSave()
    
    #@-node:namesiteInit
    #@+node:namesiteLoad
    def namesiteLoad(self):
        """
        """
        try:
            parser = pseudopythonparser.Parser()
            env = parser.parse(file(self.namesiteFile).read())
            self.namesiteLocals = env['locals']
            self.namesitePeers = env['peers']
        except:
            traceback.print_exc()
            env = {}
    
    #@-node:namesiteLoad
    #@+node:namesiteSave
    def namesiteSave(self):
        """
        Save the namesites list
        """
        f = file(self.namesiteFile, "w")
    
        f.write("# pyfcp namesites registration file\n\n")
    
        pp = pprint.PrettyPrinter(width=72, indent=2, stream=f)
    
        f.write("locals = ")
        pp.pprint(self.namesiteLocals)
        f.write("\n")
    
        f.write("peers = ")
        pp.pprint(self.namesitePeers)
        f.write("\n")
    
        f.close()
    
    #@-node:namesiteSave
    #@+node:namesiteAddLocal
    def namesiteAddLocal(self, name, privuri=None):
        """
        Create a new nameservice that we own
        """
        if not privuri:
            privuri = self.genkey()[1]
        puburi = self.invertprivate(privuri)
        
        privuri = self.namesiteProcessUri(privuri)
        puburi = self.namesiteProcessUri(puburi)
    
        for rec in self.namesiteLocals:
            if rec['name'] == name:
                raise Exception("Already got a local service called '%s'" % name)
        
        self.namesiteLocals.append(
            {'name':name,
             'privuri':privuri,
             'puburi': puburi,
             'cache': {},
            })
    
        self.namesiteSave()
    
    #@-node:namesiteAddLocal
    #@+node:namesiteDelLocal
    def namesiteDelLocal(self, name):
        """
        Delete a local nameservice
        """
        rec = None
        for r in self.namesiteLocals:
            if r['name'] == name:
                self.namesiteLocals.remove(r)
    
        self.namesiteSave()
    
    #@-node:namesiteDelLocal
    #@+node:namesiteAddRecord
    def namesiteAddRecord(self, localname, domain, uri):
        """
        Adds a (domainname -> uri) record to one of our local
        services
        """
        rec = None
        for r in self.namesiteLocals:
            if r['name'] == localname:
                rec = r
        if not rec:
            raise Exception("No local service '%s'" % localname)
    
        cache = rec['cache']
    
        # bail if domain is known and is pointing to same uri
        if cache.get(domain, None) == uri:
            return
    
        # domain is new, or uri has changed
        cache[domain] = uri
    
        # save local records
        self.namesiteSave()
    
        # determine the insert uri
        localPrivUri = rec['privuri'] + "/" + domain + "/0"
    
        # and stick it in, via global queue
        id = "namesite|%s|%s|%s" % (localname, domain, int(time.time()))
        self.put(
            localPrivUri,
            id=id,
            data=uri,
            persistence="forever",
            Global=True,
            priority=0,
            async=True,
            )
    
        self.refreshPersistentRequests()
    
    #@-node:namesiteAddRecord
    #@+node:namesiteDelRecord
    def namesiteDelRecord(self, localname, domain):
        """
        Removes a domainname record from one of our local
        services
        """
        rec = None
        for r in self.namesiteLocals:
            if r['name'] == localname:
                if domain in r['cache']:
                    del r['cache'][domai]
    
        self.namesiteSave()
    
    #@-node:namesiteDelRecord
    #@+node:namesiteAddPeer
    def namesiteAddPeer(self, name, uri):
        """
        Adds a namesite to our list
        """
        # process URI
        uri = uri.split("freenet:")[-1]
    
        # validate uri TODO reject private uris
        if not uri.startswith("USK"):
            raise Exception("Invalid URI %s, should be a public USK" % uri)
    
        # just uplift the public key part, remove path
        uri = uri.split("freenet:")[-1]
        uri = uri.split("/")[0]
    
        if self.namesiteHasPeer(name):
            raise Exception("Peer nameservice '%s' already exists" % name)
    
        self.namesitePeers.append({'name':name, 'puburi':uri})
    
        self.namesiteSave()
    
    #@-node:namesiteAddPeer
    #@+node:namesiteHasPeer
    def namesiteHasPeer(self, name):
        """
        returns True if we have a peer namesite of given name
        """    
        return self.namesiteGetPeer(name) is not None
    
    #@-node:namesiteHasPeer
    #@+node:namesiteGetPeer
    def namesiteGetPeer(self, name):
        """
        returns record for given peer
        """
        for rec in self.namesitePeers:
            if rec['name'] == name:
                return rec
        return None
    
    #@-node:namesiteGetPeer
    #@+node:namesiteRemovePeer
    def namesiteRemovePeer(self, name):
        """
        Removes a namesite from our list
        """
        for rec in self.namesitePeers:
            if rec['name'] == name:
                self.namesitePeers.remove(rec)
        
        self.namesiteSave()
    
    #@-node:namesiteRemovePeer
    #@+node:namesiteLookup
    def namesiteLookup(self, domain, **kw):
        """
        Attempts a lookup of a given 'domain name' on our designated
        namesites
        
        Arguments:
            - domain - the domain to look up
        
        Keywords:
            - localonly - whether to only search local cache
            - peer - if given, search only that peer's namesite (not locals)
        """
        self.namesiteLoad()
    
        localonly = kw.get('localonly', False)
        peer = kw.get('peer', None)
        
        if not peer:
            # try local cache first
            for rec in self.namesiteLocals:
                if domain in rec['cache']:
                    return rec['cache'][domain]
    
        if localonly:
            return None
    
        # the long step
        for rec in self.namesitePeers:
    
            if peer and (peer != rec['name']):
                continue
    
            uri = rec['puburi'] + "/" + domain + "/0"
    
            try:
                mimetype, tgtUri = self.get(uri)
                return tgtUri
            except:
                pass
    
        return None
    
    #@-node:namesiteLookup
    #@+node:namesiteProcessUri
    def namesiteProcessUri(self, uri):
        """
        Reduces a URI
        """
        # strip 'freenet:'
        uri1 = uri.split("freenet:")[-1]
        
        # change SSK to USK, and split path
        uri1 = uri1.replace("SSK@", "USK@").split("/")[0]
        
        # barf if bad uri
        if not uri1.startswith("USK@"):
            usage("Bad uri %s" % uri)
        
        return uri1
    
    #@-node:namesiteProcessUri
    #@-others
    
    #@-node:Namesite primitives
    #@+node:Other High Level Methods
    # high level client methods
    
    #@+others
    #@+node:listenGlobal
    def listenGlobal(self, **kw):
        """
        Enable listening on global queue
        """
        self._submitCmd(None, "WatchGlobal", Enabled="true", **kw)
    
    #@-node:listenGlobal
    #@+node:ignoreGlobal
    def ignoreGlobal(self, **kw):
        """
        Stop listening on global queue
        """
        self._submitCmd(None, "WatchGlobal", Enabled="false", **kw)
    
    #@-node:ignoreGlobal
    #@+node:purgePersistentJobs
    def purgePersistentJobs(self):
        """
        Cancels all persistent jobs in one go
        """
        for job in self.getPersistentJobs():
            job.cancel()
    
    #@-node:purgePersistentJobs
    #@+node:getAllJobs
    def getAllJobs(self):
        """
        Returns a list of persistent jobs, excluding global jobs
        """
        return self.jobs.values()
    
    #@-node:getAllJobs
    #@+node:getPersistentJobs
    def getPersistentJobs(self):
        """
        Returns a list of persistent jobs, excluding global jobs
        """
        return [j for j in self.jobs.values() if j.isPersistent and not j.isGlobal]
    
    #@-node:getPersistentJobs
    #@+node:getGlobalJobs
    def getGlobalJobs(self):
        """
        Returns a list of global jobs
        """
        return [j for j in self.jobs.values() if j.isGlobal]
    
    #@-node:getGlobalJobs
    #@+node:getTransientJobs
    def getTransientJobs(self):
        """
        Returns a list of non-persistent, non-global jobs
        """
        return [j for j in self.jobs.values() if not j.isPersistent]
    
    #@-node:getTransientJobs
    #@+node:refreshPersistentRequests
    def refreshPersistentRequests(self, **kw):
        """
        Sends a ListPersistentRequests to node, to ensure that
        our records of persistent requests are up to date.
        
        Since, upon connection, the node sends us a list of all
        outstanding persistent requests anyway, I can't really
        see much use for this method. I've only added the method
        for FCP spec compliance
        """
        self._log(DETAIL, "listPersistentRequests")
    
        if self.jobs.has_key('__global'):
            raise Exception("An existing non-identifier job is currently pending")
    
        # ---------------------------------
        # format the request
        opts = {}
    
        id = '__global'
        opts['Identifier'] = id
    
        opts['async'] = kw.pop('async', False)
        if kw.has_key('callback'):
            opts['callback'] = kw['callback']
    
        # ---------------------------------
        # now enqueue the request
        return self._submitCmd(id, "ListPersistentRequests", **opts)
    
    #@-node:refreshPersistentRequests
    #@+node:clearGlobalJob
    def clearGlobalJob(self, id):
        """
        Removes a job from the jobs queue
        """
        self._submitCmd(id, "RemovePersistentRequest",
                        Identifier=id, Global=True, async=True, waituntilsent=True)
    
    #@-node:clearGlobalJob
    #@+node:setSocketTimeout
    def getSocketTimeout(self):
        """
        Gets the socketTimeout for future socket calls;
        returns None if not supported by Python version
        """
        try:
            return self.socket.gettimeout()
        except Exception, e:
            # Socket timeout setting is not available until Python 2.3, so ignore exceptions
            pass
        return None
    
    #@-node:setSocketTimeout
    #@+node:setSocketTimeout
    def setSocketTimeout(self, socketTimeout):
        """
        Sets the socketTimeout for future socket calls
        
        >>> node = FCPNode()
        >>> timeout = node.getSocketTimeout()
        >>> newtimeout = 1800
        >>> node.setSocketTimeout(newtimeout)
        >>> node.getSocketTimeout()
        1800.0
        """
        self.socketTimeout = socketTimeout
        try:
            self.socket.settimeout(self.socketTimeout)
        except Exception, e:
            # Socket timeout setting is not available until Python 2.3, so ignore exceptions
            pass
    
    #@-node:setSocketTimeout
    #@+node:getVerbosity
    def getVerbosity(self):
        """
        Gets the verbosity for future logging calls

        >>> node = FCPNode()
        >>> node.getVerbosity() # default
        3
        >>> node.setVerbosity(INFO)
        >>> node.getVerbosity()
        4
        """
        return self.verbosity
    
    #@-node:getVerbosity
    #@+node:setVerbosity
    def setVerbosity(self, verbosity):
        """
        Sets the verbosity for future logging calls
        """
        self.verbosity = verbosity
    
    #@-node:setVerbosity
    #@+node:shutdown
    def shutdown(self):
        """
        Terminates the manager thread
        
        You should explicitly shutdown any existing nodes
        before exiting your client application
        """
        log = self._log
    
        log(DETAIL, "shutdown: entered")
        if not self.running:
            log(DETAIL, "shutdown: already shut down")
            return
    
        self.running = False
    
        # give the manager thread a chance to bail out
        time.sleep(pollTimeout * 3)
    
        # wait for mgr thread to quit
        log(DETAIL, "shutdown: waiting for manager thread to terminate")
        self.shutdownLock.acquire()
        log(DETAIL, "shutdown: manager thread terminated")
    
        # shut down FCP connection
        if hasattr(self, 'socket'):
            if not self.noCloseSocket:
                self.socket.close()
                del self.socket
    
        # and close the logfile
        if None != self.logfile and self.logfile not in [sys.stdout, sys.stderr]:
            self.logfile.close()
    
        log(DETAIL, "shutdown: done?")
    
    #@-node:shutdown
    #@-others
    
    
    
    #@-node:Other High Level Methods
    #@+node:Manager Thread
    # methods for manager thread
    
    #@+others
    #@+node:_mgrThread
    def _mgrThread(self):
        """
        This thread is the nucleus of pyfcp, and coordinates incoming
        client commands and incoming node responses
        """
        log = self._log
    
        self.shutdownLock.acquire()
    
        log(DETAIL, "FCPNode: manager thread starting")
        try:
            while self.running:
    
                log(NOISY, "_mgrThread: Top of manager thread")
    
                # try for incoming messages from node
                log(NOISY, "_mgrThread: Testing for incoming message")
                if self._msgIncoming():
                    log(DEBUG, "_mgrThread: Retrieving incoming message")
                    msg = self._rxMsg()
                    log(DEBUG, "_mgrThread: Got incoming message, dispatching")
                    self._on_rxMsg(msg)
                    log(DEBUG, "_mgrThread: back from on_rxMsg")
                else:
                    log(NOISY, "_mgrThread: No incoming message from node")
        
                # try for incoming requests from clients
                log(NOISY, "_mgrThread: Testing for client req")
                try:
                    req = self.clientReqQueue.get(True, pollTimeout)
                    log(DEBUG, "_mgrThread: Got client req, dispatching")
                    self._on_clientReq(req)
                    log(DEBUG, "_mgrThread: Back from on_clientReq")
                except Queue.Empty:
                    log(NOISY, "_mgrThread: No incoming client req")
                    pass
    
            self._log(DETAIL, "_mgrThread: Manager thread terminated normally")
    
        except Exception, e:
            traceback.print_exc()
            self._log(CRITICAL, "_mgrThread: manager thread crashed")
    
            # send the exception to all waiting jobs
            for id, job in self.jobs.items():
                job._putResult(e)
            
            # send the exception to all queued jobs
            while True:
                try:
                    job = self.clientReqQueue.get(True, pollTimeout)
                    job._putResult(e)
                except Queue.Empty:
                    log(NOISY, "_mgrThread: No incoming client req")
                    break
    
        self.shutdownLock.release()
    
    #@-node:_mgrThread
    #@+node:_msgIncoming
    def _msgIncoming(self):
        """
        Returns True if a message is coming in from the node
        """
        return len(select.select([self.socket], [], [], pollTimeout)[0]) > 0
    
    #@-node:_msgIncoming
    #@+node:_submitCmd
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
            - followRedirect - follow a redirect if true, otherwise fail the get
            - rawcmd - a raw command buffer to send directly
            - options specific to command such as 'URI'
            - timeout - timeout in seconds for job completion, default 1 year
            - waituntilsent - whether to block until this command has been sent
              to the node, default False
            - keep - whether to keep the job on our jobs list after it completes,
              default False
        
        Returns:
            - if command is sent in sync mode, returns the result
            - if command is sent in async mode, returns a JobTicket
              object which the client can poll or block on later
        """
        if not self.nodeIsAlive:
            raise FCPNodeFailure("%s:%s: node closed connection" % (cmd, id))
    
        log = self._log
    
        log(DEBUG, "_submitCmd: kw=%s" % kw)
    
        async = kw.pop('async', False)
        followRedirect = kw.pop('followRedirect', True)
        stream = kw.pop('stream', None)
        waituntilsent = kw.pop('waituntilsent', False)
        keepjob = kw.pop('keep', False)
        timeout = kw.pop('timeout', ONE_YEAR)
        if( kw.has_key( "kwdict" )):
            kwdict = kw[ "kwdict" ]
            del kw[ "kwdict" ]
            for key in kwdict.keys():
                kw[ key ] = kwdict[ key ]
        job = JobTicket(
            self, id, cmd, kw,
            verbosity=self.verbosity, logger=self._log, keep=keepjob,
            stream=stream)
    
        log(DEBUG, "_submitCmd: timeout=%s" % timeout)
        
        job.followRedirect = followRedirect
    
        if cmd == 'ClientGet':
            job.uri = kw['URI']
    
        if cmd == 'ClientPut':
            job.mimetype = kw['Metadata.ContentType']
    
        self.clientReqQueue.put(job)
    
        log(DEBUG, "_submitCmd: id=%s cmd=%s kw=%s" % (id, cmd, str(kw)[:256]))
    
    
        if async:
            if waituntilsent:
                job.waitTillReqSent()
            return job
        elif cmd in ['WatchGlobal', "RemovePersistentRequest"]:
            return
        else:
            log(DETAIL, "Waiting on job")
            return job.wait(timeout)
    
    #@-node:_submitCmd
    #@+node:_on_clientReq
    def _on_clientReq(self, job):
        """
        takes an incoming request job from client and transmits it to
        the fcp port, and also registers it so the manager thread
        can action responses from the fcp port.
        """
        id = job.id
        cmd = job.cmd
        kw = job.kw
    
        # register the req
        if cmd != 'WatchGlobal':
            self.jobs[id] = job
            self._log(DEBUG, "_on_clientReq: cmd=%s id=%s lock=%s" % (
                cmd, repr(id), job.lock))
        
        # now can send, since we're the only one who will
        self._txMsg(cmd, **kw)
    
        job.timeQueued = int(time.time())
    
        job.reqSentLock.release()
    
    #@-node:_on_clientReq
    #@+node:_on_rxMsg
    def _on_rxMsg(self, msg):
        """
        Handles incoming messages from node
        
        If an incoming message represents the termination of a command,
        the job ticket object will be notified accordingly
        """
        log = self._log
    
        # find the job this relates to
        id = msg.get('Identifier', '__global')
    
        hdr = msg['header']
    
        job = self.jobs.get(id, None)
        if not job:
            # we have a global job and/or persistent job from last connection
            log(DETAIL, "***** Got %s from unknown job id %s" % (hdr, repr(id)))
            job = JobTicket(self, id, hdr, msg)
            self.jobs[id] = job
    
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
            if( job.kw.has_key( 'URI' )):
                log(INFO, "Got DataFound for URI=%s" % job.kw['URI'])
            else:
                log(ERROR, "Got DataFound without URI")
            mimetype = msg['Metadata.ContentType']
            if job.kw.has_key('Filename'):
                # already stored to disk, done
                #resp['file'] = file
                result = (mimetype, job.kw['Filename'], msg)
                job.callback('successful', result)
                job._putResult(result)
                return
    
            elif job.kw['ReturnType'] == 'none':
                result = (mimetype, 1, msg)
                job.callback('successful', result)
                job._putResult(result)
                return
    
            # otherwise, we're expecting an AllData and will react to it then
            else:
                # is this a persistent get?
                if job.kw['ReturnType'] == 'direct' \
                and job.kw.get('Persistence', None) != 'connection':
                    # gotta poll for request status so we can get our data
                    # FIXME: this is a hack, clean it up
                    log(INFO, "Request was persistent")
                    if not hasattr(job, "gotPersistentDataFound"):
                        if job.isGlobal:
                            isGlobal = "true"
                        else:
                            isGlobal = "false"
                        job.gotPersistentDataFound = True
                        log(INFO, "  --> sending GetRequestStatus")
                        self._txMsg("GetRequestStatus",
                                    Identifier=job.kw['Identifier'],
                                    Persistence=msg.get("Persistence", "connection"),
                                    Global=isGlobal,
                                    )
    
                job.callback('pending', msg)
                job.mimetype = mimetype
                return
    
        if hdr == 'CompatibilityMode':
            # information, how to insert the file to make it an exact match.
            # TODO: Use the information.
            job.callback('pending', msg)
            return
    
        if hdr == 'ExpectedMIME':
            # information, how to insert the file to make it an exact match.
            # TODO: Use the information.
            mimetype = msg['Metadata.ContentType']
            job.mimetype = mimetype
            job.callback('pending', msg)
            return

        if hdr == 'ExpectedDataLength':
            # The expected filesize.
            # TODO: Use the information.
            size = msg['DataLength']
            job.callback('pending', msg)
            return

        if hdr == 'AllData':
            result = (job.mimetype, msg['Data'], msg)
            job.callback('successful', result)
            job._putResult(result)
            return

        if hdr == 'GetFailed':
            # see if it's just a redirect problem
            if job.followRedirect and msg.get('ShortCodeDescription', None) == "New URI":
                uri = msg['RedirectURI']
                job.kw['URI'] = uri
                job.kw['id'] = self._getUniqueId();
                self._txMsg(job.cmd, **job.kw)
                log(DETAIL, "Redirect to %s" % uri)
                return
            # see if it's just a TOO_MANY_PATH_COMPONENTS redirect
            if job.followRedirect and msg.get('ShortCodeDescription', None) == "Too many path components":
                uri = msg['RedirectURI']
                job.kw['URI'] = uri
                job.kw['id'] = self._getUniqueId();
                self._txMsg(job.cmd, **job.kw)
                log(DETAIL, "Redirect to %s" % uri)
                return
    
            # return an exception
            job.callback("failed", msg)
            job._putResult(FCPGetFailed(msg))
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
                return
    
        if hdr == 'PutSuccessful':
            result = msg['URI']
            job.callback('successful', result)
            job._putResult(result)
            #print "*** PUTSUCCESSFUL"
            return
    
        if hdr == 'PutFailed':
            job.callback('failed', msg)
            job._putResult(FCPPutFailed(msg))
            return
        
        if hdr == 'PutFetchable':
            uri = msg['URI']
            job.kw['URI'] = uri
            job.callback('pending', msg)
            return
    
        # -----------------------------
        # handle ConfigData
        if hdr == 'ConfigData':
            # return all the data recieved
            job.callback('successful', msg)
            job._putResult(msg)
    
            # remove job from queue
            self.jobs.pop(id, None)
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
    
        if hdr == 'SendingToNetwork':
            job.callback('pending', msg)
            return
        
        if hdr == 'ExpectedHashes':
            # The hashes the file must have.
            # TODO: Use the information.
            sha256 = msg['Hashes.SHA256']
            job.callback('pending', msg)
            return


        # -----------------------------
        # handle FCPPluginMessage replies
        
        if hdr == 'FCPPluginReply':
            job._appendMsg(msg)
            job.callback('successful', job.msgs)
            job._putResult(job.msgs)
            return   
        
        # -----------------------------
        # handle peer management messages
        
        if hdr == 'EndListPeers':
            job._appendMsg(msg)
            job.callback('successful', job.msgs)
            job._putResult(job.msgs)
            return   
        
        if hdr == 'Peer':
            if(job.cmd == "ListPeers"):
                job.callback('pending', msg)
                job._appendMsg(msg)
            else:
                job.callback('successful', msg)
                job._putResult(msg)
            return
        
        if hdr == 'PeerRemoved':
            job._appendMsg(msg)
            job.callback('successful', job.msgs)
            job._putResult(job.msgs)
            return   
        
        if hdr == 'UnknownNodeIdentifier':
            job._appendMsg(msg)
            job.callback('failed', job.msgs)
            job._putResult(job.msgs)
            return   
    
        # -----------------------------
        # handle peer note management messages
        
        if hdr == 'EndListPeerNotes':
            job._appendMsg(msg)
            job.callback('successful', job.msgs)
            job._putResult(job.msgs)




            return   
        
        if hdr == 'PeerNote':
            if(job.cmd == "ListPeerNotes"):
                job.callback('pending', msg)
                job._appendMsg(msg)
            else:
                job.callback('successful', msg)
                job._putResult(msg)
            return
        
        if hdr == 'UnknownPeerNoteType':
            job._appendMsg(msg)
            job.callback('failed', job.msgs)
            job._putResult(job.msgs)
            return   
    
        # -----------------------------
        # handle persistent job messages
    
        if hdr == 'PersistentGet':
            job.callback('pending', msg)
            job._appendMsg(msg)
            return
    
        if hdr == 'PersistentPut':
            job.callback('pending', msg)
            job._appendMsg(msg)
            return
    
        if hdr == 'PersistentPutDir':
            job.callback('pending', msg)
            job._appendMsg(msg)
            return
    
        if hdr == 'EndListPersistentRequests':
            job._appendMsg(msg)
            job.callback('successful', job.msgs)
            job._putResult(job.msgs)
            return
        
        if hdr == 'PersistentRequestRemoved':
            if self.jobs.has_key(id):
                del self.jobs[id]
            return
        
        # ----------------------------- 
        # handle USK Subscription , thanks to Enzo Matrix

        # Note from Enzo Matrix: I just needed the messages to get
        # passed through to the job, and have its callback function
        # called so I can do something when a USK gets updated. I
        # handle the checking whether the message was a
        # SubscribedUSKUpdate in the callback, which is defined in the
        # spider.
        if hdr == 'SubscribedUSK': 
            job.callback('successful', msg) 
            return 

        if hdr == 'SubscribedUSKUpdate': 
            job.callback('successful', msg) 
            return 

        if hdr == 'SubscribedUSKRoundFinished': 
            job.callback('successful', msg) 
        return 

        if hdr == 'SubscribedUSKSendingToNetwork': 
            job.callback('successful', msg) 
        return        

        # -----------------------------
        # handle testDDA messages
        
        if hdr == 'TestDDAReply':
            # return all the data recieved
            job.callback('successful', msg)
            job._putResult(msg)
    
            # remove job from queue
            self.jobs.pop(id, None)
            return
        
        if hdr == 'TestDDAComplete':
            # return all the data recieved
            job.callback('successful', msg)
            job._putResult(msg)
    
            # remove job from queue
            self.jobs.pop(id, None)
            return
    
        # -----------------------------
        # handle NodeData
        if hdr == 'NodeData':
            # return all the data recieved
            job.callback('successful', msg)
            job._putResult(msg)
    
            # remove job from queue
            self.jobs.pop(id, None)
            return
    
        # -----------------------------
        # handle various errors
    
        if hdr == 'ProtocolError':
            job.callback('failed', msg)
            job._putResult(FCPProtocolError(msg))
            return
    
        if hdr == 'IdentifierCollision':
            log(ERROR, "IdentifierCollision on id %s ???" % id)
            job.callback('failed', msg)
            job._putResult(Exception("Duplicate job identifier %s" % id))
            return
    
        # -----------------------------
        # wtf is happening here?!?
    
        log(ERROR, "Unknown message type from node: %s" % hdr)
        job.callback('failed', msg)
        job._putResult(FCPException(msg))
        return
    #@-node:_on_rxMsg
    #@-others
    
    #@-node:Manager Thread
    #@+node:Low Level Methods
    # low level noce comms methods
    
    #@+others
    #@+node:_hello
    def _hello(self):
        """
        perform the initial FCP protocol handshake
        """
        self._txMsg("ClientHello", 
                         Name=self.name,
                         ExpectedVersion=expectedVersion)
        
        resp = self._rxMsg()
        if(resp.has_key("Version")):
          self.nodeVersion = resp[ "Version" ];
        if(resp.has_key("FCPVersion")):
          self.nodeFCPVersion = resp[ "FCPVersion" ];
        if(resp.has_key("Build")):
          try:
            self.nodeBuild = int( resp[ "Build" ] );
          except Exception, msg:
            pass;
        else:
          nodeVersionFields = self.nodeVersion.split( "," );
          if( len( nodeVersionFields ) == 4 ):
            try:
              self.nodeBuild = int( nodeVersionFields[ 3 ] );
            except Exception, msg:
              pass;
        if(resp.has_key("Revision")):
          try:
            self.nodeRevision = int( resp[ "Revision" ] );
          except Exception, msg:
            pass;
        if(resp.has_key("ExtBuild")):
          try:
            self.nodeExtBuild = int( resp[ "ExtBuild" ] );
          except Exception, msg:
            pass;
        if(resp.has_key("Revision")):
          try:
            self.nodeExtRevision = int( resp[ "ExtRevision" ] );
          except Exception, msg:
            pass;
        if(resp.has_key("Testnet")):
          if( "true" == resp[ "Testnet" ] ):
            self.nodeIsTestnet = True;
          else:
            self.nodeIsTestnet = False;
        if(resp.has_key("ConnectionIdentifier")):
            self.connectionidentifier = resp[ "ConnectionIdentifier" ]
        
        return resp
    
    #@-node:_hello
    #@+node:_getUniqueId
    def _getUniqueId(self):
        """
        Allocate a unique ID for a request
        """
        timenum = int( time.time() * 1000000 );
        randnum = random.randint( 0, timenum );
        return "id" + str( timenum + randnum );
    
    #@-node:_getUniqueId
    #@+node:_txMsg
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
            self.socket.sendall(rawcmd)
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
    
        self.socket.sendall(raw)
    
    #@-node:_txMsg
    #@+node:_rxMsg
    def _rxMsg(self):
        """
        Receives and returns a message as a dict
        
        The header keyword is included as key 'header'
        """
        log = self._log
    
        log(DETAIL, "NODE: ----------------------------")
    
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
                else:
                    self.nodeIsAlive = False
                    raise FCPNodeFailure("FCP socket closed by node")
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
                
                # try to locate job
                id = items['Identifier']
                job = self.jobs[id]
                if job.stream:
                    # loop to transfer from socket to stream
                    remaining = items['DataLength']
                    stream = job.stream
                    while remaining > 0:
                        buf = self.socket.recv(remaining)
                        stream.write(buf)
                        stream.flush()
                        remaining -= len(buf)
                    items['Data'] = None
                else:
                    buf = read(items['DataLength'])
                    items['Data'] = buf
                log(DETAIL, "NODE: ...<%d bytes of data>" % len(buf))
                break
            else:
                # it's a normal 'key=val' pair
                try:
                    k, v = line.split("=", 1)
                except:
                    log(ERROR, "_rxMsg: barfed splitting '%s'" % repr(line))
                    raise
    
                # attempt int conversion
                try:
                    v = int(v)
                except:
                    pass
    
                items[k] = v
    
        # all done
        return items
    
    #@-node:_rxMsg
    #@+node:_log
    def _log(self, level, msg):
        """
        Logs a message. If level > verbosity, don't output it
        """
        if level > self.verbosity:
            return
    
        if(None != self.logfile):
            if not msg.endswith("\n"):
                msg += "\n"
            self.logfile.write(msg)
            self.logfile.flush()
        if(None != self.logfunc):
            while( msg.endswith("\n") ):
                msg = msg[ : -1 ]
            msglines = msg.split("\n")
            for msgline in msglines:
                self.logfunc(msgline)
    
    #@-node:_log
    #@-others
    #@-node:Low Level Methods
    #@-others
                

#@-node:class FCPNode
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
        
    Attributes of interest:
        - isPersistent - True if job is persistent
        - isGlobal - True if job is global
        - followRedirect - follow a redirect if true, otherwise fail the get
        - value - value returned upon completion, or None if not complete
        - node - the node this job belongs to
        - id - the job Identifier
        - cmd - the FCP message header word
        - kw - the keywords in the FCP header
        - msgs - any messages received from node in connection
          to this job
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, node, id, cmd, kw, **opts):
        """
        You should never instantiate a JobTicket object yourself
        """
        self.node = node
        self.id = id
        self.cmd = cmd
    
        self.verbosity = opts.get('verbosity', ERROR)
        self._log = opts.get('logger', self.defaultLogger)
        self.keep = opts.get('keep', False)
        self.stream = opts.get('stream', None)
        self.followRedirect = opts.get('followRedirect', False)
    
        # find out if persistent
        if kw.get("Persistent", "connection") != "connection" \
        or kw.get("PersistenceType", "connection") != "connection":
            self.isPersistent = True
        else:
            self.isPersistent = False
    
        if kw.get('Global', 'false') == 'true':
            self.isGlobal = True
        else:
            self.isGlobal = False
    
        self.kw = kw
    
        self.msgs = []
    
        callback = kw.pop('callback', None)
        if callback:
            self.callback = callback
    
        self.timeout = int(kw.pop('timeout', 86400*365))
        self.timeQueued = int(time.time())
        self.timeSent = None
    
        self.lock = threading.Lock()
        #print "** JobTicket.__init__: lock=%s" % self.lock
    
        self.lock.acquire()
        self.result = None
    
        self.reqSentLock = threading.Lock()
        self.reqSentLock.acquire()
    
    #@-node:__init__
    #@+node:isComplete
    def isComplete(self):
        """
        Returns True if the job has been completed
        """
        return self.result != None
    
    #@-node:isComplete
    #@+node:wait
    def wait(self, timeout=None):
        """
        Waits forever (or for a given timeout) for a job to complete
        """
        log = self._log
    
        log(DEBUG, "wait:%s:%s: timeout=%ss" % (self.cmd, self.id, timeout))
    
        # wait forever for job to complete, if no timeout given
        if timeout == None:
            log(DEBUG, "wait:%s:%s: no timeout" % (self.cmd, self.id))
            while not self.lock.acquire(False):
                time.sleep(0.1)
            self.lock.release()
            return self.getResult()
    
        # wait for timeout
        then = int(time.time())
    
        # ensure command has been sent, wait if not
        while not self.reqSentLock.acquire(False):
    
            # how long have we waited?
            elapsed = int(time.time()) - then
    
            # got any time left?
            if elapsed < timeout:
                # yep, patience remains
                time.sleep(1)
                log(DEBUG, "wait:%s:%s: job not dispatched, timeout in %ss" % \
                     (self.cmd, self.id, timeout-elapsed))
                continue
    
            # no - timed out waiting for job to be sent to node
            log(DEBUG, "wait:%s:%s: timeout on send command" % (self.cmd, self.id))
            raise FCPSendTimeout(
                    header="Command '%s' took too long to be sent to node" % self.cmd
                    )
    
        log(DEBUG, "wait:%s:%s: job now dispatched" % (self.cmd, self.id))
    
        # wait now for node response
        while not self.lock.acquire(False):
            # how long have we waited?
            elapsed = int(time.time()) - then
    
            # got any time left?
            if elapsed < timeout:
                # yep, patience remains
                time.sleep(2)
    
                #print "** lock=%s" % self.lock
    
                if timeout < ONE_YEAR:
                    log(DEBUG, "wait:%s:%s: awaiting node response, timeout in %ss" % \
                         (self.cmd, self.id, timeout-elapsed))
                continue
    
            # no - timed out waiting for node to respond
            log(DEBUG, "wait:%s:%s: timeout on node response" % (self.cmd, self.id))
            raise FCPNodeTimeout(
                    header="Command '%s' took too long for node response" % self.cmd
                    )
    
        log(DEBUG, "wait:%s:%s: job complete" % (self.cmd, self.id))
    
        # if we get here, we got the lock, command completed
        self.lock.release()
    
        # and we have a result
        return self.getResult()
    
    #@-node:wait
    #@+node:waitTillReqSent
    def waitTillReqSent(self):
        """
        Waits till the request has been sent to node
        """
        self.reqSentLock.acquire()
    
    #@-node:waitTillReqSent
    #@+node:getResult
    def getResult(self):
        """
        Returns result of job, or None if job still not complete
    
        If result is an exception object, then raises it
        """
        if isinstance(self.result, Exception):
            raise self.result
        else:
            return self.result
    
    #@-node:getResult
    #@+node:callback
    def callback(self, status, value):
        """
        This will be replaced in job ticket instances wherever
        user provides callback arguments
        """
        # no action needed
    
    #@-node:callback
    #@+node:cancel
    def cancel(self):
        """
        Cancels the job, if it is persistent
        
        Does nothing if the job was not persistent
        """
        if not self.isPersistent:
            return
    
        # remove from node's jobs lists
        try:
            del self.node.jobs[self.id]
        except:
            pass
        
        # send the cancel
        if self.isGlobal:
            isGlobal = "true"
        else:
            isGlobal = "False"
    
        self.node._txMsg("RemovePersistentRequest",
                         Global=isGlobal,
                         Identifier=self.id)
    
    #@-node:cancel
    #@+node:_appendMsg
    def _appendMsg(self, msg):
        self.msgs.append(msg)
    
    #@-node:_appendMsg
    #@+node:_putResult
    def _putResult(self, result):
        """
        Called by manager thread to indicate job is complete,
        and submit a result to be picked up by client
        """
        self.result = result
    
        if not (self.keep or self.isPersistent or self.isGlobal):
            try:
                del self.node.jobs[self.id]
            except:
                pass
    
        #print "** job: lock=%s" % self.lock
    
        try:
            self.lock.release()
        except:
            pass
    
        #print "** job: lock released"
    
    #@-node:_putResult
    #@+node:__repr__
    def __repr__(self):
        if self.kw.has_key("URI"):
            uri = " URI=%s" % self.kw['URI']
        else:
            uri = ""
        return "<FCP job %s:%s%s" % (self.id, self.cmd, uri)
    
    #@-node:__repr__
    #@+node:defaultLogger
    def defaultLogger(self, level, msg):
        
        if level > self.verbosity:
            return
    
        if not msg.endswith("\n"): msg += "\n"
    
        sys.stdout.write(msg)
        sys.stdout.flush()
    
    #@-node:defaultLogger
    #@-others

#@-node:class JobTicket
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

    TODO: Currently this uses sha1 as hash. Freenet uses 256. But the
          hashes are not used.
    
    Arguments:
      - dirpath - relative or absolute pathname of directory to scan
      - gethashes - also include a 'hash' key in each file dict, being
        the SHA1 hash of the file's name and contents
      
    Each returned dict in the sequence has the keys:
      - fullpath - usable for opening/reading file
      - relpath - relative path of file (the part after 'dirpath'),
        for the 'SSK@blahblah//relpath' URI
      - mimetype - guestimated mimetype for file

    >>> tempdir = tempfile.mkdtemp()
    >>> testfile = os.path.join(tempdir, "test")
    >>> with open(testfile, "w") as f:
    ...     f.write("test")
    >>> correct = [{'mimetype': 'text/plain', 'fullpath': os.path.join(tempdir, 'test'), 'relpath': 'test'}]
    >>> correct == readdir(tempdir)
    True
    >>> res = readdir(tempdir, gethashes=True)
    >>> res[0]["hash"] = hashFile(testfile)
    """
    
    #set_trace()
    #print "dirpath=%s, prefix='%s'" % (dirpath, prefix)
    entries = []
    for f in os.listdir(dirpath):
        relpath = prefix + f
        fullpath = os.path.join(dirpath, f)
        if f == '.freesiterc' or f.endswith("~"):
            continue
        if os.path.isdir(fullpath) \
        or os.path.islink(fullpath) and os.path.isdir(os.path.realpath(fullpath)):
            entries.extend(
                readdir(
                    os.path.join(dirpath, f),
                    relpath + os.path.sep,
                    gethashes
                    )
                )
        else:
            #entries[relpath] = {'mimetype':'blah/shit', 'fullpath':dirpath+"/"+relpath}
            fullpath = os.path.join(dirpath, f)
            entry = {'relpath' :relpath,
                     'fullpath':fullpath,
                     'mimetype':guessMimetype(f)
                     }
            if gethashes:
                entry['hash'] = hashFile(fullpath)
            entries.append(entry)
    entries.sort(lambda f1,f2: cmp(f1['relpath'], f2['relpath']))
    
    return entries

#@-node:readdir
#@+node:hashFile
def hashFile(path):
    """
    returns an SHA(1) hash of a file's contents

    >>> oslevelid, filepath = tempfile.mkstemp(text=True)
    >>> with open(filepath, "w") as f:
    ...     f.write("test")
    >>> hashFile(filepath) == hashlib.sha1("test").hexdigest()
    True
    """
    raw = file(path, "rb").read()
    return hashlib.sha1(raw).hexdigest()

def sha256dda(nodehelloid, identifier, path=None):
    """
    returns a sha256 hash of a file's contents for bypassing TestDDA

    >>> oslevelid, filepath = tempfile.mkstemp(text=True)
    >>> with open(filepath, "wb") as f:
    ...     f.write("test")
    >>> print sha256dda("1","2",filepath) == hashlib.sha256("1-2-" + "test").digest()
    True
    """
    tohash = "-".join([nodehelloid, identifier, file(path, "rb").read()])
    return hashlib.sha256(tohash).digest()

#@-node:hashFile
#@+node:guessMimetype
def guessMimetype(filename):
    """
    Returns a guess of a mimetype based on a filename's extension
    """
    if filename.endswith(".tar.bz2"):
        return ('application/x-tar', 'bzip2')
    
    m = mimetypes.guess_type(filename, False)[0]
    if m == None:
        m = "text/plain"
    return m

#@-node:guessMimetype
#@+node:uriIsPrivate
def uriIsPrivate(uri):
    """
    analyses an SSK URI, and determines if it is an SSK or USK private key

    for details see https://wiki.freenetproject.org/Signed_Subspace_Key

    >>> uriIsPrivate("SSK@~Udj39wzRUN4J-Kqn1aWN8kJyHL6d44VSyWoqSjL60A,iAtIH8348UGKfs8lW3mw0lm0D9WLwtsIzZhvMWelpK0,AQACAAE/")
    False
    >>> uriIsPrivate("SSK@R-skbNbiXqWkqj8FPDTusWyk7u8HLvbdysyRY3eY9A0,iAtIH8348UGKfs8lW3mw0lm0D9WLwtsIzZhvMWelpK0,AQECAAE/")
    True
    >>> uriIsPrivate("USK@AIcCHvrGspY-7J73J3VR-Td3DuPvw3IqCyjjRK6EvJol,hEvqa41cm72Wc9O1AjZ0OoDU9JVGAvHDDswIE68pT7M,AQECAAE/test.R1/0")
    True
    >>> uriIsPrivate("KSK@AIcCHvrGspY-7J73J3VR-Td3DuPvw3IqCyjjRK6EvJol,hEvqa41cm72Wc9O1AjZ0OoDU9JVGAvHDDswIE68pT7M,AQECAAE/test.R1/0")
    False
    >>> uriIsPrivate("SSK@JhtPxdPLx30sRN0c5S2Hhcsif~Yqy1lsGiAx5Wkq7Lo,-e0kLAjmmclSR7uL0TN901tS3iSx2-21Id8tUp4tyzg,AQECAAE/")
    True
    """
    # strip leading stuff
    if uri.startswith("freenet:"):
        uri = uri[8:]
    if uri.startswith("//"):
        uri = uri[2:]
    # actual recognition: SSK or USK
    if not (uri.startswith("SSK@") or uri.startswith("USK@")):
        return False
    try:
        symmetric, publicprivate, extra = uri.split(",")[:3]
    except (IndexError, ValueError):
        return False
    if "/" in extra:
        extra = extra.split("/")[0]
    extra += "/"
    extrabytes = base64.decodestring(extra)
    isprivate = ord(extrabytes[1])
    if isprivate:
        return True
    return False

#@-node:uriIsPrivate
#@+node:parseTime
def parseTime(t):
    """
    Parses a time value, recognising suffices like 'm' for minutes,
    's' for seconds, 'h' for hours, 'd' for days, 'w' for weeks,
    'M' for months.
    
    >>> endings = {'s':1, 'm':60, 'h':60*60, 'd':60*60*24, 'w':60*60*24*7, 'M':60*60*24*30}
    >>> not False in [endings[i]*3 == parseTime("3"+i) for i in endings]
    True

    Returns time value in seconds
    """
    if not t:
        raise Exception("Invalid time '%s'" % t)
    
    if not isinstance(t, str):
        t = str(t)
    
    t = t.strip()
    if not t:
        raise Exception("Invalid time value '%s'"%  t)
    
    endings = {'s':1, 'm':60, 'h':3600, 'd':86400, 'w':86400*7, 'M':86400*30}
    
    lastchar = t[-1]
    
    if lastchar in endings.keys():
        t = t[:-1]
        multiplier = endings[lastchar]
    else:
        multiplier = 1
    
    return int(t) * multiplier

#@-node:parseTime
#@+node:base64 stuff
# functions to encode/decode base64, freenet alphabet
#@+others
#@+node:base64encode
def base64encode(raw):
    """
    Encodes a string to base64, using the Freenet alphabet
    """
    # encode using standard RFC1521 base64
    enc = base64.encodestring(raw)
    
    # convert the characters to freenet encoding scheme
    enc = enc.replace("+", "~")
    enc = enc.replace("/", "-")
    enc = enc.replace("=", "_")
    enc = enc.replace("\n", "")
    
    return enc

#@-node:base64encode
#@+node:base64decode
def base64decode(enc):
    """
    Decodes a freenet-encoded base64 string back to a binary string
    
    Arguments:
     - enc - base64 string to decode
    """
    # TODO: Are underscores actually used anywhere?
    enc = enc.replace("_", "=")

    # Add padding. Freenet may omit it.
    while (len(enc) % 4) != 0:
        enc += '='

    # Now ready to decode. ~ instead of +; - instead of /.
    raw = base64.b64decode(enc, '~-')
    
    return raw

#@-node:base64decode
#@-others

#@-node:base64 stuff
#@-others

#@-node:util funcs
#@-others


#@-node:@file node.py
#@-leo

def _base30hex(integer):
    """Turn an integer into a simple lowercase base30hex encoding."""
    base30 = "0123456789abcdefghijklmnopqrst"
    b30 = []
    while integer:
        b30.append(base30[integer%30])
        integer = int(integer / 30)
    return "".join(reversed(b30))
        

def _test():
    import doctest
    tests = doctest.testmod()
    if tests.failed:
        return "☹"*tests.failed
    return "^_^ (" + _base30hex(tests.attempted) + ")"
        

if __name__ == "__main__":
    print _test()
