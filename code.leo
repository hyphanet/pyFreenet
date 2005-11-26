<?xml version="1.0" encoding="UTF-8"?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="127" clone_windows="0"/>
<globals body_outline_ratio="0.29999999999999999">
	<global_window_position top="32" left="104" height="659" width="1005"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences allow_rich_text="0">
</preferences>
<find_panel_settings>
	<find_string></find_string>
	<change_string></change_string>
</find_panel_settings>
<vnodes>
<v t="T1" a="E"><vh>NewHeadline</vh>
<v t="T2" a="E"><vh>Module Files</vh>
<v t="T3" a="E" tnodeList="3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103"><vh>@file freenet.py</vh>
<v t="T4"><vh>imports</vh></v>
<v t="T5"><vh>constants</vh></v>
<v t="T6" a="E"><vh>class node</vh>
<v t="T7"><vh>__init__</vh></v>
<v t="T8"><vh>get</vh></v>
<v t="T9"><vh>put</vh></v>
<v t="T10"><vh>getseq</vh></v>
<v t="T11"><vh>putseq</vh></v>
<v t="T12"><vh>putraw</vh></v>
<v t="T13"><vh>genkeypair</vh></v>
<v t="T14"><vh>genchk</vh></v>
<v t="T15"><vh>keyexists</vh></v>
<v t="T16"><vh>getsite</vh></v>
<v t="T17"><vh>putsite</vh></v>
<v t="T18"><vh>_connect</vh></v>
<v t="T19"><vh>_disconnect</vh></v>
<v t="T20"><vh>_rawtransaction</vh></v>
<v t="T21"><vh>_handshake</vh></v>
<v t="T22"><vh>_getsmart</vh></v>
<v t="T23"><vh>_getraw</vh></v>
<v t="T24"><vh>_put</vh></v>
<v t="T25"><vh>_send</vh></v>
<v t="T26"><vh>_sendline</vh></v>
<v t="T27"><vh>_sendhdr</vh></v>
<v t="T28"><vh>_recv</vh></v>
<v t="T29"><vh>_recvline</vh></v>
<v t="T30"><vh>_recvkeydata</vh></v>
<v t="T31"><vh>_recvchunk</vh></v>
<v t="T32"><vh>_genchk</vh></v>
<v t="T33"><vh>FEC methods</vh>
<v t="T34"><vh>_fecput</vh></v>
<v t="T35"><vh>_fecputfile</vh></v>
<v t="T36"><vh>_fecputfileex</vh></v>
<v t="T37"><vh>_fec_InsFecSplitPart</vh></v>
<v t="T38"><vh>_fec_retryInsert</vh></v>
<v t="T39"><vh>_fec_retryInsertFancy</vh></v>
<v t="T40"><vh>_fec_createManifest</vh></v>
<v t="T41"><vh>class _fec_threadData</vh></v>
<v t="T42"><vh>_fec_getMimetype</vh></v>
<v t="T43"><vh>_fec_makeSimpleMetadata</vh></v>
<v t="T44"><vh>_fec_makeDbr</vh></v>
<v t="T45"><vh>_fec_makeRedirect</vh></v>
<v t="T46"><vh>_fec_rebuildHdr</vh></v>
<v t="T47"><vh>_fec_makeMetadata</vh></v>
<v t="T48"><vh>_fec_segmentFile</vh></v>
<v t="T49"><vh>_fec_largeSend</vh></v>
<v t="T50"><vh>_fec_getNodeLoad</vh></v>
<v t="T51"><vh>_fec_openPort</vh></v>
<v t="T52"><vh>_fec_readMsg</vh></v>
<v t="T53"><vh>_fec_getFile</vh></v>
<v t="T54"><vh>_fec_removeTmpFiles</vh></v>
<v t="T55"><vh>_fec_clientGet</vh></v>
<v t="T56"><vh>_fec_segmentSplitFile</vh></v>
<v t="T57"><vh>_fec_decodeSegment</vh></v>
<v t="T58"><vh>_fec_getKey</vh></v>
<v t="T59"><vh>_fec_hexIndexList</vh></v>
<v t="T60"><vh>_fec_openSocket</vh></v>
<v t="T61"><vh>_fec_makeFakeMsg</vh></v>
<v t="T62"><vh>_fec_copyBinary</vh></v>
<v t="T63"><vh>_fec_zeroPad</vh></v>
<v t="T64"><vh>_fec_sameLength</vh></v>
<v t="T65"><vh>_fec_diffBinary</vh></v>
<v t="T66"><vh>_fec_concatFiles</vh></v>
<v t="T67"><vh>_fec_makeFilenames</vh></v>
<v t="T68"><vh>_fec_makeIndexList</vh></v>
<v t="T69"><vh>_fec_makeRebuiltFileList</vh></v>
<v t="T70"><vh>_fec_findMissingIndices</vh></v>
</v>
</v>
<v t="T71"><vh>class site</vh>
<v t="T72"><vh>__init__</vh></v>
<v t="T73"><vh>chkArgs</vh></v>
<v t="T74"><vh>put</vh></v>
<v t="T75"><vh>get</vh></v>
<v t="T76"><vh>readdir</vh></v>
<v t="T77"><vh>__get</vh></v>
<v t="T78"><vh>opendocfile</vh></v>
</v>
<v t="T79"><vh>class key</vh>
<v t="T80"><vh>__init__</vh></v>
<v t="T81"><vh>get</vh></v>
<v t="T82"><vh>put</vh></v>
</v>
<v t="T83"><vh>class uri</vh>
<v t="T84"><vh>__init__</vh></v>
<v t="T85"><vh>render</vh></v>
<v t="T86"><vh>dbr</vh></v>
<v t="T87"><vh>__repr__</vh></v>
<v t="T88"><vh>__str__</vh></v>
</v>
<v t="T89"><vh>class metadata</vh>
<v t="T90"><vh>attribs</vh></v>
<v t="T91"><vh>__init__</vh></v>
<v t="T92"><vh>add</vh></v>
<v t="T93"><vh>set</vh></v>
<v t="T94"><vh>targeturi</vh></v>
<v t="T95"><vh>documents</vh></v>
<v t="T96"><vh>parseRaw</vh></v>
<v t="T97"><vh>__repr__</vh></v>
<v t="T98"><vh>__str__</vh></v>
<v t="T99"><vh>parseRawLine</vh></v>
<v t="T100"><vh>render</vh></v>
</v>
<v t="T101"><vh>class Dispatcher</vh></v>
<v t="T102"><vh>global funcs</vh></v>
<v t="T103"><vh>exceptions</vh></v>
</v>
</v>
<v t="T104" a="E"><vh>Project Files</vh>
<v t="T105"><vh>@file Makefile</vh></v>
<v t="T106" tnodeList="106"><vh>@file README</vh></v>
<v t="T107" tnodeList="107"><vh>@file INSTALL</vh></v>
<v t="T108" a="V" tnodeList="108"><vh>@file setup.py</vh></v>
</v>
<v t="T109" a="E"><vh>Test Files</vh>
<v t="T110"><vh>@file autoexec.py</vh></v>
<v t="T111" tnodeList="111"><vh>@file latency-test.py</vh></v>
<v t="T112"><vh>@file sitetest.py</vh></v>
<v t="T113" a="E"><vh>@file testsuite.py</vh>
<v t="T114"><vh>declarations</vh></v>
<v t="T115"><vh>test01()</vh></v>
<v t="T116"><vh>test02()</vh></v>
<v t="T117"><vh>test03()</vh></v>
<v t="T118"><vh>test04()</vh></v>
<v t="T119"><vh>test05()</vh></v>
<v t="T120"><vh>test06()</vh></v>
<v t="T121"><vh>test07()</vh></v>
<v t="T122"><vh>test08()</vh></v>
<v t="T123"><vh>test09()</vh></v>
<v t="T124"><vh>test10()</vh></v>
<v t="T125"><vh>test11()</vh></v>
<v t="T126"><vh>run()</vh></v>
<v t="T127"><vh>mainline()</vh></v>
</v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="T1"></t>
<t tx="T2"></t>
<t tx="T3">@language python
# ***********************************************************************
#
# IMPORTANT NOTE!
#
# This code is best viewed and edited with the Leo meta-structural editor.
#
# If you look at this file raw with a regular text editor like
# emacs or vim, it will look like 4500 lines of spaghetti and
# will annoy you to no end.
#
# But if you open it with Leo, it will reveal itself as a clean and
# easily-understandable tree of classes and methods.
#
# Leo runs on *nix and Windoze systems, and is one amazing editor
# that leverages your effort by giving you easy multi-dimensional
# views of code. Also, it can integrate seamlessly with Emacs.
#
# You can get Leo from http://leo.sourceforge.net
#
# **********************************************************************

"""
Module freenet


Provides a high-level Python interface to the Freenet network,
fcptools backend has been replaced with totally Python socket access.

Portions of code, particularly relating to splitfiles and FEC, lifted
from GJ and fish - hearty thanks to you both for saving me from
painful duplicated effort.

This module and its component files (except GJ's and Fish's stuff)
written By David McNab &lt;david@rebirthing.co.nz&gt;
Copyright (c) 2003, all rights reserved.

Released under the GNU General Public License, www.gnu.org

This softare comes with absolutely no warranty. Use only at your
own risk. If it fries your hard disk, destroys your files, lands
you in jail, causes your liver to shut down etc - don't blame me.

"""

@others
</t>
<t tx="T4">import fnmatch, glob, md5, mimetypes, os, os.path, pickle
import random, re, socket, string, sys, tempfile
import thread, threading, Queue, time, types, warnings
import traceback

from UserString import MutableString
from pdb import set_trace

</t>
<t tx="T5">version = "0.2.4"

fcpRoundRobin=1
fcpRandom=2
fcpLoad=3


############################################################
# FCP Server dependant constants
FCP_HEADER_BYTES="\x00\x00\x00\x02"

# UNDOCUMENTED
# Causes _fec_clientGet and FCP_ClientPut
# to delete the local copy of the key from
# the node's data store before executing.
# see freenet.message.client.ClientRequest
FLAG_DELETELOCAL = 0x01

# MetadataHint kind constants
# defined in freenet.message.client.MetadataHint
MDH_DATA = 1
MDH_REDIRECT = 2
MDH_DATEREDIRECT = 3
MDH_SPLITFILE = 4
MDH_TOODUMB = 5
MDH_ERROR = 6

# Maximum size for non-CHK keys
MAX_SVK_SIZE = 32768

# flag to indicate if we've connected to an FCP host
#connected = False

logLevel = 2

defaultHost = "127.0.0.1"
defaultPort = 8481
defaultHtl = 15

defaultMaxSiteThreads = 8

defaultAllowSplitfiles = 1

# vars for FEC

</t>
<t tx="T6">class node:
    """
    'node' is the main class for working with Freenet.
    
    It contains methods for inserting and retrieving files and even
    entire freesites, plus a whole raft of lower level methods.
    """
    @others
</t>
<t tx="T7">def __init__(self, host=None, port=None, htl=20, **kw):
    """
    Constructs the freenet.node object
    
    Arguments:
     - host - hostname of freenet FCP interface, defaults to
       the global module variable 'defaultHost'
     - port - port of freenet FCP interface, defaults to
       the global module variable 'defaultPort'
     - htl - hops-to-live for insert/retrieve operations, defaults
       to 20
    
    Keywords:
     - future - for putsite operations, sets the default number of days
       in the future for which to insert freesites, defaults to 0
    """
    global defaultHost
    global defaultPort
    if host == None:
        self._host = defaultHost
    else:
        self._host = host
    if port == None:
        self._port = defaultPort
    else:
        self._port = port
    self._htl = htl
    self._recvbuf = ''
    self._recvbuflen = 0
    #self._handshake()

    # accept some keywords
    self._future = kw.get("future", 0)
    self._allowSplitfiles = kw.get("allowSplitfiles", 1)

    self._siteType = kw.get('siteType', 'dbr')
    self._edition = kw.get('edition', 0)
    self._editionMaxTries = kw.get('editionMaxTries', 0)
    
    self.metadataHeader = "Version\nRevision=1\nEndPart\n"

</t>
<t tx="T8">def get(self, keyuri, htl=None, raw=False, past=0):
    """
    retrieves a key from Freenet

    Arguments:
     - uri - uri of key to request
     - htl - hops to live - default 20
     - raw - whether to fetch the raw key, and not interpret metadata (false)
     - past - number of periods in the past to regress (dbr keys only)

    Returns:
     - a freenet.key object containing the retrieved key

    Exceptions:
     - FreenetFcpError - details in error value
    """

    if htl == None:
        htl = self._htl

    # Fetch and return a key object
    if raw:
        # easy case
        return self._getraw(keyuri, htl)
    else:
        return self._getsmart(keyuri, htl, 'text/plain',
                              past=past)

</t>
<t tx="T9">def put(self,
        keydata=None, keymeta=None,
        keyuri='CHK@',
        htl=None, allowSplitfiles=defaultAllowSplitfiles,
        **args):

    """
    Smarter key insertion routine that inserts via splitfiles
    and FEC if needed

    Arguments:
     - keydata - string of data to insert. Defaults to ''
     - keymeta - string of metadata to insert. Defaults to a minimal
       metadata file
     - keyuri - uri object or URI string to insert as. If None or '',
       inserts the key as a CHK
     - htl - hops-to-live, default 20 (I think)
    Keywords:
     - mimetype - if keymeta is None or '', a metadata block is created
       which declares the default doc to have this mimetype.
     - host - lets you override host setting
     - port - lets you override port setting
    Returns:
     - IF called statically, returns a complete key object containing
       the key, its data, metadata and uri

    NOTE!!! You no longer have to worry about the 32k size limit for KSK, SVK and SSK
    keys. If you try to insert something bigger than 32k, this method will transparently
    insert it as a CHK, then insert a redirector at your original URI. So feel free to
    insert any size key under KSK, SVK and SSK - the get() method can get it back
    transparently.
    """

    # Set defaults
    if keydata == None:
        keydata = ''
    if keymeta == None or (type(keymeta) == type("") and keymeta == ''):
        keymeta = metadata()
        mimetype = args.get('mimetype', None)
        if mimetype:
            keymeta.add("", mimetype=mimetype)
    if not isinstance(keyuri, uri):
        if keyuri == None or (type(keyuri) == type("") and keyuri == ''):
            keyuri = uri('CHK@')
    if htl == None:
        htl = getattr(self, '_htl', defaultHtl)

    # if KSK, SVK or SSK, and &gt;32k, insert a CHK redirect
    uriTxt = str(keyuri)
    if uriTxt[0:4] in ['SSK@', 'SVK@', 'KSK@'] and len(keydata) &gt;= 32768:

        LOGMSG(3, "key '%s' is too big - redirecting to CHK" % uriTxt)

        # insert as a CHK
        kChk = self.put(keydata, keymeta, 'CHK@', htl, allowSplitfiles, **args)
        uriChk = str(kChk.uri)

        # create redirection metadata
        metaRedir = metadata()
        metaRedir.add('', 'Redirect', target=uriChk)

        # insert the redirector at original requested URI
        k = self.put('', metaRedir, uriTxt, htl, 0, **args)

        #if not k:
        #    LOGMSG(3, "************ put() returned nothing?!?!?")

        # all done
        return k
    
    # If key is large, insert via fish
    if len(keydata) &lt;= 1024*1024 or not allowSplitfiles:
        k = self.putraw(keydata, keymeta, keyuri, htl)
        #if not k:
        #    LOGMSG(3, "************ putraw() returned nothing?!?!?")
        return k
    else:
        LOGMSG(3, "Inserting data via FEC")

        # Big bugger - insert with fish's FCP FEC magic
        newuri = self._fecput(str(keyuri), keydata, htl)

        # fetch it back - raw - and return as key object
        k = self.get(newuri, htl, True)

        return key(keydata, k.metadata, newuri, host=self._host, port=self._port)



</t>
<t tx="T10">def getseq(self, keyprefix, startnum=0, numtries=5, htl=None, raw=False):
    """
    Retrieves a sequenced key.
    
    Sequenced keys allow for implementation of in-Freenet 'queues',
    to/from which different parties can insert/retrieve messages.
    
    Example:
      - KSK@somequeuename-1, KSK@somequeuename-2, ...
    
    This function attempts to retrieve the key URI &lt;keyprefix&gt;&lt;startnum&gt;.
    If this fails, then tries to get &lt;keyprefix&gt;&lt;startnum+1&gt; right up to
    &lt;keyprefix&gt;&lt;startnum+numtries-1&gt;
    
    If a key is successfully retrieved, it is returned.
    Otherwise, the FreenetKeySequenceFail exception occurs
    
    Arguments:
     - keyprefix - the prefix of the URI queue. For instance, if you
       are fetching keys 'KSK@myqueue-1', 'KSK@myqueue-2'..., then
       this argument should be 'KSK@myqueue-'. Note the trailing
       hyphen - otherwise this method would try 'KSK@myqueue1', 'KSK@myqueue2'...
     
     - startnum - the starting sequence number of the key. For instance,
       if keyprefix is 'KSK@myqueue-', and startnum is 15, then this
       method will try 'KSK@myqueue-15', 'KSK@myqueue-16', ...
       Defaults to 0
     
     - numtries - sets a limit on how far to look ahead in the queue.
       For instance, with keyprefix = 'KSK@myqueue-', and startnum = 15,
       and numtries = 7, this method will try 'KSK@myqueue-15',
       'KSK@myqueue-16', ..., 'KSK@myqueue-21' inclusive.
       Defaults to 5
     
     - htl - determines the HTL value to use in the key fetches.
       Defaults to the node object's HTL setting.
    
     - raw - if set, prevents smart key handling (such as DateRedirects,
       Redirects, SplitFiles etc. Defaults to False.
    """
    keyprefix = str(keyprefix)
    startnum = int(startnum)
    numtries = int(numtries)
    
    trynum = 0
    
    while trynum &lt; numtries:
        tryuri = keyprefix + str(startnum+trynum)
        try:
            return self.get(tryuri, htl, raw)
        except FreenetDataNotFound, FreenetRouteNotFound:
            pass
        except:
            raise
        trynum = trynum + 1
    raise FreenetDataNotFound("%s[%d-%d]" % (keyprefix, startnum, startnum+numtries-1))
</t>
<t tx="T11">def putseq(self, keyprefix, startnum=0, numtries=5, keydata='', keymeta=None, htl=None, **kw):
    """
    Inserts a sequenced key.
    
    Sequenced keys allow for implementation of in-Freenet 'queues',
    to/from which different parties can insert/retrieve messages.
    
    Example:
      - KSK@somequeuename/1, KSK@somequeuename/2, ...
    
    This function attempts to insert the key URI &lt;keyprefix&gt;&lt;startnum&gt;.
    If this fails, then tries to insert &lt;keyprefix&gt;&lt;startnum+1&gt; right up to
    &lt;keyprefix&gt;&lt;startnum+numtries-1&gt;
    
    If a key is successfully inserted without collisions, it is returned.
    Otherwise, the FreenetKeySequenceFail exception occurs
    
    Arguments:
     - keyprefix - the prefix of the URI queue. For instance, if you
       are inserting keys 'KSK@myqueue-1', 'KSK@myqueue-2'..., then
       this argument should be 'KSK@myqueue-'. Note the trailing
       hyphen - otherwise this method would try 'KSK@myqueue1', 'KSK@myqueue2'...
     
     - startnum - the starting sequence number of the key. For instance,
       if keyprefix is 'KSK@myqueue-', and startnum is 15, then this
       method will try 'KSK@myqueue-15', 'KSK@myqueue-16',
       Defaults to 0
     
     - numtries - sets a limit on how far to look ahead in the queue.
       For instance, with keyprefix = 'KSK@myqueue-', and startnum = 15,
       and numtries = 7, this method will try 'KSK@myqueue-15',
       'KSK@myqueue-16', ..., 'KSK@myqueue-21' inclusive.
       Defaults to 5.
       Set to -1 to try endlessly
     
     - keydata - data of key to insert
     
     - keymeta - metadata string

     - htl - determines the HTL value to use in the key inserts
       Defaults to the node object's HTL setting.
    """
    keyprefix = str(keyprefix)
    startnum = int(startnum)
    numtries = int(numtries)

    allowSplitfiles = kw.get('allowSplitfiles', 1)

    # if KSK, SVK or SSK, and &gt;32k, insert a CHK redirect
    uriTxt = str(keyprefix)
    #if uriTxt[0:4] in ['SSK@', 'SVK@', 'KSK@'] and len(keydata) &gt;= 32768:
    if len(keydata) &gt;= 32768:

        LOGMSG(3, "key '%s' is too big - redirecting to CHK" % uriTxt)

        # insert as a CHK
        kChk = self.put(keydata, keymeta, 'CHK@', htl, allowSplitfiles, **kw)
        uriChk = str(kChk.uri)

        # create redirection metadata
        metaRedir = metadata()
        metaRedir.add('', 'Redirect', target=uriChk)

        # frig - set up to insert the pointer key's data/metadata
        keydata = ''
        keymeta = metaRedir
        
        # insert the redirector at original requested URI
        #k = self.put('', metaRedir, uriTxt, htl, 0, **args)

        #if not k:
        #    LOGMSG(3, "************ put() returned nothing?!?!?")

        # all done
        #return kChk
    
    
    trynum = 0
    while numtries &lt; 0 or trynum &lt; numtries:
        tryuri = keyprefix + str(startnum+trynum)
        try:
            k = self.put(keydata, keymeta, tryuri, htl=None)
            #if not k:
            #    LOGMSG(3, "************ put() returned nothing?!?!?")
            k.seq = startnum + trynum
            return k

        except FreenetKeyCollision, FreenetRouteNotFound:
            pass
        except:
            raise
        trynum = trynum + 1
    raise FreenetKeyInsertFail("%s[%d-%d]" % (keyprefix, startnum, startnum+numtries-1))


</t>
<t tx="T12">def putraw(self, *args, **kwds):
    """
    Inserts a key into freenet - raw, without any splitfiles or FEC rubbish

    Calling options:
     1. Insert a URI object:
        - Arguments:
           - key - uri object of key to insert
           - uri - if None, uses key's uri attrib. IF this attrib is none,
             inserts the key as a CHK and stores that CHK into the key object
           - htl - Hops To Live, defaults to 20
        - Returns:
           - uri object that key is inserted under
     2. Insert raw data and metadata:
        - Arguments:
           - keydata - string of data to insert
           - meta - string of key metadata (or a metadata object)
           - uri - uri object or string to insert under. If not provided,
             the key is inserted as a CHK
           - htl - Hops to Live for insert, default 20
        - Returns:
           - key object for inserted key

    Exceptions:
      - FreenetFcpError - details in exception's 'value' attribute
    """

    # First validation
    #set_trace()
    lenargs = len(args)
    if lenargs == 0:
        raise FreenetFcpError("fcp._put: must give key data, uri, [htl]")

    # Action depends on arg type
    keydata = args[0]
    if isinstance(keydata, key):
        # got a key object - insert it
        if lenargs &gt; 1:
            keyuri = args[1]
            if keyuri == None:
                keyuri = keydata.uri
            if keyuri == None:
                keyuri = ''
            if lenargs &gt; 2:
                htl = args[2]
            else:
                htl = None
        else:
            keyuri = keydata.uri
            if keyuri == None:
                keyuri = ''
            if str(keyuri) == '':
                keyuri = 'CHK@'
            htl = self.htl

        # allow keywords args
        htl = kwds.get('htl', htl)
        
        meta = str(keydata.metadata)
        inserteduri = self._put(str(keydata), str(meta), str(keyuri), htl)
        keydata.uri = inserteduri

        #if not inserteduri:
        #    LOGMSG(3, "************ _put() returned nothing?!?!?")

        return inserteduri
    else:
        # just raw data - insert it and make up a key object
        if lenargs &gt; 1:
            meta = metadata(args[1])
            if lenargs &gt; 2:
                keyuri = args[2]
                if keyuri == None:
                    keyuri = ''
                if str(keyuri) == '':
                    keyuri = 'CHK@'
                keyuri = uri(keyuri)
                if lenargs &gt; 3:
                    htl = args[3]
                else:
                    htl = None
            else:
                keyuri = 'CHK@'
                htl = None
        else:
            meta = ''
            keyuri = 'CHK@'
            htl = None
        
        # allow keywords args
        htl = kwds.get('htl', htl)

        inserteduri = self._put(str(keydata), str(meta), str(keyuri), htl)

        #if not inserteduri:
        #    LOGMSG(3, "*********!!! _put() returned nothing?!?!?")

        #set_trace()
        keyobj = key(keydata, meta, inserteduri, host=self._host, port=self._port)
        return keyobj

</t>
<t tx="T13">def genkeypair(self):
    """
    Generates an SVK keypair, needed for inserting SSK freesites

    Arguments:
     - none
    Returns:
     - Keypair as (public, private) tuple
    Exceptions:
     - FreenetFcpError - details in error value
    """

    self._connect()
    self._sendline("GenerateSVKPair")
    self._sendline("EndMessage")

    # We should get back some keys
    pubkey = None
    privkey = None
    resp = self._recvline()
    if resp != "Success":
        raise FreenetFcpError("makekeypair: expecting 'Success', got '%s'" % resp)
    while 1:
        resp = self._recvline()
        if resp == 'EndMessage':
            break
        fld, val = resp.split("=", 1)
        if fld == 'PublicKey':
            pubkey = val
        elif fld == 'PrivateKey':
            privkey = val
        else:
            #print "makekeypair: strange node response '%s'" % resp
            continue
            raise FreenetFcpError("makekeypair: strange node response '%s'" % resp)

    if pubkey == None:
        raise FreenetFcpError("makekeypair: node sent no public key")
    if privkey == None:
        raise FreenetFcpError("makekeypair: node sent no private key")

    return pubkey, privkey
</t>
<t tx="T14">def genchk(self, keydata, meta=None):
    """
    Calculates the CHK for a block of data and metadata,
    
    genchk(data, metadata)

    Useful if you need to know a key's CHK before you insert it.

    Option 1 - pass in key object, CHK uri gets added to object:
     - Arguments:
       - keyobj - a freenet.key instance
     - Returns:
       - generated URI object
     - Note:
       - The key object is updated by having the CHK uri added to it

    Option 2 - pass in raw data and metadata strings, get back a URI object
     - Arguments:
       - data - string of raw data
       - metadata - string of raw metadata (default '')
     - Returns:
       - a uri object, being the CHK key uri

    Exceptions:
     - FreenetFcpError - details in exception's value attrib
    """

    if isinstance(keydata, key):
        if meta != None:
            raise FreenetFcpError("genchk: invalid arguments - RTFD")
        rawdata = str(keydata)
        rawmeta = str(keydata.metadata)
        chk = self._genchk(rawdata, rawmeta)
        keydata.uri = chk
        return chk
    else:
        rawdata = str(keydata)
        if meta == None:
            rawmeta = ''
        else:
            rawmeta = str(meta)
        chk = self._genchk(rawdata, rawmeta)
        return chk
</t>
<t tx="T15">def keyexists(self, keyuri, htl=None):
    """
    Attempts to fetch key from freenet.

    Arguments:
     - keyuri - uri object or URI string of key
     - htl - hops-to-live
    Returns:
     - True if key exists, or False if it couldn't be retrieved
    """

    #if not isinstance(self, node):
    #    inst = node()
    #    return inst.keyexists(keyuri, htl)

    if htl == None: htl = self._htl
    self._connect()
    try:
        self._sendline("ClientGet")
        self._sendline("URI=%s" % str(keyuri))
        self._sendline("HopsToLive=%d" % htl)
        self._sendline("EndMessage")
    
        # wait for response
        while 1:
            resp = self._recvline()
            if resp == 'Restarted':
                continue
            elif resp == 'DataFound':
                self._disconnect()
                return True
            else:
                break
    except:
        pass
    self._disconnect()
    return False
</t>
<t tx="T16">def getsite(self, siteuri=None, todir=None, docname=None, **args):
    """
    Retrieves a freesite, lock, stock'n'barrel.

    Arguments (not required if instance vars present):
     - siteuri - full URI of site to retrieve
     - todir - directory to store the retrieved site
       Note - this direcctory must already exist.
    Keywords:
     - past - number of time intervals (default 0) to regress
       when retrieving the site. Note that most DBR sites work
       at offset 0, increment 86400 (1 day)
     - htl - hops to live - how deeply to delve within the Freenet
       for retrieving this site
     - docname - only used during recursive calls - ignore this
     - host - FCP host to use, defaults to constructor arg
     - port - FCP port to use - defaults to constructor arg
    Returns:
     - True if retrieval succeeded, False if failed
    Note:
     - Site's files will be written *into* directory 'todir'
       So if you're fetching 'SSK@blahblah/somesite', you should
       perhaps create a directory called 'somesite' somewhere first.
    """
    if not args.has_key('host'):
        args['host'] = self._host
    if not args.has_key('port'):
        args['port'] = self._port

    siteobj = site(**args)
    return siteobj.get(siteuri, todir, docname)
</t>
<t tx="T17">def putsite(self, fromdir=None, **args):
    """
    Insert this site object into freenet as a complete freesite
    Arguments:
     - fromdir - directory to insert form. If not given, attempts to
       take this from instance variables
    Keywords:
     - host - FCP host to use, defaults to constructor arg
     - port - FCP port to use - defaults to constructor arg
     - name (optional, defaults to 'site'
       called, otherwise taken from instance var
     - htl - optional, default 20
     - pub - ssk public key
     - priv - ssk private key
     - future - optional, defaultx to the 'future' constructor keyword 
     - default - file to use as site default, default 'index.html'
     - splitsize - size of splitfile chunks, default 262144
     - offset - dbr offset, default 0
     - increment - dbr increment, default 86400
     - maxthreads - maximum number of parallel insert threads
     - allowSplitfiles - default 1, allow large files to be split
     - files - dict of files to insert into the freesite.

       You may only specify this keyword if you don't pass a 'fromdir' arg.
       
       The keys of the dict are
       relative paths (as they appear, for example:
         - the 'path/to/file.txt' in 'SSK@BblahblahPAgM/fred//path/to/file.txt'.
       The value is a dict containing the keys:
         - mimetype - a standard mimetype string, AND one of:
             - raw - a raw string comprising the file's content, OR
             - fullpath - an absolute path on the host filesystem
       Example::

         { 'index.html' ;     {'mimetype' : 'text/html',
                               'raw' : '&lt;html&gt;&lt;body&gt;Here is index.html&lt;/body&gt;&lt;/html&gt;'
                               },
           '/fred/mary.txt' : {'mimetype' : 'text/plain',
                               'raw' : 'This is fred/mary.txt'
                               },
           }

    Returns:
     - a uri object for the inserted site

    After any insertion attempt, the pub/priv keypair, htl, splitsize, offset
    and increment get stored in a pickle in file /.freesiterc in the site's
    directory - but only if the caller did not pass a fileset
    """
    if not args.has_key('host'):
        args['host'] = self._host
    if not args.has_key('port'):
        args['port'] = self._port
    if not args.has_key('htl'):
        args['htl'] = self._htl
    if not args.has_key('future'):
        args['future'] = self._future
    if not args.has_key('allowSplitfiles'):
        args['allowSplitfiles'] = self._allowSplitfiles

    if not args.has_key('siteType'):
        args['siteType'] = self._siteType
    if not args.has_key('edition'):
        args['edition'] = self._edition
    if not args.has_key('editionMaxTries'):
        args['editionMaxTries'] = self._editionMaxTries
    if not args.has_key('maxthreads'):
        args['maxthreads'] = defaultMaxSiteThreads

    if args.has_key('files'):
        files = args['files']
        del args['files']
    else:
        files = None
    siteobj = site(**args)
    
    if files:
        return siteobj.put(fromdir, files=files)
    else:
        return siteobj.put(fromdir)

</t>
<t tx="T18">def _connect(self):
    try:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._host, self._port))
        self._sendhdr()
    except:
        raise FreenetFcpConnectError("Failed to connect to '%s:%d'" % (self._host, self._port))

    self._recvbuf = ''
    self._recvbuflen = 0

</t>
<t tx="T19">def _disconnect(self):
    self._sock.close()
    self._recvbuf = ''
    self._recvbuflen = 0

</t>
<t tx="T20">def _rawtransaction(self, txdata):
    """
    Sends a raw block of data to node, and returns raw response.
    """
    self._send(txdata)
    rx = self._recv(32768)
    self._disconnect()
    return rx
</t>
<t tx="T21">def _handshake(self):
    self._connect()
    self._sendline("ClientHello")
    self._sendline("EndMessage")

    line = self._recvline()
    if line != 'NodeHello':
        LOGMSG(2, "Bad resp: '%s'" % line)
        raise FreenetFcpError(
            "I'm not sure that '%s:%s' is a real Freenet or Entropy FCP Port" % (self._host, self._port))
        while 1:
            line = self._recvline()
            if line == 'EndMessage':
                self._disconnect()
                return None
        return None

    resp = ''
    flds = {}
    while 1:
        x = self._recvline()
        if x == 'EndMessage':
            self._disconnect()
            self.nodeinfo = flds
            return
        fld, val = x.split("=", 1)
        flds[fld] = val
    pass


</t>
<t tx="T22">def _getsmart(self, keyuri, htl=20, mimetype='text/plain', **kw):
    """
    Recursive method which follows redirects and msk chains,
    reassembles splitfiles, till the target doc is retrieved
    
    Arguments:
        - keyuri - the URI to fetch
        - htl - default 20
        - mimetype - the default mimetype to assign to the data
    
    Keywords:
        - past - only applies to DBR - number of periods in the past to regress, default 0
    """

    past = kw.get('past', 0)

    if not isinstance(keyuri, uri):
        keyuri = uri(keyuri)

    rawuri = str(keyuri).split("//", 1)[0]

    k = self._getraw(rawuri, htl)
    doc = keyuri.mskpath.split('//')[0] # first part of MSK path

    if k.metadata:
        tgt = k.metadata.targeturi(doc, -past)
        # grab a mimetype if one given

        if k.metadata.map.has_key(doc):
            if k.metadata.map[doc].has_key('mimetype'):
                mimetype = k.metadata.map[doc]['mimetype']
    else:
        k.mimetype = mimetype
        return k

    if tgt == None:
        k.mimetype = mimetype
        return k # we're at final destination with this key

    elif isinstance(tgt, uri):
        # re-fucking-cursion
        return self._getsmart(tgt, htl, mimetype)

    elif type(tgt) is types.ListType:
        # We've got a splitfile - dive off into GJ-land for now
        f = tempFilename()
        if self._fec_getFile(str(keyuri), f, self._host, self._port, htl):
            fd = open(f)
            data = fd.read()
            fd.close()
            os.unlink(f)

            #set_trace()
            m = metadata()
            m.add('')
            km = k.metadata.map['']
            m.set('', 'Info.Format', km.get('Info.Format', 'text/plain'))
            if km.has_key('Info.Description'):
                m.set('', 'Info.Description', km['Info.Description'])
            k = key(data, m, keyuri, host=self._host, port=self._port)
            k.mimetype = km.get('Info.Format', mimetype)
            return k
        else:
            raise FreenetFcpError("getsmart: FEC error: %s" % keyuri)
    else:
        raise FreenetFcpError("getsmart: strange uri target on %s" % keyuri)


</t>
<t tx="T23">def _getraw(self, keyuri, htl=None):
    """
    retrieves a key from Freenet, with no interpretation of
    metadata
    
    Arguments:
     - uri - uri of key to request
     - htl - hops to live - default 20
    Returns:
     - tuple (key, metadata)
    Exceptions:
     - FreenetFcpError - details in error value
    """

    if htl == None:
        htl = self._htl
    data = ''
    meta = ''

    # 'normalise' the uri
    keyuri = uri(keyuri)

    # connect and send key request
    self._connect()
    self._state = 'wait' # 'wait', 'hdr', 'meta' or 'data'

    try:
        self._sendline("ClientGet")
        self._sendline("URI=%s" % str(keyuri))
        self._sendline("HopsToLive=%x" % htl)
        self._sendline("EndMessage")
    
        # wait for response
        while 1:
            if self._state == 'wait':
                resp = self._recvline()
                if resp == 'URIError':
                    raise FreenetFcpError("Node dislikes URI '%s'" % keyuri)
                elif resp == 'Restarted':
                    self._state = 'waitrestart'
                    continue
                elif resp == 'DataNotFound':
                    raise FreenetDataNotFound("Key Not Found: '%s'" % keyuri)
                elif resp == 'RouteNotFound':
                    raise FreenetRouteNotFound("Route Not Found: '%s'" % keyuri)
                elif resp == 'DataFound':
                    self._state = 'hdr'
                    continue
                else:
                    raise FreenetFcpError("Strange node response: '%s'" % resp)

            elif self._state == 'waitrestart':
                resp = self._recvline()
                if resp.startswith("Timeout="):
                    LOGMSG(4, "Got '%s'" % resp)
                    continue
                elif resp == 'EndMessage':
                    self._state = 'wait'
                    continue

            elif self._state == 'hdr':
                # receive data header
                datalen = 0
                metalen = 0
                data = ''
                while 1:
                    resp = self._recvline()
                    if resp == 'EndMessage':
                        break # move on and get data
                    fld, val = resp.split("=", 1)
                    if fld == 'DataLength':
                        datalen = int(val, 16)
                    elif fld == 'MetadataLength':
                        metalen = int(val, 16)

                # IIRC, 'DataLength' includes metadata - need to adjust
                datalen -= metalen

                if metalen &gt; 0:
                    self._state = 'meta'
                else:
                    self._state = 'data'
                continue

            elif self._state == 'meta':
                meta = self._recvkeydata(metalen)
                if meta == None:
                    # whoops - restarted - back to start
                    self._state = 'wait'
                    continue
                # got metadata just fine
                self._state = 'data'
                continue

            elif self._state == 'data':
                #set_trace()
                data = self._recvkeydata(datalen)
                if data == None:
                    # whoops - restarted - back to start
                    self._state = 'wait'
                    self._recvbuf = ''
                    continue

            # everything has arrived just as we want it
            self._disconnect()
            return key(data, meta, keyuri, host=self._host, port=self._port)

    except:
        self._disconnect()
        raise

</t>
<t tx="T24">def _put(self, rawdata, rawmeta, keyuri, htl=None):
    """
    Lower-level key insert routine.
    Arguments:
     - rawdata - raw key data to insert
     - rawmeta - metadata string or object
     - keyuri - uri string or object
     - htl - Hops to Live, defaults to self.htl, which defaults to 20
    Returns:
     - uri object for inserted key
    Exceptions:
     - FreenetFcpError - details in exception's 'value' attribute
    """

    if rawdata == None:
        rawdata = ''
    if rawmeta == None:
        rawmeta = ''
    if keyuri == None:
        keyuri = ''
    else:
        keyuri = str(keyuri)
    if rawdata == '' and rawmeta == '' and keyuri == '':
        raise FreenetFcpError("_put: no data, no metadata, no uri")

    # if no uri, default to inserting CHK
    if keyuri == '':
        keyuri = 'CHK@'

    if htl == None:
        htl = self._htl
    if htl == None:
        htl = 20

    collision = 0 # flag - indicates collision with different content

    metalen = len(rawmeta)
    datalen = len(rawdata) + metalen

    # send data and metadata to node
    self._connect()
    self._sendline("ClientPut")
    self._sendline("HopsToLive=%x" % htl)
    self._sendline("URI=%s" % str(keyuri))
    self._sendline("DataLength=%x" % datalen)
    if metalen &gt; 0:
        self._sendline("MetadataLength=%x" % metalen)
    self._sendline("Data")
    if metalen &gt; 0:
        self._send(rawmeta)
    self._send(rawdata)

    # Await confirmation
    while 1:
        resp = self._recvline()
        if resp == 'URIError':
            raise FreenetFcpError("fcp._put: Note dislikes uri '%s'" % keyuri)
        elif resp == 'Restarted':
            while 1:
                resp = self._recvline()
                if resp == 'EndMessage':
                    break
                else:
                    continue
            continue
        elif resp == 'RouteNotFound':
            raise FreenetRouteNotFound("Key '%s'" % keyuri)
        elif resp == 'SizeError':
            raise FreenetFcpError("Key '%s' limited to 32k of data" % keyuri)
        elif resp == 'Pending':
            # discard remainder of 'Pending' message
            while self._recvline() != 'EndMessage':
                pass
            continue
        elif resp != 'Success' and resp != 'KeyCollision':
            raise FreenetFcpError("fcp._put: expected 'Success', got '%s'" % resp)

        if resp == 'KeyCollision':
            collision = 1

        pubkey = None
        privkey = None
        while 1:
            resp = self._recvline()
            fld = resp.split("=")
            if fld[0] == 'URI':
                keyuri = uri(fld[1])
            elif fld[0] == 'PublicKey':
                pubkey = fld[1]
            elif fld[0] == 'PrivateKey':
                privkey = fld[1]
            elif resp == 'EndMessage':
                break
        break

    # got success or collision packet from node
    # TODO - incorporate better handling of KeyCollision
    if collision:
        # retrieve the key back and compare
        retrkey = self._getraw(keyuri, htl)
        if retrkey.data != rawdata or retrkey.metadata != rawmeta:
            # what we got back ain't what we stuck in - this is not good
            LOGMSG(2, "fcp._put: collision - existing data at key '%s' differs" % str(keyuri))
            raise FreenetKeyCollision("Key '%s' is already present with differing data" % str(keyuri))
        else:
            LOGMSG(3, "fcp._put: collision - existing data at key '%s' is identical - no problem" % str(keyuri))

    if pubkey != None:
        keyuri.sskpub = pubkey
    if privkey != None:
        keyuri.sskpriv = privkey
    return keyuri
</t>
<t tx="T25">def _send(self, buf):
    #set_trace()
    return self._sock.send(buf)
</t>
<t tx="T26">def _sendline(self, line):
    LOGMSG(4, "to host: %s" % line)
    self._send(line + "\n")
</t>
<t tx="T27">def _sendhdr(self):
    self._send('\x00\x00\x00\x02')
</t>
<t tx="T28">def _recv(self, max):

    #LOGMSG(4, "_recv: wanting %d bytes" % max)
    buf = self._sock.recv(max)
    #LOGMSG(4, "_recv: got %d bytes" % max)
    return buf

    chars = []
    rcvd = 0
    try:
        while rcvd &lt; max:
            c = self._sock.recv(1)
            chars.append(c)
            rcvd = rcvd + 1
    except:
        LOGMSG(4, "_recv: timed out")
    LOGMSG(4, "_recv: got %d bytes" % rcvd)
    buf = "".join(chars)
    return buf
</t>
<t tx="T29">def _recvline(self):
    line = ''
    while 1:
        ch = self._sock.recv(1)
        if ch == '\n':
            LOGMSG(4, "from host: '%s'" % line)
            return line
        line += ch
</t>
<t tx="T30">def _recvkeydata(self, len):
    """
    Receives incoming key data, guaranteeing the delivery of len bytes.
    This is used in key receive

    Arguments:
     - len - number of bytes to receive
    Returns:
     - received bytes, as a string, if received OK
     - None if a 'Restarted' message is received

    Note:
     - This routine is 'all or nothing', in that it guarantees either the full
       complement of requested data, or None if a restart occurs
     - Since a metadata-&gt;data transition is not guaranteed to occur at DataChunk
       boundaries (ie, can occur *within* a DataChunk), this routine needs to do
       buffering via self._recvbuf, and receive discrete chunks via
       self._recvchunk()
    """

    # loop around till we get everything, or a restart
    while len &gt; self._recvbuflen:

        # keep receiving chunks till our buffer is big enough to fulfil request
        #set_trace()
        buf, buflen = self._recvchunk()
        if buf == None:
            # got a restart - bail out here
            self._recvbuf = ''
            self._recvbuflen = 0
            return None

        # add this chunk to our buffer
        self._recvbuf += buf
        self._recvbuflen += buflen

    # got enough now
    buf = self._recvbuf[0:len]
    #del self._recvbuf[0:len]
    self._recvbuf = self._recvbuf[len:]
    self._recvbuflen -= len
    return buf
</t>
<t tx="T31">def _recvchunk(self):
    """
    Receive a discrete chunk of data from node.
    As per FCP spec, the node dictates the size of the chunk.

    Arguments:
     - None
    Returns:
     - tuple - (chunk, len), where 'chunk' is a string of raw data
       or (None, None) if we got a restart
    """

    #set_trace()

    # now receive a series of data chunks
    resp = self._recvline()
    if resp == 'Restarted':
        # dammit
        self._recvbuf = ''
        self._recvbuflen = 0
        return None
        
    if resp != 'DataChunk':
        raise FreenetFcpError("Expected 'DataChunk', got '%s'" % resp)

    # get length field
    resp = self._recvline()
    fld, val = resp.split("=")
    if fld != 'Length':
        raise FreenetFcpError("Expected 'Length=', got '%s'" % resp)

    chunklen = int(val, 16)
    needed = chunklen
    chunk = ''

    # Get 'Data' line, or complain
    resp = self._recvline()
    if resp != 'Data':
        raise FreenetFcpError("Expected 'Data', got '%s'" % resp)

    # now we can loop around and pull the raw data
    while (needed &gt; 0):
        slice = self._recv(needed)
        chunk += slice
        needed -= len(slice)
    
    # Got the chunk
    return chunk, chunklen
</t>
<t tx="T32">def _genchk(self, rawdata, rawmeta=''):
    """
    Lower-level CHK generation method.
    Takes raw data and metadata strings, and sends back a URI object
    being the CHK that would be generated on inserting this data,metadata

    Arguments:
     - rawdata - raw data that would be inserted
     - rawmeta - accompanying raw metadata (default '')
    Returns:
     - a uri object, being the CHK key uri
    Exceptions:
     - FreenetFcpError - details in exception's 'value' attribute
    """

    metalen = len(rawmeta)
    datalen = len(rawdata) + metalen
    self._connect()
    self._sendline("GenerateCHK")
    self._sendline("DataLength=%x" % datalen)
    if metalen &gt; 0:
        self._sendline("MetadataLength=%x" % metalen)
    self._sendline("Data")
    if metalen &gt; 0:
        self._send(rawmeta)
    self._send(rawdata)
    #self._sendline("EndMessage") # not sure if this is needed

    # Get node response
    resp = self._recvline()
    if resp != 'Success':
        raise FreenetFcpError("_genchk: expected 'Success', got '%s'" % resp)
    resp = self._recvline()
    fld, val = resp.split("=", 1)
    if fld != 'URI':
        raise FreenetFcpError("_genchk: expected 'URI=', got '%s'" % resp)
    keyuri = uri(val)
    resp = self._recvline()
    if resp != 'EndMessage':
        raise FreenetFcpError("_genchk: expected EndMessage, got '%s'" % resp)

    # success
    return keyuri
</t>
<t tx="T33"></t>
<t tx="T34">def _fecput(self, keyuri, data, htl, **kw):
    keyuri = uri(keyuri)

    threaded = kw.get('threaded', 1)

    # stuff data into temporary file
    nam = tempFilename()
    fd = open(nam, "wb")
    fd.write(data)
    fd.close()

    k = self._fecputfile(keyuri, nam, htl, threaded=threaded)
    os.unlink(nam)
    return k

</t>
<t tx="T35">def _fecputfile(self, keyuri, filename, htl, **kw):
    
    keyuri = uri(keyuri)

    # stuff data into temporary file
    threaded = kw.get('threaded', 1)
    k = self._fecputfileex("CHK@", filename, htl, False, False, "CHK@", threaded)
    return k

</t>
<t tx="T36">def _fecputfileex(self, location, file, htl, remoteInsert, verifySite, oldUri, threaded=True):

    """
    fish's fec insert front-end - sorry about renaming :)
    """

    LOGMSG(3, "threaded=%s" % threaded)

    # does this even work on win32?
    # (yes)
    length = os.stat(file)[6]
    self._fec_threadData.usedData += length
    #print location, oldUri

    # the following code was mostly shamlessly stolen from the fantastic incredible GJ
    LOGMSG(3, "insertFileKey: Inserting FEC version 1.2 using FCP\nthreaded=%s" % threaded)
    segmentHeaders = self._fec_segmentFile('OnionFEC_a_1_2', length)
    #print segmentHeaders
    maps = []
    headers = []
    for header in segmentHeaders:
        # lock bitch
        self._fec_threadData.fecLock.acquire()

        headers.append(header)
        numChecks = int(header[1]['CheckBlockCount'], 16)
        numBlocks = int(header[1]['BlockCount'], 16)
        blocksRequired = int(header[1]['BlocksRequired'], 16)
        segments = int(header[1]['Segments'], 16)
        segmentNum = int(header[1]['SegmentNum'], 16)
        offset = long(header[1]['Offset'], 16)
        blockSize = int(header[1]['BlockSize'], 16)
        checkSize = int(header[1]['CheckBlockSize'], 16)

        # duh, we've alrady got this one
        # length = long(header[1]['FileLength'], 16)

        # I was going to just call GJ's code here, but then it occoured to me that it
        # relied on paging files, and it was just easier to copy it inline
        # here, modifying it as I go ^_^.
        # need to move this into a seperate function later!
        headerString = "SegmentHeader\n"
        headerString += self._fec_rebuildHdr(header[1])
        headerString += "EndMessage\n"
                
        # segments are always padded to this length, non?
        # GJ's code gets a bit esoteric here :)
        segLength = numBlocks*blockSize
        # read data
        s = open(file, "rb")
        s.seek(offset)
        data = s.read(segLength)
        # zero pad
        data = data+("\0"*(segLength-len(data)))
        s.close()

        # ask freenet to actully encode it
        # FIXME: this should definantly be in a differnet function ^_^
        LOGMSG(4, "insertFileKey: %s %s" % (location, oldUri))
        dataString = "\x00\x00\x00\x02"
        dataString += "FECEncodeSegment\n"
        dataString += "DataLength=%lx\n" % (len(headerString)+len(data))
        dataString += "MetadataLength=%lx\n" % len(headerString)
        dataString += "Data\n"
        dataString += headerString
        dataString += data
            
        s = self._fec_openPort()
        if s == None:
            LOGMSG(1, "insertFileKey: Couldn't connect to FCP - dying now!")
            return None

        self._fec_largeSend(s, dataString)

        # wait for confirmation
        # FIXME: rewrite all of this to use socets directly, rather than files
        fakefile = s.makefile("rb")
        msg = self._fec_readMsg(fakefile)

        if msg==None:
            LOGMSG(1, "insertFileKey: FEC encoding failed for %s %d" % (file, length))
            return None

        if msg[0] != 'BlocksEncoded':
            LOGMSG(1, "insertFileKey: no expected BlocksEncoded message - dying now! %s %d" \
                    % (file,length))
            return None
                
        # how this works is a tad esoteric, but it does makes sense.
        blockNum = 0
        count = 0
        blockData = ""
        blocks = []
 
        #set_trace()

        msg = self._fec_readMsg(fakefile)
        while msg != None:
            #print "_fecputfileex: msg='%s'" % str(msg)
            if msg[0]=="DataChunk":
                length = int(msg[1]['Length'], 16)
                while length &gt; 0:
                    boundry = (blockNum + 1) * checkSize
                    if count &lt; boundry:
                        # Read into the current block
                        nBytes = boundry - count
                        if nBytes &gt; length:
                            nBytes = length

                        time.sleep(0.2)
                        myData = fakefile.read(nBytes)
                        
                        #print "_fecputfileex: trying to read the %d bytes" % nBytes
                        #myChunks = []
                        #nwanted = nBytes
                        #while nwanted &gt; 0:
                        #    thistime = min(nwanted, 256)
                        #    print "still need %d bytes, reading %d" % (nwanted, thistime)
                        #    chnk = fakefile.read(thistime)
                        #    myChunks.append(chnk)
                        #    nwanted = nwanted - len(chnk)
                        #myData = string.join(myChunks, "")
                        #print "_fecputfileex: got the %d bytes" % nBytes
                        if len(myData) &lt; nBytes:
                            LOGMSG(1,
                                   "insertFileKey: Didn't read enough data! (%d)" \
                                     % len(myData))
                            return None
                        count += len(myData)
                        length -= len(myData)
                        blockData += myData
                    else:
                        blocks.append(blockData)    
                        blockData = ""
                        blockNum += 1
                msg = self._fec_readMsg(fakefile)
            else:
                LOGMSG(1, "insertFileKey: Recieved an unknown message! %s" % msg)
        fakefile.close()
        s.close()
        # append last block
        if len(blockData) &gt; 0:
            blocks.append(blockData)    
            blockData = ""
            blockNum += 1

        # okay, now insert the file
        # the rest is all copied from the old v1.0 splitfile insert code
        LOGMSG(3, "insertFileKey: Encoded %d redundant blocks @ %d kb per block" \
                % (len(blocks), checkSize/1024))

        # unlock bitch
        self._fec_threadData.fecLock.release()
        # no, no, no, no, no, no, no
        # no, no, no, no, no, no, no, no
        # no.  fuck no.  I am a fucking
        # moron.
        #self._fec_threadData.currentThreads = self._fec_threadData.currentThreads-1

        splitfileKeys = []
        splitfileLock = thread.allocate_lock()
        splitCheckKeys = []
        splitCheckLock = thread.allocate_lock()
            
        # clear the block thingys
        for i in range(numBlocks):
            splitfileKeys.append(None)
            splitCheckKeys.append(None)

        # insert the main blocks
        for i in range(numBlocks):
            blockdata = data[blockSize*i:blockSize*(i+1)]
            #print len(blockdata)
            splitPos = i
            while self._fec_threadData.currentThreads &gt;= self._fec_threadData.maxThreads:
                time.sleep(0.5)
            if threaded:
                thread.start_new_thread(self._fec_InsFcpSplitPart,
                                        (blockdata, i, splitPos, htl, numBlocks+numChecks,
                                         splitfileLock, splitfileKeys, remoteInsert,
                                         verifySite, oldUri)
                                        )
            else:
                self._fec_InsFcpSplitPart(blockdata, i, splitPos, htl, numBlocks+numChecks,
                                        splitfileLock, splitfileKeys, remoteInsert,
                                        verifySite, oldUri)
            time.sleep(0.25)                

        for i in range(numChecks):
            blockdata = blocks[i]
            splitPos = i + numBlocks
            while self._fec_threadData.currentThreads &gt;= self._fec_threadData.maxThreads:
                time.sleep(0.5)
            if threaded:
                thread.start_new_thread(self._fec_InsFcpSplitPart,
                                        (blockdata, i, splitPos, htl, numBlocks+numChecks,
                                         splitCheckLock, splitCheckKeys, remoteInsert,
                                         verifySite, oldUri)
                                        )
            else:
                self._fec_InsFcpSplitPart(blockdata, i, splitPos, htl, numBlocks+numChecks,
                                        splitCheckLock, splitCheckKeys, remoteInsert,
                                        verifySite, oldUri)
            time.sleep(0.25)                

        map = ("BlockMap", {})
        for i in range(numBlocks):
            while splitfileKeys[i] == None:
                time.sleep(0.5)
            key = "Block.%lx" % i
            map[1][key] = splitfileKeys[i]
        
        for i in range(numChecks):
            while splitCheckKeys[i] == None:
                time.sleep(0.5)
            key = "Check.%lx" % i
            map[1][key] = splitCheckKeys[i]
        #print map
        #print "done"
        maps.append(map)

    # back to blatent gj copy mode ^_^
    LOGMSG(4, "insertFileKey: Making splitfile metadata")

    #set_trace()

    meta = self._fec_makeMetadata(headers, maps, self._fec_getMimetype(file))

    key = self._fec_retryInsertFancy("", meta, location, htl,
                                "splitfile metadata for "+file,
                                oldUri, verifySite, remoteInsert)
    return key




</t>
<t tx="T37">def _fec_InsFcpSplitPart(self, blockdata, i, splitPos, htl, n, lock,
                       splitfileKeys, remoteInsert, verifySite, oldUri):

    mynode = node(self._host, self._port, htl)
    self._fec_threadData.currentThreads += 1

    mou = oldUri

    if mou != None:
        # generate the CHK for this key to verify, if we're doing a refresh
        #mou = self.generateCHK(blockdata, "")
        mou = str(mynode._genchk(blockdata, ''))

    try:
        keyuri = self._fec_retryInsert(blockdata, "", "CHK@", htl,
                                  ("Part %s of %s threads: %s" % \
                                   (str(splitPos+1),
                                    str(n),
                                    str(self._fec_threadData.currentThreads))),
                                  mou, verifySite, remoteInsert)
    except:
        traceback.print_exc()

    lock.acquire()
    splitfileKeys[i] = keyuri
    lock.release()
    self._fec_threadData.currentThreads -= 1</t>
<t tx="T38"># we almost always want to remote insert
#
# but we don't want to preverify if we already know ahead of time that the file isn't in freenet
def _fec_retryInsert(self, data, meta, location, htl, data2print,
                preverify=None, postverify=True, remoteinsert=True):

    n = node(self._host, self._port, htl)

    #print "preverify: ",location, preverify, data2print
    if(preverify != None):
        LOGMSG(3, "_fec_retryInsert: attempting to preverify %s at %s" \
                % (data2print, preverify))
        #d=retrieveKey(preverify, 15, true) # disabled DDM
        if n.keyexists(preverify, htl):
            LOGMSG(3, "_fec_retryInsert: retrieved %s without inserting - skipping..." % data2print)
            self._fec_threadData.skipped += 1
            return preverify

    keyuri = None
    retry = 0
    while keyuri==None:
        retry += 1
        LOGMSG(3, "_fec_retryInsert: Inserting %s at %s, try %s" \
                % (data2print, location, str(retry)))
        #traceback.print_stack()
        #keyuri = insertKey(data, meta, location, htl, remoteinsert)
        try:
            k = n.putraw(data, meta, location, htl)
            keyuri = str(k.uri)
        except:
            keyuri = None
        if postverify and keyuri != None:
            LOGMSG(4, "_fec_retryInsert: Verifying %s at %s", (data2print, keyuri))
            # we always want this to be remote
            # we're sticking to HTL=15 for retrieval right now, since this
            # is what fproxy defaults to - make it settable later, tho
            #d=retrieveKey(key, 15, true) # disabled DDM
            if n.keyexists(keyuri, htl):
                LOGMSG(3, "_fec_retryInsert: Verification succeeded!")
            else:
                LOGMSG(3, "_fec_retryInsert: Verification failed!")
                keyuri=None
            
        if keyuri == None:
            time.sleep(5)

    self._fec_threadData.inserted += 1
    return keyuri


</t>
<t tx="T39">def _fec_retryInsertFancy(self, data, meta, location, htl,
                     data2print, preverify=None, postverify=True, remoteinsert=True):
    needRedirect = True;
    if location[:3] == "CHK":
        needRedirect=False

    if data == None:
        data = ''
    if meta == None:
        meta = ''

    # not 32768, we're playing it safe :-p
    if len(data + meta) &lt; 32000:
        needRedirect = False
    if needRedirect == True:
        # insert the key
        keyuri = self._fec_retryInsert(data, meta, "CHK@", htl, data2print,
                                  None, postverify, remoteinsert)
        # create the redirect
        meta = self._fec_makeRedirect(keyuri)
        keyuri = self._fec_retryInsert("", meta, location, htl, data2print+" redirect",
                             preverify, postverify, remoteinsert)
    else:
        keyuri = self._fec_retryInsert(data, meta, location, htl, data2print,
                                  preverify, postverify, remoteinsert)
    return keyuri

</t>
<t tx="T40">def _fec_createManifest(self, sourceList, keyList):

    meta = self.metadataHeader

    # find index.html first
    for i in range(len(sourceList)):
        if (sourceList[i] == "index.html"):
            meta += "Document\n"
            meta += "Redirect.Target=%s\n" % keyList[i]
            meta += "EndPart\n"

    # and everything else
    for i in range(len(sourceList)):
        meta += "Document\n"
        meta += "Name=%s\n" % sourceList[i].replace("\\", "/")
        meta += "Redirect.Target=%s\n" % keyList[i]
        meta += "EndPart\n"
        # Change last EndPart to End - thanks to wookie :)

    if meta[-5:-1] == "Part":
        meta = meta[:-5] + "\n"
    return meta

</t>
<t tx="T41">class _fec_threadData:
    
    currentThreads = 0
    maxThreads = 4
    fcpHost = []
    fcpPort = []
    seperator = "/"
    inserted = 0
    skipped = 0
    verbose = False
    edition = -1
    activeLink = None
    firstFeedback = 0
    feedbackNumber = 20
    sitename = None
    usedData = 0
    maxData = 0
    lastFcp = 0
    fecLock = thread.allocate_lock()
</t>
<t tx="T42">def _fec_getMimetype(self, file):
    return {'html':'text/html', 'mp3':'audio/mpeg', 'ogg':'audio/ogg', 'mid':'audio/midi',
            'jpg':'image/jpeg', 'jpeg':'image/jpeg', 'gif':'image/gif', 'png':'image/png',
            'avi':'video/avi', 'asf':'video/asf', 'avi':'video/avi', 'mpg':'video/mpeg',
            'mpeg':'video/mpeg', 'sid':'audio/psid', 'zip':'binary/zip-compressed',
            'iso':'binary/cdimage',
            'gz':'binary/gzip-compressed'}.get(file.split('.')[-1], "text/plain")

</t>
<t tx="T43">def _fec_makeSimpleMetadata(self, mimetype):
    data = self.metadataHeader
    data += "Document\n"
    data += "Info.Format=%s\n" % mimetype
    data += "End\n"
    return data

</t>
<t tx="T44">def _fec_makeDbr(self, keyuri, period=86400):

    meta = self.metadataHeader
    meta += "Document\n"
    meta += "DateRedirect.Target=" + keyuri +"\n"
    meta += "DateRedirect.Increment=%lx\n" % period
    meta += "End\n"

    return meta
</t>
<t tx="T45">def _fec_makeRedirect(self, target):

    meta = self.metadataHeader
    meta += "Document\n"
    meta += "Redirect.Target=" + target + "\n"
    meta += "End\n"

    return meta
</t>
<t tx="T46">def _fec_rebuildHdr(self, header):

    out=""
    for field in header.keys():
        out += field + "=" + header[field] + "\n"

    return out
</t>
<t tx="T47"># this function copied almost verbatum from GJ, and then cleaned up
def _fec_makeMetadata(self, headers, maps, mimeType):

    n = node(self._host, self._port, self._htl)

    description="Onion FEC v1.2 file inserted by FishTools - ph33r d4 ph15h!"
    listString = ""

    for index in range(len(headers)):
        header = headers[index]
        listString += "SegmentHeader\n"
        listString += self._fec_rebuildHdr(header[1])
        listString += "EndMessage\n"

        map=maps[index]
        listString += "BlockMap\n"
        listString += self._fec_rebuildHdr(map[1])
        listString += "EndMessage"

    dataString = "\x00\x00\x00\x02"
    dataString += "FECMakeMetadata\n"
    dataString += "Segments=%lx\n" % len(headers)
    dataString += "Description=%s\n" % description
    if(mimeType):
        dataString += "MimeType=%s\n" % mimeType
    dataString += "DataLength=%lx\n" % len(listString)
    dataString += "Data\n"
    dataString += listString
    #print dataString
    s = n._fec_openPort()
    n._fec_largeSend(s, dataString)

    # the file hack from before returns
    fakefile = s.makefile("rb")
    msg = n._fec_readMsg(fakefile)
    LOGMSG(4, "_fec_makeMetadata: %s" % str(msg))
    if msg[0] != "MadeMetadata":
        LOGMSG(4, "_fec_makeMetadata: Unknown message: %s" % str(msg))
        return None

    tlen = int(msg[1]['DataLength'], 16)
    count = 0
    msg = n._fec_readMsg(fakefile)
    odata = ""
    while msg!=None:
        if msg[0] == "DataChunk":
            length = int(msg[1]["Length"], 16)
            time.sleep(0.2)
            myData = fakefile.read(length)
            if len(myData) &lt; length:
                LOGMSG(4, "_fec_makeMetadata failed to read enough data!")
                return None
            count += len(myData)
            if count &gt; tlen:
                break
            odata += myData
            msg = n._fec_readMsg(fakefile)
        else:
            LOGMSG(4, "_fec_makeMetadata: Bad message: %s" % str(msg))
            msg = n._fec_readMsg(fakefile)
            return None
    fakefile.close()
    s.close()
    return odata


</t>
<t tx="T48"># this one is almost a direct cut/paste from GJ - why reinvent the wheel :)
def _fec_segmentFile(self, algorythm, length):

    n = node(self._host, self._port, self._htl)

    # Build the message.
    dataString = "\x00\x00\x00\x02"
    dataString += "FECSegmentFile\n"
    dataString += "AlgoName=%s\n" % algorythm
    dataString += "FileLength=%lx\n" % length
    dataString += "EndMessage\n"

    print "_fec_segmentFile: algo=%s, length=%s" % (algorythm, length)

    # open the socket
    s = self._fec_openPort()
    if s is None:
        LOGMSG(1, "FECSegmentFile: Couldn't connect to FCP port")
        return None

    n._fec_largeSend(s, dataString)

    # Get response.
    file = s.makefile("rb")
    headers = []
    msg = n._fec_readMsg(file)
    while msg != None:
        if msg[0] != 'SegmentHeader':
            print "Received an unexpected msg!"
            print msg
            headers = []
            headers.append(msg)
            break

        headers.append(msg)
        msg = n._fec_readMsg(file)
    file.close()
    s.close()

    return headers

</t>
<t tx="T49"># send data in chunks of 1meg at a time
def _fec_largeSend(self, sock, data):

    sd=0
    while sd &lt; len(data):
        ed = sd + (1024 * 1024)
        if(ed &gt; len(data)): 
            ed = len(data)
        newdata = data[sd:ed]
        sock.send(newdata)
        sd = sd + (1024 * 1024)

</t>
<t tx="T50">def _fec_getNodeLoad(self, host, port):

    dataString = "\x00\x00\x00\x02"
    dataString += "ClientInfo\n"
    dataString += "EndMessage\n"
    s = self.openSpecificFcpPort(host, port)
    if s==None:
        return 100

    self._fec_largeSend(s, dataString)
    dataBack='fish'
    cbuf=''
    while len(dataBack) &gt; 0:
        dataBack = s.recv(1024)
        cbuf += dataBack
        # we have a complete message - process it...
        if cbuf[-11:] == "EndMessage\n":
            lines = cbuf.split("\n")
            for j in lines:
                fields = j.split('=')
                if fields[0] == "EstimatedLoad":
                    return int(fields[1], 16)
    return 100
</t>
<t tx="T51">def _fec_openPort(self, host=None, port=None):

    if host == None:
        host = self._host
    if port == None:
        port = self._port

    # open the socket
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mytuple = (host, int(port))
        if self._fec_threadData.verbose and len(self._fec_threadData.fcpHost) &gt; 1:
            LOGMSG(4, "openSpecificFcpPort: %s" % str(mytuple))
        s.connect(mytuple)
    except:
        s = None

    # write to it
    if s is None:
        LOGMSG(1, "openSpecificFcpPort: Couldn't connect to %s:%s" % (str(host), str(port)))
        return None
    return s
</t>
<t tx="T52">def _fec_readMsg(self, file):
    """
    Reads an FCP message off of an open file.
    returns a (Msg Name, Fields Dictionary) tuple
    or None, if no message could be read.
    """

    msgName = None     
    fields = {}

    time.sleep(0.2)
    buffer = file.readline()
    while buffer != '':
        #print "_fec_readMsg buffer: ", buffer
        if buffer.find('=') != -1:
            values = buffer.split('=')
            fields[values[0]] = values[1].strip()
        else:
            buffer = buffer.strip()
            if msgName == None:
                msgName = buffer.strip()
            elif buffer == 'EndMessage' or buffer == 'Data':
                # Stop at the end of the message.
                break

        buffer = file.readline()

    if msgName == None:
        return None

    return (msgName, fields)

</t>
<t tx="T53"># url can't be redirected.
# for now htl must be 0

def _fec_getFile(self, url, fileName, host, port, htl):

    DEVNULL_FILE = "null.dat"
    LOGMSG(3, "_fec_getFile: Requesting SplitFile %s" % url)

    #set_trace()

    ret = self._fec_clientGet(host, port, url, htl, None, '__FCP_temp_dl_meta.dat', 0, None, None)
    if ret[0] != 'Success':
        return 0
    
    LOGMSG(4, "Getting headers for SplitFile metadata.")

    pair = self._fec_segmentSplitFile(host, port, '__FCP_temp_dl_meta.dat')
    if pair == None:
        LOGMSG(2, "Couldn't segment SplitFile metadata.")
        return 0
        
    headers = pair[0]

    maps = pair[1]

    for index in range(len(headers)):
        header = headers[index]
        map = maps[index]
        
        nRequired = int(header[1]['BlocksRequired'], 16)
        nBlocks = int(header[1]['BlockCount'], 16)
        blockSize = int(header[1]['BlockSize'], 16)

        nChecks = int(header[1]['CheckBlockCount'], 16)
        fileLength = long(header[1]['FileLength'], 16)
        offset = int(header[1]['Offset'], 16)
        segment = int(header[1]['SegmentNum'], 16)
        segments = int(header[1]['Segments'], 16)
            
        
        # Randomly select required check and data blocks
        indices = self._fec_makeIndexList(nBlocks + nChecks, nRequired)

        dataIndices = []
        checkIndices = []

        for i in indices:
            if i &lt; nBlocks:
                dataIndices.append(i)
            else:
                checkIndices.append(i - nBlocks)

        LOGMSG(4, "Requesting data blocks...")

        for i in dataIndices:
            hexIndex =  "%lx" % i
            key = 'Block.' + hexIndex
            blockURL = map[1][key]
            blockFile = '__FCP_temp_data_block_' + str(i)
            ret = self._fec_clientGet(host, port, blockURL, htl,
                        blockFile, DEVNULL_FILE, 0, None, None)

            if ret == None:
                LOGMSG(3, "Couldn't download block: %d" % i)
                return 0
            if ret[0] != 'Success':
                LOGMSG(3, "Couldn't download block: %d" % i)
                return 0
            
            LOGMSG(4, "Downloaded block: %d" % i)

        for i in checkIndices:
            hexIndex =  "%lx" % i
            key = 'Check.' + hexIndex
            blockURL = map[1][key]
            blockFile = '__FCP_temp_check_block_' + str(i)
            ret = self._fec_clientGet(host, port, blockURL, htl,
                        blockFile, DEVNULL_FILE, 0, None, None)

            if ret == None:
                LOGMSG(3, "Couldn't download check block: %d" % i)
                return 0
            if ret[0] != 'Success':
                LOGMSG(3, "Couldn't download check block: %d" % i)
                return 0
            
            LOGMSG(4, "Downloaded check block: %d" % i)

        requestedIndices = self._fec_findMissingIndices(range(nBlocks), dataIndices)

        blockFiles = ( self._fec_makeFilenames(dataIndices, "__FCP_temp_data_block_") +
                   self._fec_makeFilenames(checkIndices, "__FCP_temp_check_block_") )
        
        reconFiles = self._fec_makeFilenames(requestedIndices, "__FCP_temp_recon_block_")
        
        LOGMSG(3, "FEC decoding...")
        self._fec_decodeSegment(host, port, header,
                     blockFiles,
                     dataIndices, checkIndices, requestedIndices,
                     reconFiles)
        

        LOGMSG(4, "data indices: %s" % dataIndices)
        LOGMSG(4, "requested Indices: %s" % requestedIndices)
        
        reconList = self._fec_makeRebuiltFileList(dataIndices, '__FCP_temp_data_block_',
                             requestedIndices, '__FCP_temp_recon_block_')
        
        LOGMSG(4, "block file list: ")
        LOGMSG(4, reconList)

        LOGMSG(4, "Concatinating blocks....")
        segLen = fileLength
        if segments &gt; 1:
            if segment &lt; segments - 1:
                segLen = nBlocks * blockSize
            else:
                # final segment
                segLen = fileLength - offset
        
        # Seeks and appends as nescessary.        
        self._fec_concatFiles(reconList, segLen, fileName, segment &gt; 0)

        self._fec_removeTmpFiles()

    return 1

</t>
<t tx="T54">def _fec_removeTmpFiles(self):

    filz = os.listdir(".")
    for file in filz:
        if len(file) &gt; 2:
            if file[0:11] == "__FCP_temp_":
                os.unlink(file)
                LOGMSG(4, "Removed temp file: %s" % file)
</t>
<t tx="T55"># returns A MetadataHint msg if bHint is true and the request succeeds
#     A Success msg if bHint is false and the request succeeds
#     A failure message otherwise.
def _fec_clientGet(self, server, port, uri, htl, dataFileName, metaDataFileName, bHint, hintTime, flags):
    # REDFLAG: remove debugging...
    #print "*** _fec_clientGet ***"
    #print "    server        : ", server
    # segv's printing the port.  wtf?
    #print "    port          : ", port
    #print "    uri            : ", uri
    #print "    htl            : ", htl
    #print "    dataFileName      : ", dataFileName
    #print "    metaDataFileName : ", metaDataFileName
    #print "    bHint         : ", bHint
    #print "    flags         : ", flags
    
    # Build the message.
    dataString=FCP_HEADER_BYTES+"ClientGet\n"+"URI="+uri+"\n"+"HopsToLive="+str(htl)+"\n"
    if bHint:
        dataString += "MetadataHint=true\n"
        if hintTime != None:
            dataString += "RedirectTimeSec=" + str(hintTime) + "\n"

    # To support local key deletion
    if flags != None:
        dataString += "Flags=" + ("%lx" % flags) +"\n"
        
    dataString += "EndMessage\n"

    # Open a socket
    s = self._fec_openSocket(server, port);
    if s is None:
        print "Couldn't connect to FCP port"
        raise IOError

    s.send(dataString)

    file = s.makefile("r")

    hintMsg = None
    errMsg = None
    
    # Total length
    tlen = -1
    # Data length
    dlen = -1
    # Metadata Length
    mlen = -1
    
    msg = self._fec_readMsg(file)

    if dataFileName != None:
        dataFile = open(dataFileName, 'wb')
    else:
        dataFile = None

    if metaDataFileName != None:
        metaFile = open(metaDataFileName, 'wb')
    else:
        metaFile = None
    
    # Total byte count
    count = 0
    
    while msg != None:
        #print "msg: " + msg[0]      
        if msg[0] == 'DataFound':
            tlen = int(msg[1]['DataLength'], 16)
            mlen = 0
            if msg[1].has_key('MetadataLength'):
                mlen = int(msg[1]['MetadataLength'], 16)
            dlen = tlen - mlen
        if msg[0] == 'DataChunk':
            length = int(msg[1]['Length'], 16)
            if count &lt; mlen:
                nBytes = length
                if count + nBytes &gt; mlen:
                    nBytes = mlen
                if metaFile != None:
                    nRead = self._fec_copyBinary(file, nBytes, metaFile)
                    if nRead != nBytes:
                        print "Didn't read enough bytes!"
                        print "nRead: ", nRead, " nBytes: ", nBytes
                        raise IOError

                count += nRead
                length -= nRead

            if count &gt;= mlen:
                nBytes = length
                if count + nBytes &gt; tlen:
                    nBytes = tlen - count

                if dataFile != None:
                    nRead = self._fec_copyBinary(file, nBytes, dataFile)
                    if nRead != nBytes:
                        print "Didn't read enough bytes!"
                        print "nRead: ", nRead, " nBytes: ", nBytes
                        raise IOError
                    count += nRead

        # Handle restarts
        if msg[0] == 'Restarted':
            if dataFile != None:
                dataFile.close()
            if metaFile != None:
                metaFile.close()
            count = 0
            
            dataFile = open(dataFileName, 'wb')
            if metaDataFileName != None:
                metaFile = open(metaDataFileName, 'wb')
            
        # Handle terminal messages
        if msg[0] == 'DataNotFound' or \
            msg[0] == 'RouteNotFound' or \
            msg[0] == 'URIError' or \
            msg[0] == 'FormatError' or \
            msg[0] == 'Failed':
            errMsg = msg
            break
        if msg[0] == 'MetadataHint':
            hintMsg = msg
            break
        
        msg = self._fec_readMsg(file)


    if dataFile != None:
        dataFile.close()
    if metaFile != None:
        metaFile.close()
    file.close()    
    s.close()

    if errMsg != None:
        return errMsg

    if hintMsg != None:
        return hintMsg
    
    return self._fec_makeFakeMsg('Success', 'Downloaded successfully.')

</t>
<t tx="T56"># returns the list of segment headers and block maps
# required to download a SplitFile on success
# returns None on failure
def _fec_segmentSplitFile(self, server, port, inputFileName):

    # Get length of the file containing the
    # SplitFile metadata.
    tlen = os.stat(inputFileName)[6]

    # Build the message.
    dataString=FCP_HEADER_BYTES
    dataString += "FECSegmentSplitFile\n"
    dataString += "DataLength=%lx\n" % tlen
    dataString += "Data\n"

    LOGMSG(4, "FECSegmentSplitFile:")
    LOGMSG(4, dataString)
    
    # open the socket
    s=self._fec_openSocket(server, port)
    if s is None:
        print "Couldn't connect to FCP port"
        raise IOError

    # REDFLAG: bush league, use file interface
    s.send(dataString)

    # Send the metadata.
    file = s.makefile("w");
    inputFile = open(inputFileName, "rb")
    self._fec_copyBinary(inputFile, tlen, file)
    inputFile.close()

    # Get response.
    file = s.makefile("r")

    # Hmmmm.... this is inconsistent
    # Should there be a "SegmentedSplitFile" msg?
    # NO, because messages come back as msgs not data
    
    msg = self._fec_readMsg(file)
    if msg[0] != 'SegmentHeader':
        print "Received an unexpected msg:", msg
        return None

    headers = []
    maps = []
    error = 0
    while msg != None:
        if msg[0] != 'SegmentHeader':
            print "Received an unexpected msg!"
            error = 1
            break
        
        headers.append(msg)

        msg = self._fec_readMsg(file)
        if msg[0] != 'BlockMap':
            print "Received an unexpected msg!"
            error = 1
            break;
        
        maps.append(msg)

        msg = self._fec_readMsg(file)
    
    file.close()
    s.close()

    if error:
        return None

    return (headers, maps)

</t>
<t tx="T57"># returns 1 on success 0 otherwise
def _fec_decodeSegment(self, server, port, header,
             blockFileNames,
             blockIndices, checkIndices, requestedIndices,
             outputFileNames):


    # REDFLAG: check arguments?
    
    blockCount = int(header[1]['BlockCount'], 16)
    blockSize = int(header[1]['BlockSize'], 16)
    checkBlockCount = int(header[1]['CheckBlockCount'], 16)
    checkBlockSize = int(header[1]['CheckBlockSize'], 16)
    offset = long(header[1]['Offset'], 16)


    #REDFLAG: make client do this themself?
    tmp = []
    for i in checkIndices:
        tmp.append(i + blockCount)

    checkIndices = tmp

    dlen = blockSize * len(blockIndices) + checkBlockSize * len(checkIndices)

    # Reconstruct the SegmentHeader msg
    # so that we can send it in the metadata
    headerString="SegmentHeader\n"
    for field in header[1].keys():
        headerString=headerString+ field+ "=" + header[1][field] + "\n"
    headerString=headerString+"EndMessage\n" 

    mlen = len(headerString)
    tlen = dlen + mlen
    
    # Build the message.
    dataString=FCP_HEADER_BYTES
    dataString += "FECDecodeSegment\n"
    dataString += "DataLength=%lx\n" % tlen
    dataString += "MetadataLength=%lx\n" % mlen
    dataString += "BlockList=%s\n" % self._fec_hexIndexList(blockIndices)
    dataString += "CheckList=%s\n" % self._fec_hexIndexList(checkIndices)
    dataString += "RequestedList=%s\n" % self._fec_hexIndexList(requestedIndices)
    dataString += "Data\n"

    #print "FECDecodeSegment:"
    #print dataString

    #print "SegmentHeader (sent via metadata):"
    #print headerString

    # open the socket
    s=self._fec_openSocket(server, port)
    if s is None:
        print "Couldn't connect to FCP port"
        raise IOError

    file = s.makefile("w")

    # Send the FCP decode request.
    file.write(dataString)

    # Send SegmentHeader in metadata.
    file.write(headerString)

    dataSent = 0;
    
    # Send blocks
    index = 0
    for name in blockFileNames:
        fileSize = blockSize
        if index &gt; len(blockIndices):
            fileSize = checkBlockSize
            
        assert os.stat(name)[6] == fileSize
        
        inputFile = open(name, "rb")
        self._fec_copyBinary(inputFile, fileSize, file)
        inputFile.close()

        dataSent += fileSize
        index = index + 1

    file.flush()
    file.close()

    # Get the confirmation
    file = s.makefile("r")
    msg = self._fec_readMsg(file)

    if msg[0] != 'BlocksDecoded':
        print "Received an unexpected msg:", msg
        return 0

    # grrrrrrr.... C&amp;P, factor this out.

    # Read decoded data blocks off the socket.
    blockNum = 0
    currentFile = open(outputFileNames[blockNum], "wb")
    count = 0
    msg = self._fec_readMsg(file)
    while msg != None:
        #print "msg: " + msg[0]     
        if msg[0] == 'DataChunk':
            length = int(msg[1]['Length'], 16)
            while length &gt; 0:
                boundry = (blockNum + 1) * blockSize
                if count &lt; boundry:
                    # Read into the current block
                    nBytes = boundry - count
                    if nBytes &gt; length:
                        nBytes = length
                    nRead = self._fec_copyBinary(file, nBytes, currentFile)
                    if nRead != nBytes:
                        print "Didn't read enough bytes!"
                        print "nRead: ", nRead, " nBytes: ", nBytes
                        raise IOError
                    count += nRead
                    length -= nRead
                else:
                    # Advance to the next block    
                    currentFile.close()
                    blockNum = blockNum + 1
                    currentFile = open(outputFileNames[blockNum], "wb")
            msg = self._fec_readMsg(file)
        else:
            print "Received an unexpected msg:", msg
            return 0
    

    currentFile.close()

    file.close()
    s.close()

    return 1

</t>
<t tx="T58">############################################################
# Automatic insertion and retrieval functions built
# on top of the FCP primatives.
############################################################

############################################################
# Downloads a key from Freenet automatically handling
# redirects.
#
# returns a (success, mimeType, redirectList) tuple
#
# If success is 0, the last entry in the redirectList is the uri that
# couldn't be retrieved.
def _fec_getKey(self, server, port, uri, htl, dataFileName, metaDataFileName, hintTime, flags):
    uris = []
    mimeType = None

    msg = self._fec_clientGet(server, port, uri, htl, dataFileName, metaDataFileName, 1, hintTime, flags)
    uris.append(uri)
    while msg != None:
        #print "uri: ", uri
        #print "msg: ", msg
        if msg[0] == 'MetadataHint':
            if mimeType == None and msg[1].has_key('MimeType'):
                # We take the first mime type definition
                # in the redirect chain
                mimeType = msg[1]['MimeType']

            kind = int(msg[1]['Kind'])
            # ok to leave as a hex string.
            hintTime = msg[1]['TimeSec']

            # Handle metadata using the hint sent
            # by the FCP server. Cool huh.
            #
            if kind == MDH_DATA:
                # Our work is done.
                return (1, mimeType, uris)
                break
            elif kind == MDH_REDIRECT:
                uri = msg[1]['NextURI']
                uris.append(uri)
                msg = self._fec_clientGet(server, port, uri, htl,
                            dataFileName, metaDataFileName, 1, hintTime, flags)
            elif kind == MDH_DATEREDIRECT:
                uri = msg[1]['NextURI']
                # Append increment and offset and evaluation time to dbrs
                uris.append(uri + " [" + msg[1]['Increment'] +
                        ", " + msg[1]['Offset'] + ", " + hintTime + "]" )

                msg = self._fec_clientGet(server, port, uri, htl,
                            dataFileName, metaDataFileName, 1, hintTime, flags)
            elif kind == MDH_SPLITFILE:
                print "Can't handle splitfiles yet!"
                break
            elif kind == MDH_TOODUMB:
                print "FCP server too dumb to parse the metadata!"
                break
            elif kind == MDH_ERROR:
                print "FCP server enountered and error parsing metadata!"
                break
            else:
                print "Phreaked out. UNKNOWN kind constant: " + str(kind)
                break
        else:
            break

    return (0, mimeType, uris)

</t>
<t tx="T59">def _fec_hexIndexList(self, indices):
    return ",".join([("%lx" % n) for n in indices])

</t>
<t tx="T60"># Opens a socket for an FCP connection.
def _fec_openSocket(self, server, port):
    # REDFLAG: Work around for segv
    # grrrrr.....
    # There is something badly fuXORd with my rh7.1 python2.2
    # install.  People with python properly configured
    # shouldn't have to resort to this.
    portAsString = str(port)
    copyAtNewAddress = int(portAsString)

    #print "_fec_openSocket: server=%s, port=%s" % (server, port)

    # open the socket
    s=None
    for res in socket.getaddrinfo(server, copyAtNewAddress, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error, msg:
            s = None
            continue
        try:
            s.connect(sa)
        except socket.error, msg:
            s.close()
            s = None
            continue
        break

    return s

</t>
<t tx="T61">def _fec_makeFakeMsg(self, msgName, reason):
    fields = {}
    fields['Reason'] = reason
    return (msgName, fields)

</t>
<t tx="T62"># Copy data from a file open for input
# to a file open for output.
#
# Note: This function doesn't close or
#       flush the files.
#
def _fec_copyBinary(self, file, length, outputFile):
    #print "_fec_copyBinary: length=", length 
    requested = length
    count = 0
    while length &gt; 0:
        #print "_fec_copyBinary: ",  count
        nBytes = 16384
        if nBytes &gt; length:
            nBytes = length

        buffer = file.read(nBytes)
        if buffer == '':
            break

        outputFile.write(buffer)
        nWritten = len(buffer)
        count += nWritten
        length -= nWritten
        #if nWritten != nBytes:
        #    break

    if requested != count:
        print "_fec_copyBinary -- only wrote ", count, " of " , requested
        raise IOError

    return count
</t>
<t tx="T63">#Output file must be open for writing
def _fec_zeroPad(self, outputFile, length):
    # REDFLAG: hoist out and re-use same buffer?
    # Is this a speed issue?
    buffer = "\x00" * 16384

    while length &gt; 0:
        nBytes = 16384
        if nBytes &gt; length:
            nBytes = length
            buffer = "\x00" * nBytes

        outputFile.write(buffer)
        length -= nBytes
</t>
<t tx="T64">def _fec_sameLength(self, fileNameA, fileNameB):
    if os.stat(fileNameA)[6] == os.stat(fileNameB)[6]:
        return 1
    return 0
</t>
<t tx="T65">def _fec_diffBinary(self, fileNameA, fileNameB):
    fileA = open(fileNameA, "rb")
    fileB = open(fileNameB, "rb")
    if not self._fec_sameLength(fileNameA, fileNameB):
        print "_fec_diffBinary: lengths don't match! ", fileNameA, " ", fileNameB
        return 0

    length = os.stat(fileNameA)[6]
    count = 0

    nBuf = length / 4096
    if length % 4096 != 0:
        nBuf = nBuf + 1

    for i in range(nBuf):
        bufferA = fileA.read(4096)
        bufferB = fileB.read(4096)

        nReadA = len(bufferA)
        nReadB = len(bufferB)

        if nReadA != nReadB:
            # REDFLAG: underwhelming
            print "My pitiful code choked! Sorry :-("
            assert 0

        for j in range(nReadA):
            if bufferA[j] != bufferB[j]:
                print "Mismatch at byte: " , count
                return 0
            count = count + 1


    assert count == length

    return 1
</t>
<t tx="T66">def _fec_concatFiles(self, inputFileNames, length, outputFileName, append):
    #print "_fec_concatFiles: length=" , length
    if append:
        outputFile = open(outputFileName, "ab")
    else:
        outputFile = open(outputFileName, "wb")

    index = 0
    flen = os.stat(inputFileNames[index])[6]
    inputFile = open(inputFileNames[index], "rb")
    while length &gt; 0:
        # print "index: " , index, "length: ", length
        if flen == 0:
            inputFile.close()
            index = index + 1
            flen = os.stat(inputFileNames[index])[6]
            inputFile = open(inputFileNames[index], "rb")
        nBytes = length
        if nBytes &gt; flen:
            nBytes = flen
        self._fec_copyBinary(inputFile, nBytes, outputFile)
        length -= nBytes
        flen -= nBytes
        outputFile.flush()
        # print " outputFile length=", os.stat(outputFileName)[6]

    inputFile.close()
    outputFile.close()
</t>
<t tx="T67">def _fec_makeFilenames(self, indices, prefix):
    ret = []
    for i in indices:
        ret.append(prefix + str(i))

    return ret
</t>
<t tx="T68">def _fec_makeIndexList(self, max, number):
    if number &gt; max:
        print "Bad arguments number&gt; max"
        assert 0

    list = range(max)
    ret = []
    while len(ret) &lt; number:
        element = random.choice(list)
        ret.append(element);
        list.remove(element)
    ret.sort()
    return ret
</t>
<t tx="T69"># makes an ordered list of data block / renonstructed
# block file names
def _fec_makeRebuiltFileList(self, dataIndices, data_prefix, reconstructedIndices, recon_prefix):
    dataMap = {}
    for index in dataIndices:
        dataMap[index] = 'extant'

    reconMap = {}
    for index in reconstructedIndices:
        reconMap[index] = 'extant'

    ret = []
    for index in range(len(dataIndices) + len(reconstructedIndices)):
        if dataMap.has_key(index):
            ret.append(data_prefix + str(index))
        elif reconMap.has_key(index):
            ret.append(recon_prefix + str(index))
        else:
            print "failed, block missing: " , index 
            assert 0
    return ret
</t>
<t tx="T70">def _fec_findMissingIndices(self, full_range, partial_range):
    list = {}
    for i in partial_range:
        list[i] = "extant"

    ret = []
    for i in full_range:
        if not list.has_key(i):
            ret.append(i)

    ret.sort()
    return ret
</t>
<t tx="T71">class site:
    """
    Class for creation, insertion and retrieval of freesites

    1001 uses, including:
     - creating new freesites from scratch
     - downloading existing freesites from freenet
     - inserting new freesites into freenet
     - refreshing existing freesites owned by client
    """
    @others
</t>
<t tx="T72">def __init__(self, **args):
    """
    Constructor for class freenet.site

    Arguments:
     - none

    Keywords:
     - siteType - style of freesite - 'dbr', 'edition' or 'oneshot', default to last
       saved site state, or 'dbr' if no previous site state
     - edition - if siteType is 'edition', specifies the edition number from which
       to start insert attempts - defaults to last saved site state, or 0 if no prev saved state
     - editionMaxTries - maximum number of edition numbers to try - failure results if we
       exhaust all tries - default is last saved site state, or 0 (try forever) if no prev saved state

     - name      - text name of site, must be [A-Za-z0-9_\-\/]+, compulsory
       used in key URI, as in SSK@blahblahPAgM/name//
     - fromdir   - directory to insert from, compulsory if inserting
     - todir     - directory to retrieve to, defaults to unique dir in /tmp
     - htl       - htl for insert/retrieve, default 20
     - pub       - SSK public key, compulsory if refreshing
     - priv      - SSK private key, compulsory if refreshing
     - future    - days in future to insert, default 0
     - default   - file in fromdir to use as default, default='index.html'
     - splitsize - size of splitfile segments
     - map       - metadata map object
     - offset    - offset for DBR, default 0
     - increment - DBR interval in seconds, default 86400 (1 day)
     - retries   - number of retry attempts, default 3
     - allowSplitfiles - allows large files to get split up, default 1 (true)
     - host      - FCP host to use
     - port      - FCP port to use
     - maxthreads - maximum number of insert threads
    """

    self.map = metadata()

    # validation - only accept certain keywords, of certain type
    argmap = {'name':str, 'fromdir':str, 'todir':str, 'htl':int,
              'pub':str, 'priv':str, 'default':str,
              'splitsize':int, 'map':metadata,
              'offset':int, 'increment':int, 'retries':int, 'allowSplitfiles':int,
              'host':str, 'port':int, 'future':int,
              'siteType':str, 'edition':int, 'editionMaxTries':int, 'maxthreads':int,
              }
    self.args = self.chkArgs(argmap, **args)

    if not args.has_key('retries'):
        self.retries = 3
</t>
<t tx="T73">def chkArgs(self, argmap, **args):
    """
    Retrieve arguments from args, validate names and types
    """
    goodargs = {}
    for arg in args.keys():
        val = args[arg]
        if not argmap.has_key(arg):
            raise FreenetFreesiteBadArgument(
                "Illegal keyword: '%s'" % arg)
        typ = argmap[arg]
        if typ == str:
            typ = (str, MutableString)
        if not isinstance(val, typ):
            raise FreenetFreesiteBadArgument(
                "'%s' should be type '%s'" % (arg, repr(typ)))
        goodargs[arg] = val
    return goodargs
</t>
<t tx="T74">def put(self, fromdir=None, **args):
    """
    Insert this site object into freenet as a complete freesite
    Arguments:
     - fromdir - directory to insert form. If not given, attempts to
       take this from instance variables
    Keywords:
     - host - FCP host to use, defaults to constructor arg
     - port - FCP port to use - defaults to constructor arg

     - siteType - style of freesite - 'dbr', 'edition' or 'oneshot', defaults to constructor
       argument (see __init__)
     - edition - if siteType is 'edition', specifies the edition number from which
       to start insert attempts. defaults to constructor arg (see __init__)
     - editionMaxTries - maximum number of edition numbers to try - failure results if we
       exhaust all tries - defaults to contstructor arg (see __init__)

     - name (optional, defaults to 'site'
       called, otherwise taken from instance var
     - htl - optional, default 20
     - pub - ssk public key
     - priv - ssk private key
     - future - optional, default 0
     - default - file to use as site default, default 'index.html'
     - splitsize - size of splitfile chunks, default 262144
     - offset - dbr offset in seconds, default 0
     - increment - dbr increment in seconds, default 86400
     - maxthreads - default 8, maximum number of parallel insert threads
     - allowSplitfiles - default 1, allow large files to be split
     - files - dict of files to insert into the freesite. The keys of the dict are
       relative paths (as they appear, for example:
         - the 'path/to/file.txt' in 'SSK@BblahblahPAgM/fred//path/to/file.txt'.
       The value is a dict containing the keys:
         - mimetype - a standard mimetype string, AND one of:
             - raw - a raw string comprising the file's content, OR
             - fullpath - an absolute path on the host filesystem
       Example::

         { 'index.html' ;     {'mimetype' : 'text/html',
                               'raw' : '&lt;html&gt;&lt;body&gt;Here is index.html&lt;/body&gt;&lt;/html&gt;'
                               },
           '/fred/mary.txt' : {'mimetype' : 'text/plain',
                               'raw' : 'This is fred/mary.txt'
                               },
           }

    Returns:
     - a uri object for the inserted site

    After any insertion attempt, the pub/priv keypair, htl, splitsize, offset
    and increment get stored in a pickle in file /.freesiterc in the site's
    directory - but only if the caller did not pass a fileset
    """

    dontsave = False

    # create temporary instance if needed
    #if not isinstance(self, site):
    #    inst = site()
    #    return inst.put(fromdir, **args)

    LOGMSG(4, "site.put: entered")

    if args.has_key('files'):
        files = args['files']
        lastconf = {}
        dontsave = True
    else:
        # determine source directory
        if fromdir == None:
            fromdir = self.args.get('fromdir')
        if fromdir == None:
            raise FreenetFreesiteBadDir('')
        LOGMSG(3, "site.put: fromdir='%s'" % fromdir)
    
        # Read the 'fromdir' directory
        try:
            files = self.readdir(fromdir)
        except OSError:
            raise FreenetFreesiteBadDir(fromdir)
        if len(files) == 0:
            raise FreenetFreesiteBadDir(fromdir)
    
        # Try to uplift configuration from freesite dir as '.freesiterc'
        #print "Trying to uplift config from %s" % self.fromdir
        conffile = "%s/.freesiterc" % fromdir
        try:
            # pick up keys from pickled file
            fd = open(conffile)
            lastconf = pickle.load(fd)
            fd.close
            LOGMSG(3, "site.put: got configs from site dir")
        except:
            lastconf = {}
            LOGMSG(3, "site.put: inserting site for the first time")

    # general args
    host = args.get('host', self.args.get('host', defaultHost))
    port = args.get('port', self.args.get('port', defaultPort))
    name = lastconf.get('name', args.get('name', self.args.get('name', 'site')))
    pub = args.get('pub', self.args.get('pub', lastconf.get('pub', None)))
    priv = args.get('priv', self.args.get('priv', lastconf.get('priv', None)))
    default = args.get('default', lastconf.get('default', self.args.get('default', 'index.html')))
    splitsize = args.get('splitsize', lastconf.get('splitsize', self.args.get('splitsize', 262144)))
    htl = args.get('htl', self.args.get('htl', lastconf.get('htl', 20)))
    allowSplitfiles = args.get('allowSplitfiles', self.args.get('allowSplitfiles', defaultAllowSplitfiles))

    maxthreads = args.get('maxthreads', self.args.get('maxthreads', defaultMaxSiteThreads))

    # site-type-specific args
    siteType = args.get('siteType', lastconf.get('siteType', self.args.get('siteType', 'dbr')))
    edition = args.get('edition', lastconf.get('edition', self.args.get('edition', 0)))
    editionMaxTries = args.get('editionMaxTries', lastconf.get('editionMaxTries', self.args.get('editionMaxTries', 0)))
    offset = lastconf.get('offset', args.get('offset', self.args.get('offset', 0)))
    increment = lastconf.get('increment', args.get('increment', self.args.get('increment', 86400)))
    future = args.get('future', self.args.get('future', 0))

    # take action for different site types
    if siteType == 'oneshot':
        manifestPubUri = uri("SSK@%sPAgM/%s" % (pub, name))
        manifestPrivUri = uri("SSK@%s/%s" % (priv, name), sskpriv=True)
        pass

    elif siteType == 'edition':
        pass

    elif siteType == 'dbr':
        dbrPrefix = dbr(future, increment, offset)
        manifestPubUri = uri("SSK@%sPAgM/%s-%s" % (pub, dbrPrefix, name))
        manifestPrivUri = uri("SSK@%s/%s-%s" % (priv, dbrPrefix, name), sskpriv=True)

        LOGMSG(3, "manifestPrivUri=%s" % manifestPrivUri)
        LOGMSG(3, "manifestPubUri=%s" % manifestPubUri)
        LOGMSG(3, "offset=%s" % offset)
        LOGMSG(3, "increment=%s" % increment)
        LOGMSG(3, "future=%d" % future)
        LOGMSG(3, "dbr-prefix=%s" % dbrPrefix)

    # grab a temporary FCP interface object
    mynode = node(host, port, htl, allowSplitfiles=allowSplitfiles)

    gotprevkeys=False # means we need to write keys
    # make up some keys, if needed
    if (pub == None) ^ (priv == None):
        raise FreenetFreesiteBadKeys(pub, priv)

    # Create new keypair if we don't have one
    if pub == None:
        (pub, priv) = mynode.genkeypair()
        LOGMSG(3, "site.put: created new keys pub=%s, priv=%s" % (pub, priv))

    # determine key URIs
    puburi = uri("SSK@%sPAgM/%s" % (pub, name))
    privuri = uri("SSK@%s/%s" % (priv, name), sskpriv=True)

    LOGMSG(3, "puburi=%s" % puburi)
    LOGMSG(3, "privuri=%s" % privuri)
    LOGMSG(3, "name=%s" % name)
    LOGMSG(3, "pubkey=%s" % pub)
    LOGMSG(3, "privkey=%s" % priv)
    LOGMSG(3, "default=%s" % default)
    LOGMSG(3, "splitsize=%d" % splitsize)
    LOGMSG(3, "htl=%d" % htl)

    # ----------------------
    # Insert all the files
    # ----------------------
    
    # function to be run in dispatcher threads, to insert each file
    def inserter(dispObj, f):
        files = dispObj.files
        LOGMSG(4, "site.put: Inserting file %s, %d threads running" % (f, dispObj._numrunning))
        if files[f].has_key('fullpath'):
            fd = open(files[f]['fullpath'])
            fdat = fd.read()
            fd.close()
        elif files[f].has_key('raw'):
            fdat = files[f]['raw']
        else:
            raise FreenetFreesiteBadArgument("relative path '%s' has neither file nor raw content" % f)
        metaFile = metadata()
        metaFile.add('', mimetype=files[f]['mimetype'])
        #if allowSplitfiles:
        #    raise Exception
        mynode = node(dispObj.host, dispObj.port, dispObj.htl, allowSplitfiles=dispObj.allowSplitfiles)

        curbackoff = 3
        expbackoff = 1.25
        while 1:
            try:
                insertedkey = mynode.put(fdat,
                                         metaFile,
                                         "CHK@",
                                         htl=dispObj.htl,
                                         allowSplitfiles=dispObj.allowSplitfiles)
                files[f]['uri'] = insertedkey.uri
                LOGMSG(3, "site.put: File %s inserted as %s, %d threads running" % (
                                f, files[f]['uri'], dispObj._numrunning))
                break
            except FreenetRouteNotFound:
                LOGMSG(2, "site.put: got RNF inserting file %s\nbacking off for %s secs" % (
                               f, curbackoff))
                time.sleep(curbackoff)
                curbackoff = curbackoff * expbackoff

    # create a dispatcher object and feed in common attributes
    dispObj = Dispatcher(inserter, maxthreads)
    dispObj.files = files
    dispObj.host = host
    dispObj.port = port
    dispObj.htl = htl
    dispObj.allowSplitfiles = allowSplitfiles

    # load dispatcher with insert jobs
    for f in files.keys():
        dispObj.add(f)

    # launch insert dispatcher
    LOGMSG(3, "site.put: Launching dispatcher for file inserts")
    dispObj.start()
    
    # wait for dispatcher to finish
    LOGMSG(3, "site.put: Waiting for dispatcher to complete")
    dispObj.wait()
    LOGMSG(3, "site.put: Dispatcher has finished")

    if 0: # old insert loop - one at a time - yikes
        for f in files.keys():
            LOGMSG(4, "site.put: Inserting file %s" % f)
            if files[f].has_key('fullpath'):
                fd = open(files[f]['fullpath'])
                fdat = fd.read()
                fd.close()
            elif files[f].has_key('raw'):
                fdat = files[f]['raw']
            else:
                raise FreenetFreesiteBadArgument("relative path '%s' has neither file nor raw content" % f)
            metaFile = metadata()
            metaFile.add('', mimetype=files[f]['mimetype'])
            #if allowSplitfiles:
            #    raise Exception
            insertedkey = mynode.put(fdat, metaFile, "CHK@", htl=htl, allowSplitfiles=allowSplitfiles)
            files[f]['uri'] = insertedkey.uri
            LOGMSG(3, "site.put: File %s inserted as %s" % (f, files[f]['uri']))

    # Construct metadata for site manifest
    manifest = metadata()
    for f in files.keys():
        manifest.add(f, "Redirect", target=files[f]['uri'])
    # Don't forget our default file!
    manifest.add("", "Redirect",
                 target=files[default]['uri'],
                 mimetype=guessMimetype(default))

    # insert the manifest at a URI according to the site type (dbr/edition/oneshot)
    if siteType == 'dbr':
        # Create and Insert DBR main pointer key
        metaDbr = metadata()
        metaDbr.add('', 'DateRedirect',
                    target=puburi,
                    increment=increment,
                    offset=offset)
        #print metaDbr
        LOGMSG(4, "site.put: about to insert dbr")
        mynode.put('', metaDbr, privuri, htl=htl, allowSplitfiles=0)
        LOGMSG(3, "site.put: dbr inserted")
    
        # Now insert the manifest du jour as the dbr target
        LOGMSG(4, "site.put: inserting manifest to %s\n%s" % (manifestPrivUri, manifest))
        keyNow = mynode.put('', manifest, manifestPrivUri, htl=htl, allowSplitfiles=allowSplitfiles)

    elif siteType == 'oneshot':
        # just insert the manifest at the main URI
        LOGMSG(4, "site.put: inserting one-shot manifest at %s" % privuri)
        keyNow = mynode.put('', manifest, privuri, htl=htl, allowSplitfiles=allowSplitfiles)
    
    elif siteType == 'edition':
        # not quite so trivial - keep trying to insert until we stop getting key collisions
        LOGMSG(4, "site.put: attempting manifest inserts, starting at %s/%d" % (privuri, edition))
        curEd = edition
        if editionMaxTries != 0:
            maxEd = edition + editionMaxTries
        else:
            maxEd = 1000000000
        
        while curEd &lt; maxEd:
            manifestPrivUri = privuri + "/%d" % curEd
            manifestPubUri = puburi + "/%d" % curEd
            try:
                keyNow = mynode.put('', manifest, manifestPrivUri, htl=htl, allowSplitfiles=allowSplitfiles)
                edition = curEd
                keyNow.edition = edition
                break
            except FreenetKeyCollision:
                curEd = curEd + 1
                continue
        if curEd == maxEd:
            raise FreenetEditionsExhausted("failed to insert edition freesite %s/n" % puburi)

    LOGMSG(3, "site.put: manifest inserted successfully")

    #set_trace()

    # Write out the keypair to the freesite dir if needed
    if not dontsave and not gotprevkeys:
        try:
            #print "Trying to write out keypair to %s/.sskkeys" % fromdir
            #set_trace()
            conf = {'name':name,
                    'pub':pub,
                    'priv':priv,
                    'default':default,
                    'htl':htl,
                    'offset':offset,
                    'increment':increment,
                    'splitsize':splitsize,
                    'allowSplitfiles':allowSplitfiles,
                    'siteType':siteType,
                    'edition':edition,
                    'editionMaxTries':editionMaxTries,
                    }
            fd = open(conffile, "w")
            pickle.dump(conf, fd)
            fd.close()
            LOGMSG(4, "site.put: saved settings")
        except:
            # directory must be write-protected - author's fault!
            LOGMSG(2, "site.put: failed to save site settings")
            pass

    # well, i'll be darned - might be done now!
    #print manifest
    LOGMSG(4, "puburi         = %s" % puburi)
    LOGMSG(4, "privuri        = %s" % privuri)
    LOGMSG(4, "manifestPubUri = %s" % manifestPubUri)
    LOGMSG(4, "manifestPrivUri = %s" % manifestPrivUri)
    LOGMSG(4, "keyNow         = %s" % keyNow)

    self.uri = puburi
    #return puburi
    return keyNow</t>
<t tx="T75">def get(self, siteuri=None, todir=None, docname=None, **args):
    """
    Retrieves a freesite, lock, stock'n'barrel.

    Arguments (not required if instance vars present):
     - siteuri - full URI of site to retrieve
     - todir - directory to store the retrieved site
       Note - this direcctory must already exist.
    Keywords:
     - past - number of time intervals (default 0) to regress
       when retrieving the site. Note that most DBR sites work
       at offset 0, increment 86400 (1 day)
     - htl - hops to live - how deeply to delve within the Freenet
       for retrieving this site
     - docname - only used during recursive calls - ignore this
     - host - FCP host to use, defaults to constructor arg
     - port - FCP port to use - defaults to constructor arg
    Returns:
     - True if retrieval succeeded, False if failed
    Note:
     - Site's files will be written *into* directory 'todir'
       So if you're fetching 'SSK@blahblah/somesite', you should
       perhaps create a directory called 'somesite' somewhere first.
    """

    # Create temporary instance if called statically
    #if not isinstance(self, site):
    #    inst = site()
    #    inst.get(siteuri, todir, **args)
    #    return inst

    LOGMSG(4, "site.retrieve: entered")

    self.failures = 0
    #set_trace()
    self.__get(siteuri, todir, **args)
    LOGMSG(3, "retrieve completed with %d failures" % self.failures)
    self.failures = 0
    self.uri = siteuri

</t>
<t tx="T76">def readdir(self, dirpath, prefix=''):
    """
    Reads a directory, returning a sequence of file dicts.
    Arguments:
      - dirpath - relative or absolute pathname of directory to scan
      
    Each returned dict in the sequence has the keys:
      - fullpath - usable for opening/reading file
      - relpath - relative path of file (the part after 'dirpath'),
        for the 'SSK@blahblah//relpath' URI
      - mimetype - guestimated mimetype for file
    """

    #set_trace()
    #print "dirpath=%s, prefix='%s'" % (dirpath, prefix)
    entries = {}
    for f in os.listdir(dirpath):
        relpath = prefix + f
        fullpath = dirpath + "/" + f
        if f == '.freesiterc':
            continue
        if os.path.isdir(fullpath):
            entries.update(self.readdir(dirpath+"/"+f, relpath + "/"))
        else:
            #entries[relpath] = {'mimetype':'blah/shit', 'fullpath':dirpath+"/"+relpath}
            entries[relpath] = { 'fullpath':dirpath+"/"+f,
                                 'mimetype':guessMimetype(f)
                                 }
    return entries

</t>
<t tx="T77">def __get(self, siteuri=None, todir=None, parentdoc=None, **args):
    """
    Private recursive method for site.get - do not call this method
    """
    
    LOGMSG(4, "site.__retrieve: entered")

    #
    # Get and validate args
    #
    if siteuri == None:
        if not self.args.has_key('name') or not self.args.has_key('pub'):
            raise FreenetFreesiteCantDetermineUri
        # got enough instance vars
        siteuri = uri(type='SSK',
                      hash=self.args['pub'],
                      sskpath=self.args['name'])
        LOGMSG(1, "site.retrieve: fetching '%s'" % siteuri)
    else:
        if not isinstance(siteuri, uri):
            #set_trace()
            siteuri = uri(siteuri)
    if todir == None:
        todir = getattr(self, 'todir', None)
    if todir == None or todir == '' or not os.path.isdir(todir):
        os.makedirs(todir)
        #raise FreenetFreesiteBadDir(todir)

    LOGMSG(3, "site.retrieve: uri='%s', dir='%s'" \
                % (siteuri, todir))

    # Set htl and past args
    htl = args.get('htl', self.args.get('htl', 20))
    past = args.get('past', 0)

    #
    # Get the key
    #
    LOGMSG(3, "site.get: htl=%d name='%s' key='%s'" % (htl, parentdoc, siteuri))
    failed = True
    basekey = key.get(siteuri, raw=1, htl=htl, retries=3, graceful=1)
    if basekey == None:
        LOGMSG(2, "site.get: failed to get doc '%s', key '%s'" % (parentdoc, siteuri))
        self.failures += 1
        return
    LOGMSG(3, "site.get: successfully got key '%s'" % siteuri)

    #
    # If there's no metadata map, just save the file
    #
    doclist = basekey.metadata.map.keys()
    if len(doclist) == 0:
        # save this key
        fd = self.opendocfile(todir, parentdoc)
        fd.write(str(basekey))
        fd.close()

    # recursively get all the files
    #set_trace()
    for doc in doclist:
        tgt = basekey.metadata.targeturi(doc)

        #set_trace()

        if type(tgt) == types.ListType:
            #
            # reassemble a splitfile
            #
            if parentdoc and not doc:
                doc = parentdoc
            fd = self.opendocfile(todir, doc)
            for chunk in tgt:
                chunkKey = key.get(chunk, raw=1, graceful=1, htl=htl)
                if chunkKey == None:
                    LOGMSG(3, "site.__get: failed to get chunk %s" % chunk)
                    fd.close()
                    os.unlink(splitname)
                    self.failures += 1
                    continue
                fd.write(str(chunkKey))
            fd.close()
        elif tgt != None:
            # named file target
            #set_trace()
            if parentdoc:
                doc = parentdoc
            self.__get(tgt, todir, doc, htl=htl)

        else:
            # no target - write out file now
            if parentdoc and not doc:
                doc = parentdoc
            fd = self.opendocfile(todir, doc)
            fd.write(str(basekey))
            fd.close()
    return

    LOGMSG(4, "site.retrieve: metadata:\n%s" % basekey.metadata)

    #set_trace()
    tgt = basekey.metadata.targeturi(siteuri.mskpath, -past)

    LOGMSG(3, "site.retrieve: fetching map at %s" % tgt)
    nextkey = fcp.getKey(tgt, raw=1, htl=htl)
    LOGMSG(4, "site.retrieve: metadata:\n%s" % nextkey.metadata)
    
    return nextkey
</t>
<t tx="T78">def opendocfile(self, todir, docfile):
    """
    Internal utility - open a new doc file for writing,
    first creating any needed parent directories.

    Arguments:
     - todir - base directory
     - docname - name of document, which includes relative directory paths
    """

    if docfile == None or docfile == '':
        docfile = "__default__"

    fullpath = todir + "/" + docfile

    pathbits = fullpath.split("/")

    filename = pathbits.pop()
    parentdir = "/".join(pathbits)

    if not os.path.isdir(parentdir):
        os.makedirs(parentdir)

    LOGMSG(3, "writing key to file %s" % fullpath)
    fd = open(fullpath, "w")
    return fd

</t>
<t tx="T79">class key(MutableString):
    """
    freenet.key is a MutableString subclass
    extended to contain and manipulate *retrieved* freenet keys
    the raw key data, plus other pertinent stuff like metadata, uri etc.

    Client programs should not normally need to create key objects.

    Attributes:
      - data     - raw data for the key, also returned by repr(inst)
      - metadata - key's metadata
      - uri      - uri object for key
    Methods:
      - all the usual string methods
    """

    @others
</t>
<t tx="T80">def __init__(self, rawdata='', meta='', keyuri=None, **attrs):
    """
    Creates an instance of a key object.
    Arguments:
      - raw - raw data for key
      - meta - key's metadata
      - uri - key's uri
    Keywords:
      - host - FCP host, defaults to global 'defaultHost'
      - port - FCP port, defaults to global 'defaultPort'
    """

    #set_trace()
    if rawdata == None:
        rawdata = ''

    # stick in raw key data
    MutableString.__init__(self, rawdata)

    # add other mandatory stuff
    #print "key init: metadata = ", meta
    if isinstance(meta, metadata):
        self.metadata = meta
    elif meta != '':
        self.metadata = metadata(meta)
    else:
        self.metadata = None

    if isinstance(keyuri, uri):
        self.uri = keyuri
    elif keyuri == None:
        self.uri = None
    elif keyuri != '':
        self.uri = uri(keyuri)
    else:
        self.uri = None

    #print "freenet.key.__init__: keyuri='%s'" % keyuri
    #print "key init: attrs = ", attrs

    # now stick in the optional stuff
    self.host = defaultHost
    self.port = defaultPort

    for k in attrs.keys():
        #print "key init: adding attr ", k, "=", attrs[k]
        setattr(self, k, attrs[k])
</t>
<t tx="T81">def get(self, keyuri=None, **args):
    """
    Unimethod which retrieves the key

    Atguments:
     - keyuri - URI to fetch. If none, looks for URI instance var
    Returns:
     - if called statically, returns a new key object with the retrieved key
     - if called from an instance, fetches the key into the instance and
       returns a ref to that instance.
    Keywords:
     - htl - hops to live
     - retries - number of times to retry, default 0
     - graceful - default False, fail gracefully, returning None
       if graceful is not set, then key read failures raise an exception
    """
    #set_trace()
    #if not isinstance(self, key):
    #    return key('', '', keyuri).get(**args)

    if keyuri == None:
        if self.uri == None:
            raise FreenetKeyReadFail("&lt;no uri&gt;")
        else:
            keyuri = self.uri
        
    # create temporary accessor object
    #set_trace()
    host = args.get('host', self.host)
    port = args.get('port', self.port)
    
    mynode = node(host, port)

    retries = args.get('retries', 0)
    htl = args.get('htl', 20)
    graceful = args.get('graceful', 0)
    LOGMSG(3, "key.get: htl=%d retries=%d graceful=%d uri=%s" \
                % (htl, retries, graceful, keyuri))
    
    failed = True
    for i in range(retries+1):
        try:
            k = mynode.get(keyuri, htl=args.get('htl', 20))
            failed = False
            break;
        except FreenetKeyNotFound:
            pass
    if failed:
        if not graceful:
            raise FreenetKeyNotFound
        else:
            return None

    # success
    self.data = k.data
    self.metadata = k.metadata
    self.uri = k.uri
    return self
</t>
<t tx="T82">def put(self, keyuri=None, rawdata=None, meta=None, **args):
    """
    Unimethod which inserts a key

    Atguments:
     - keyuri - URI to insert. If none, seeks uri from instance vars
     - rawdata - raw data to insert,
     - metadata - metadata to insert with key
    Keywords:
     - htl - hops to live, default taken from instance if called from instance
     - raw - default 1, whether to insert as raw
    Returns:
     - if called statically, returns a new key object with the retrieved key
     - if called from an instance, fetches the key into the instance and
       returns a ref to that instance.
    """
    #set_trace()
    #if not isinstance(self, key):
    #    return key(rawdata, meta, keyuri, **args).put()

    if keyuri != None:
        self.uri = keyuri
    if self.uri == None:
        raise FreenetKeyInsertFail("&lt;no uri&gt;")
    if rawdata != None:
        self.data = rawdata
    if meta != None:
        self.metadata = metadata(meta)
    if args.has_key('htl'):
        self.htl = args['htl']
    if args.has_key('raw'):
        self.raw = args['raw']
    else:
        self.raw = 1
    
    # create temporary accessor object
    host = args.get('host', self.host)
    port = args.get('port', self.port)
    
    mynode = node(host, port)

    mynode.put(self.data, self.metadata, self.uri, htl=self.htl)
    return self
</t>
<t tx="T83">class uri(MutableString):
    """
    Representation of a freenet key URI, broken up into its
    component parts.
    """

    reTrailpub = re.compile(".*(PAgM|BCMA)$")
    validKeyTypes = ['KSK', 'SSK', 'CHK', 'SVK', 'MSK']

    @others

</t>
<t tx="T84">def __init__(self, raw='', type='', hash='', sskpath='', mskpath='', pub='PAgM', **args):
    """
    Instantiates a URI object
    """

    #print "raw='%s', type='%s', hash='%s', sskpath='%s', mskpath='%s', pub='%s'" % (
    #            raw, type, hash, sskpath, mskpath, pub)

    # just in case we're trying to use a uri object as the 'raw' arg
    if isinstance(raw, uri):
        self.type = raw.type
        self.hash = raw.hash
        self.sskpath = raw.sskpath
        self.mskpath = raw.mskpath
        self.pub = raw.pub
        self.data = raw.render()
        return

    elif raw:

        #print "uri: raw='%s'" % raw

        issskpriv = args.get('sskpriv', False)

        if (True in [i != '' for i in [type, hash, sskpath, mskpath]]):
            # spit - trying to instantiate with raw uri AND uri parts
            raise FreenetUriRawMustExcludeOthers

        # key specs are one of:
        #  [freenet:]KSK@&lt;hash&gt;[//[&lt;mskpath&gt;]]
        #  [freenet:]CHK@&lt;hash&gt;[//[&lt;mskpath&gt;]]
        #  [freenet:]SSK@&lt;hash&gt;[/[&lt;sskpath&gt;]][//[&lt;mskpath&gt;]]
        #  [freenet:]CHK@&lt;hash&gt;[//[&lt;mskpath&gt;]]

        # strip off the 'freenet:'
        #tmp = raw.split("freenet:")
        if raw[0:8] in ["freenet:", "entropy:"]:
            raw = raw[8:]
        tmp = [raw]
 
        tmpl = len(tmp)
        if tmpl &gt; 2:
            print "fail 1"
            raise FreenetInvalidUriError    # more than one 'freenet:' in uri
        elif tmpl == 2:
            if tmp[0] != '':
                print "fail 2"
                raise FreenetInvalidUriError # there's stuff before the 'freenet:' in URI
            else:
                raw = tmp[1] # grab the bit after the 'freenet:'
        elif tmpl == 1:
            pass # ok - no 'freenet:' in uri
        else:
            print "fail 3"
            raise FreenetInvalidUriError # empty raw string

        # now grab keytype
        tmp = raw.split("@")
        tmpl = len(tmp)
        if tmpl == 1:
            tmp[0:0] = ["KSK"]
        elif tmpl &gt; 2:
            print "fail 4"
            raise FreenetInvalidUriError # must have exactly one '@'
        type = tmp[0]
        nextbit = tmp[1]
        if type not in self.validKeyTypes:
            print "fail 5"
            raise FreenetInvalidUriKeyType

        mskpath = nextbit.split("//")
        premsk = mskpath.pop(0)
        mskpath = "//".join(mskpath)
        if type == 'SSK':
            # extract bits from SSK
            sskpath = premsk.split("/")
            hash = sskpath.pop(0)
            sskpath = "/".join(sskpath)
            #print "HASH =", hash
            if not self.reTrailpub.match(hash):
                #print "NO HASH MATCH"
                if not issskpriv:
                    #print "strange - no 'PAgM"
                    #print "fail 6"
                    #raise FreenetInvalidUriError # ssk hash doesn't end in magic 'PAgM'
                    pass
                else:
                    pass
                pub = ''

            if hash.endswith("PAgM") or hash.endswith("BCMA"):
                pub = "PAgM"
                hash1 = hash[:-4]
            else:
                pub = ''
                hash1 = hash
            if hash == '':
                print "strange - no 'PAgM"
                # raise FreenetInvalidUriError
            else:
                hash = hash1
        else:
            hash = premsk
            pub = ''

        self.type = type
        self.hash = hash
        self.pub = pub
        self.sskpath = sskpath
        self.mskpath = mskpath

    else:
        if type == '':
            type = 'KSK'
        if hash == '':
            raise FreenetInvalidUriError
        if type not in self.validKeyTypes:
            raise FreenetInvalidUriKeyType

        if type != 'SSK':
            pub = ''

        self.type = type
        self.hash = hash
        self.pub = pub
        self.sskpath = sskpath
        self.mskpath = mskpath

    self.data = self.render()

</t>
<t tx="T85">def render(self):
    """
    Assemble the URI components into a URI string
    """

    #print "uri_repr: entered"
        
    if self.type == 'SSK' and self.sskpath != '':
        sskbits = "/" + self.sskpath
    else:
        sskbits = ''
    if self.mskpath != '':
        mskbits = "//" + self.mskpath
    else:
        mskbits = ''

    if self.type in ['SSK', 'SVK']:
        ret = "%s@%s%s%s%s" % (self.type,
                               self.hash,
                               self.pub,
                               sskbits,
                               mskbits)
    else:
        ret = "%s@%s%s" % (self.type, self.hash, mskbits)
    #print "uri: repr = '%s'" % ret
    return ret
</t>
<t tx="T86">def dbr(self, future=0, increment=86400, offset=0):
    """
    Calculates a DBR-modified URI, based on offset and increment.
    Spits if the uri is not an SSK or KSK

    Arguments:
     - future - number of time intervals in future (default 0)

    Returns:
     - a new URI object with the date prefix

    Exceptions:
     - FreenetIllegalDBR - key is not a KSK or SSK, so DBR can't happen
    """
    if self.type not in ['KSK', 'SSK']:
        raise FreenetIllegalDBR(self.render())

    return uri(type=self.type,
               hash=self.hash,
               sskpath="%s-%s" % (dbr(future, increment, offset), self.sskpath))
</t>
<t tx="T87">def __repr__(self):
    """
    Render the URI into a plain string
    """
    return repr(self.render())
</t>
<t tx="T88">def __str__(self):
    """
    Return URI rendered as a plain string
    """
    return self.render()

</t>
<t tx="T89">class metadata(MutableString):
    """
    This class will develop into a 'swiss army knife' for freenet metadata

    With the metadata class, you can parse a raw metadata string
    received from a key fetch.

    You can also construct a metadata string with the high level
    methods.

    """

    @others
</t>
<t tx="T90"># build some regexps for parsing
reDocHeader = re.compile("\s*Version[\r\n]+\s*")
reDocFooter = re.compile("\s*End[ \t]*[\r\n]+")
rePartSep = re.compile("\s*EndPart[\r\n]+\s*Document[\r\n]+\s*")
reLineSep = re.compile("\s*[\r\n]+\s*")
reEqSep = re.compile("\s*=\s*")

MetadataKeywords = ['Name',
                    'Info.Format',
#                        'Info.Description',
                    'Redirect.Target',
                    'DateRedirect.Target',
                    'DateRedirect.Offset',
                    'DateRedirect.Increment',
                    'SplitFile.Size', 
                    'SplitFile.BlockCount',
                    'SplitFile.Block.[0-9a-fA-F]+']
#print MetadataKeywords
MetadataKeywords = ["^%s$" % k.replace(".", "\\.") for k in MetadataKeywords]
#print MetadataKeywords
reMetaKeywords = re.compile("|".join(MetadataKeywords))
#print "ok"

data = ''
metaRevision = '1'
metaParts = []
metaDict = {}
metaTrailing = ''

</t>
<t tx="T91">def __init__(self, raw=None, **args):
    """
    Constructor for metadata objects.

    You can instantiate a metadata object in one of 2 ways:
     - pass the constructor an existing string of raw metadata,
       as received from a freenet key fetch, or
     - pass in nothing, or some high-level keywords, to build
       up a complete metadata object from scratch. Note that
       if you dont' give any keywords, you can invoke the 'add'
       method at any time to add documents to the metadata.

    Arguments:
     - raw  - optional - Raw string to be parsed upon creation
       of the object
    Keywords:
     - to be defined
    Exceptions:
     - to be defined
    """

    # save the raw string, if any
    if raw == None:
        raw = ''
    #self.data = raw
    self.map = {}
    if isinstance(raw, metadata):
        self.map = raw.map
        self.data = raw.data
        self.metaTrailing = raw.metaTrailing
        self.metaRevision = raw.metaRevision
    else:
        self.parseRaw(raw)

</t>
<t tx="T92">def add(self, name='', action=None, **args):
    """
    Add a document to a metadata map.
    Arguments:
     - name - name of the document
       (eg, 'fred', for SSK@blahdeblah/blahdeblah//fred)
     - mimetype - MIMEtype of the document, default 'text/plain'.
     - action - how to fetch the document, one of:
        - None (default) - look no further (invalid unless name = '')
        - 'Redirect'     - perform a straight redirect to another key
        - 'DateRedirect' - do a date-based redirect to another key
        - 'SplitFile'    - swarm in the document from a splitfile spec

    Keyword Args (required or not, according to 'action'):
     - target ([Date]Redirect only) - target URI to go for
     - mimetype - the mimetype for the file
     - offset (DateRedirect only) - DBR offset in seconds from
       midnight GMT, default 0
     - increment (DateRedirect only) - frequency of DBR in seconds
       (default 86400, 1 day)
     - splitsize (SplitFile only, mandatory, no default) - size of each
       splitfile chunk
     - splitchunks (Splitfile only, mandatory, no default) a sequence of
       URIs for the splitfile chunks, in exact order
     - extras - a dict of extra declarations, that will be rendered into
       the document metadata verbatim.

    Returns:
     - None

    Exceptions:
     - lots - yet to be defined

    Examples:
     - x.add("images/fred.jpg", mimetype="image/jpeg")
     - x.add("fred.jpg", "Redirect", target="CHK@blahblah", mimetype="image/jpeg")
     - x.add("fred.html", "DateRedirect", target="KSK@blah", mimetype="text/html",
       increment=3600)

    Warning:
     - If you add a doc with the same name as an existing doc, the old one will
       get overwritten by the new one, without warning.

    For more information on metadata, refer to the Metadata Specification
    on the Freenet website - www.freenetproject.org, click on
    'Developers/Public Area'.
    """
    # Are we adding the default document?
    if action==None or action == '':
        # spit if any illegal keywords given
        for arg in args.keys():
            if arg not in ['mimetype', 'extras']:
                raise FreenetMetadataBadArguments(
                    "No keywords allowed with default action except 'mimetype' and 'extras'")
        # spit if name given
        if name != '':
            raise FreenetMetadataBadArguments(
                "You must specify an 'action' keyword when adding a non-default document")
        mimetype = args.get('mimetype', 'text/plain')
        self.map[name] = {'mimetype': mimetype, 'action':''}

    # Adding a Redirect document?
    elif action=='Redirect':
        # just need redirect target, spit at anything else
        if not args.has_key('target'):
            raise FreenetMetadataBadArguments(
                "Redirect requires 'target' keyword")
        for k in args.keys():
            if k not in ['target', 'mimetype', 'extras']:
                raise FreenetMetadataBadArguments(
                    "'target' is the only permitted arg with redirect")
        tgturi = uri(args['target'])
        self.map[name] = {'action':'Redirect', 'target':tgturi}
        if args.has_key('mimetype'):
            self.map[name]['mimetype'] = args['mimetype']

    # Adding a DateRedirect?
    elif action=='DateRedirect':
        # date-based redirect - pick off dbr-related args
        if not args.has_key('target'):
            raise FreenetMetadataBadArguments(
                "DateRedirect requires 'target' keyword")
        for k in args.keys():
            if k not in ['target', 'offset', 'increment', 'extras']:
                raise FreenetMetadataBadArguments(
                    "Illegal DBR argument keyword '%s'" % k)
        tgturi = uri(args['target'])
        offset = args.get('offset', 0)
        increment = args.get('increment', 86400)
        self.map[name] = {'action':'DateRedirect', 'target':tgturi}
        if offset != 0:
            self.map[name]['offset'] = offset
        if increment != 86400:
            self.map[name]['increment'] = increment

    # Adding a SplitFile set?
    elif action=='SplitFile':
        if not args.has_key('splitsize'):
            raise FreenetMetadataBadArguments(
                "Missing splitsize")
        if not args.has_key('splitchunks'):
            raise FreenetMetadataBadArguments(
                "Missing splitchunks")
        splitchunks = args['splitchunks']
        if not isinstance(splitchunks, list):
            raise FreenetMetadataBadArguments(
                "splitchunks arg should be a list of URIs")
        for k in args.keys():
            if k not in ['splitsize', 'splitchunks', 'extras']:
                raise FreenetMetadataBadArguments(
                    "Illegal DBR argument keyword '%s'" % k)
        # splitfiles need a default mimetype
        mimetype = args.get('mimetype', 'text/plain')

        # grab chunk details
        splitsize = int(args['splitsize'])
        splitchunks = [uri(chunk) for chunk in splitchunks]

        # construct map entry
        self.map[name] = {'action':'SplitFile',
                          'splitsize':splitsize,
                          'splitchunks':splitchunks,
                          'mimetype':mimetype}
    else:
        raise FreenetMetadataBadArguments(
            "Illegal action '%s'" % action)

    # add any extras
    self.map[name]['extras'] = args.get('extras', {})
</t>
<t tx="T93">def set(self, doc, attr, val=None):
    """
    Set the metadata attributes for a document in the map.

    Older settings remain intact, unless the attributes you're passing
    include a name of an existing attribute. (For example, if existing
    map has 'Info.Format', and     you call this func with a new
    'Info.Format' setting, it will overwrite the old one).

    Arguments:
     - doc - name of document in the map. If document is not present in map,
       an exception will occur
     - Either:
         - attribs - dict of attribs to set for this document
       OR:
         - name - name of attrib to set
         - value - value of attrib
    """

    # is doc already in the map?
    if not self.map.has_key(doc):
        raise FreenetMetadataBadArguments("set(): doc '%s' nonexistent in map" % doc)

    if type(attr) is types.DictType:
        for k in attr.keys():
            if k == 'mimetype':
                self.map[doc]['mimetype'] = attr[k]
            else:
                self.map[doc]['extras'][k] = attr[k]
    elif isinstance(attr, str):
        if val != None:
            self.map[doc]['extras'][attr] = str(val)
    else:
        raise FreenetMetadataBadArguments("set: must pass dict or name and value")
</t>
<t tx="T94">def targeturi(self, doc='', future=0):
    """
    Determines the target uri required to reach document 'doc'.
    Automatically handles redirects, dateredirects etc.

    Arguments:
     - doc - the document to look up in the map. Defaults to the map's
       default document
     - future - only valid for date-based redirect - number of time intervale
       in the future to calculate
    Returns - depends on document action:
     - None, if there are no redirects or splitfiles
     - uri of target, if it's a straight redirect or dateredirect
     - sequence of splitfile URIs, if target is a splitfile
    Exceptions:
     - FreenetMetadataNoSuchDocument - document is not present in the map
    """


    if doc == None:
        doc = ''
    if not self.map.has_key(doc):
        if doc == '':
            return None # bit of a fudge
        else:
            u = self.targeturi()
            #set_trace()
            u.mskpath = doc
            return u
            return uri(str(u) + "//" + doc) # yikes - hack alert!!!
        #raise FreenetMetadataNoSuchDocument

    docprops = self.map[doc]
    action = docprops['action']

    if action == '':
        # use data from this key, don't chase metadata
        return None 

    elif action == 'Redirect':
        return docprops['target']

    elif action == 'DateRedirect':
        tgt = docprops['target']
        return tgt.dbr(future, docprops['increment'], docprops['offset'])

    elif action == 'SplitFile':
        return docprops['splitchunks']

    else:
        raise FreenetMetadataNoSuchDocument(doc)
</t>
<t tx="T95">def documents(self):
    """
    Returns a list of documents listed in the key's metadata map
    """
    return self.metadata.map.keys()
</t>
<t tx="T96">def parseRaw(self, raw='', strict=True):
    """
    Parse and store a raw metadata string.
    Discards any old metadata strings or elements that were stored.
    """

    if not isinstance(raw, str) and not isinstance(raw, MutableString):
        raise FreenetMetadataNotStringError

    #set_trace()

    #print "parseRaw: parsing metadata '%s'\n" % raw
    strict = True

    self.data = raw
    self.metaRevision = '1'
    #self.metaParts = []
    self.map = {}
    self.metaTrailing = ''
    if raw=='':
        #print "no metadata"
        return None # nothing to do

    #set_trace()

    # tear off header
    raw = self.reDocHeader.split(raw, 1)
    if len(raw) == 1:
        if strict:
            raise FreenetMetadataBadHeader
        return False # can't do much more here
    if raw[0] != '':
        if strict:
            raise FreenetMetadataBadHeader
        # if not strict, can just ignore junk before header
    raw = raw[1]

    # tear off footer
    raw = self.reDocFooter.split(raw, 1)
    if len(raw) == 1:
        if strict:
            raise FreenetMetadataBadFooter
        return False # missing footer
    self.metaTrailing = raw[1]
    raw = raw[0]

    # now, can carve up into parts
    parts = self.rePartSep.split(raw)
    if len(parts) == 0:
        return False # no actual metadata here!

    # dice up each section into lines
    parts = [[self.parseRawLine(line)
                for line in self.reLineSep.split(part)]
                  for part in parts]

    # extract and validate head section
    headpart = parts.pop(0)
    if len(headpart) != 1 or len(headpart[0]) != 2 or headpart[0][0] != 'Revision':
        if strict:
            raise FreenetMetadataBadRevision
        else:
            self.metaRevision = '1' # sane default
    else:
        self.metaRevision = headpart[0][1]

    #
    # now convert the whole thing into a dict of doc names with properties
    #
    metadict = {}
    #print 'dicing up into parts:\n', parts
    for part in parts:
        absDict = {} # absDict == 'abstract dictionary'
        partdict = dict(part)
        name = partdict.get('Name', '')
        if partdict.has_key('Info.Format'):
            absDict['mimetype'] = partdict.get('Info.Format')
        if partdict.has_key('Info.Description'):
            absDict['mimetype'] = partdict.get('Info.Description')

        # handle other keywords
        if partdict.has_key('Redirect.Target'):
            # plain redirect
            absDict['action'] = 'Redirect'
            absDict['target'] = uri(partdict['Redirect.Target'])
            absDict['args'] = partdict
        elif partdict.has_key('DateRedirect.Target'):
            # Date-based redirect
            absDict['action'] = 'DateRedirect'
            #absDict['DateRedirect.Target'] = partdict.get('DateRedirect.Target')
            absDict['target'] = uri(partdict['DateRedirect.Target'])
            # note - 86400 == 0x15180
            absDict['increment'] = int(partdict.get('DateRedirect.Increment', '15180'), 16)
            absDict['offset'] = int(partdict.get('DateRedirect.Offset', '0'), 16)
            absDict['args'] = partdict
        elif partdict.has_key('SplitFile.BlockCount'):
            # Splitfile
            absDict['action'] = 'SplitFile'
            absDict['splitsize'] = int(partdict['SplitFile.Size'], 16)
            nblocks = int(partdict['SplitFile.BlockCount'], 16)
            blocks = []
            #set_trace()
            for i in range(nblocks):
                tmpuri = uri(partdict['SplitFile.Block.%x' % (i+1)])
                blocks.append(tmpuri)
            absDict['splitchunks'] = blocks
        else:
            # No action - only parse mimetype
            absDict['action'] = ''
            if not absDict.has_key('mimetype'):
                absDict['mimetype'] = "text/plain"

        # add the extras
        absDict['extras'] = {}
        for e in partdict.keys():
            if not self.reMetaKeywords.match(e):
                absDict['extras'][e] = partdict[e]

        # add to the map
        metadict[name] = absDict
    #print "parts:\n", parts

    # save the parts
    #self.metaParts = parts
    self.map = metadict
</t>
<t tx="T97">def __repr__(self):
    """
    Return a rendered string representation of the metadata
    """
    #set_trace()
    return repr(self.render())
</t>
<t tx="T98">def __str__(self):
    """
    Return a printable string of the rendered metadata
    """
    #set_trace()
    return self.render()
</t>
<t tx="T99">def parseRawLine(self, line):
    """
    Dices up a 'field = val' line
    Strips all leading/trailing spaces
    """

    bits = self.reEqSep.split(line, 1)
    if len(bits) != 2 or bits[0] == '':
        raise FreenetMetadataBadLine(line)
    return bits
</t>
<t tx="T100">def render(self):
    """
    Assemble a raw metadata string from this object's metadata components
    """
    #print "calling repr"
    parts = ["Version\nRevision=%s\n" % self.metaRevision]

    #numparts = len(self.metaParts)
    #for i in range(0, numparts):
    #    if i &lt; numparts:
    #        raw += "EndPart\nDocument\n"
    #    for line in self.metaParts[i]:
    #        raw += "%s=%s\n" % (line[0], line[1])
    #raw += "End\n"
    #raw += self.metaTrailing
    ##print raw.__class__
    #return raw

    #set_trace()

    # Build doc entries from our map
    for name in self.map.keys():
        rawpart = ''
        doc = self.map[name]
        if name != '':
            rawpart += "Name=%s\n" % name # Add name if not default doc
        action = doc['action']
        if action == 'Redirect':
            rawpart += "Redirect.Target=%s\n" % doc['target']
            if name == '':
            #    # default doc - add mimetype
            #    rawpart += "Info.Format=%s\n" % doc['mimetype']
                pass
        elif action == 'DateRedirect':
            rawpart += "DateRedirect.Target=%s\n" % doc['target']
            if doc.has_key('offset'):
                rawpart += "DateRedirect.Offset=%x\n" % doc['offset']
            if doc.has_key('increment'):
                rawpart += "DateRedirect.Increment=%x\n" % doc['increment']
        elif action == 'SplitFile':
            rawpart += "SplitFile.Size=%x\n" % doc['splitsize']
            chunks = doc['splitchunks']
            numchunks = len(chunks)
            rawpart += "SplitFile.BlockCount=%x\n" % numchunks
            for i in range(numchunks):
                rawpart += "SplitFile.Block.%x=%s\n" % (i+1, chunks[i])
        if doc.has_key('mimetype'):
            rawpart += "Info.Format=%s\n" % doc['mimetype']
        if doc.has_key('description'):
            rawpart += "Info.Description=%s\n" % doc['description']

        # Add the extra bits
        if doc.has_key('extras'):
            extras = doc['extras']
            for e in extras.keys():
                rawpart += "%s=%s\n" % (e, extras[e])
        parts.append(rawpart)
    
    # Now chuck it all together
    raw = "EndPart\nDocument\n".join(parts) + "End\n"
    return raw

</t>
<t tx="T101">class Dispatcher:

    """
    Class to manage the multi-threaded dispatch of a function, with
    each thread running the function with a different set of arguments

    Example::

      def myfunc(dispObj, arg1, **kw):

          # do some stuff
          time.sleep(random.randint(2, 10))
          print "global1 = %s" % dispObj.global1
          print "arg1 = %s" % arg1
          print "keywords: %s" % kw
        
      dispObj = Dispatcher(myfunc, 4)

      dispObj.global1 = "dispatcher-global arg"
      dispObj.add("First thread")
      dispObj.add("Second thread", a=1, x="blah")
      dispObj.add("Third thread", x=9)

      dispObj.start() # launch the dispatcher

      dispObj.wait() # wait till all jobs are complete
      
    """
    def __init__(self, func, maxthreads=8):
        """
        Constructs a thread dispatcher object.

        Arguments:
         - func - some callable which should be invoked in each thread
           Upon each dispatch, the func will be called in a thread. The
           first argument of the call will be a ref to this dispatcher
           object itself

         - maxthreads - maximum number of threads which can run at any
           one time - default 8

        If there are any data items which are not thread-specific, they
        should be written as instance attributes of the dispatcher.
        """
        self._func = func
        self._jobs = Queue.Queue(0)
        self._alldispatched = Queue.Queue(1)
        self._alldone = Queue.Queue(1)
        self._threads = Queue.Queue(0)
        self._maxthreads = maxthreads
        self._threadpool = threading.Semaphore(maxthreads)
        self._countlock = threading.Lock()
        self._numrunning = 0


    def start(self):
        """
        Starts the dispatcher engine
        """
        thread.start_new_thread(self._engine, ())


    def add(self, *args, **kw):
        """
        Adds a task to the dispatcher queue

        Arguments:
         - whatever you like, however many you like

        Keywords:
         - whatever you like, however many you like

        NOTES:

         1. When this task gets launched, the func will be called
            with a ref to the dispatcher object as the first argument,
            and the subsequent args following.

            So if you call this method as::

              dispObj.add(2, "xyz", a=8, b=9)

            then upon dispatch, the callable function will be invoked as::

              func(dispObj, 2, "xyz", a=8, b=9)

         2. It's perfectly ok to invoke this method at any times before, or
            after, you launch the engine with 'start'.
        """
        self._jobs.put((args, kw))


    def wait(self, timeout=-1):
        """
        Wait for all threads to terminate

        Arguments:
         - timeout - time in seconds to wait for threads to finish,
           default is to wait forever
        """
        # pass the quit sentinel to the engine
        self._jobs.put(None)

        # wait till all jobs are dispatched (none more to launch)
        self._alldispatched.get()

        # now wait till all remaining threads have terminated
        self._alldone.get()

    def quit(self):
        """
        Causes any call to 'wait()' to return.
        
        Typically, a thread will trigger this if it decides that the aim of the
        dispatcher object has been fulfilled
        """
        self._alldone.put(None)

    def _thread(self, *args, **kw):
        """
        Launched in a thread.
        Calls the callable func
        """
        self._countlock.acquire()
        self._numrunning += 1
        self._countlock.release()

        try:
            self._threads.put(None)
            self._func(self, *args, **kw)
            self._threadpool.release()
        except:
            LOGMSG(1, "A dispatcher thread crashed!!")
            traceback.print_exc()

        self._countlock.acquire()
        self._numrunning -= 1
        if self._numrunning == 0:
            self._alldone.put(None)
        self._countlock.release()


    def _engine(self):
        """
        Do the actual work of grabbing thread slots and dispatching
        the threads.
        """
        self._running = 1
        while 1:

            # get a thread slot, or wait till one comes available
            self._threadpool.acquire()

            # get a job, or wait till one comes available
            job = self._jobs.get()

            # have we received the 'please quit' sentinel?
            if job is None:
                self._alldispatched.put(None)
                return

            # no - we have a real job to launch
            args, kw = job
            thread.start_new_thread(self._thread, args, kw)
</t>
<t tx="T102"># Warm up a connection to the FCP host
def connect(fcphost="127.0.0.1",
            fcpport=8481,
            defaultHtl=15,
            raw=False,
            maxSplitThreads=4):
    """
    You must call this function before doing any other
    operations on Freenet.

    Arguments:
      - host            - FCP host to connect to (127.0.0.1)
      - defaultHtl      - default Hops To Live (15)
      - raw             - raw mode (False)
      - maxSplitThreads - max threads when inserting splitfiles (4)
    Returns:
      - None
    Exceptions:
      - Raises FreenetHostConnectFail exception if connection failed
    """

    global defaultHost
    global defaultPort

    try:
        node(fcphost, fcpport)
    except:
        raise FreenetHostConnectError

    # got a connection
    defaultHost = fcphost
    defaultPort = fcpport


def initfec(fcphost, fcpport):
    """
    Set up some shit in the fish module
    """

    #
    # export some of our stuff into module 'fcp'
    #

    # set up fish data structures


def verbosity(level=None):
    """
    Set the verbosity level for log messages.
    Arguments:
      - 0 - Shut Up
      - 1 - Critical messages only
      - 2 - Normal Detail
      - 3 - Verbose
      - 4 - Debug (very noisy)
    A second argument sets the verbosity for the python-level callback
    Returns:
      - None
    """
    global logLevel

    if level != None:
        #_checkIfConnected()
        #if level != None:
        #    freenet_.setLogDetail(level)
        #if pylevel != None:
        logLevel = level

    return logLevel

def tempFilename():
    """
    Wrapper around tempfile.mktemp that suppresses the
    shitty warning message
    """

    warnings.filterwarnings("ignore")
    t = tempfile.mktemp()
    warnings.resetwarnings()
    return t


def _transferArgs(args, kwds):
    """
    Extracts keywords in list 'kwds' from dict 'args'.
    Arguments:
      - args - dict of args
      - kwds - list of allowed keywords
    Returns:
      - a dict with only those args found in 'args'
    """
    retargs = {}
    for k in kwds:
        v = args.get(k, None)
        if v != None:
            retargs[k] = v
    return retargs


def guessMimetype(filename):
    """
    Returns a guess of a mimetype based on a filename's extension
    """
    m = mimetypes.guess_type(filename, False)[0]
    if m == None:
        m = "text/plain"
    return m

def dbr(future=0, increment=86400, offset=0):
    """
    Useful little utility func.
    
    Calculates a target prefix for Date-Based Redirects.
    Returns it as a hex string (since this is what's needed
    for FCP interactions).

    Arguments:
     - future (default 0) - number of time periods in the future
       to calculate
     - increment (default 86400) - the period of the DBR, most
       sites are based on a 1-day (86400 seconds) period
     - offset (default 0) - number of seconds after midnight GMT
       to calculate from. Most DBR sites are based around midnight GMT

    Returns:
     - number of seconds after the epoch, formatted as a string
       containing this number in hex format.
    """
    now = time.time()
    secsSinceFirstHit = now - offset
    lastHitTime = (int(secsSinceFirstHit/increment) * increment) + offset
    wantedHitTime = lastHitTime + (future * increment)
    return "%x" % wantedHitTime


def setLogCallback(func):
    global LOGMSG
    LOGMSG = func

def defaultLogCallback(level, msg, back=0):
    global logLevel
    msg = str(msg).replace("\r\n", "\n")
    if level &lt;= logLevel:
        caller = traceback.extract_stack()[-2-back]
        full = "%s:%s:%s(): %s" % (caller[0], caller[1], caller[2], msg.replace("\n", "\n* "))

        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        finalmsg = "%s %s\n" % (now, full)
        sys.stdout.write(finalmsg)

LOGMSG = defaultLogCallback

</t>
<t tx="T103"># define a few exceptions

class FreenetError(Exception):
    """Generic Freenet Error"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "%s" % str(self.value)

class FreenetDataNotFound(FreenetError):
    """Got a 'DataNotFound' from node"""

class FreenetRouteNotFound(FreenetError):
    """Got a 'RouteNotFound' from node"""

class FreenetNotConnectedError(FreenetError):
    """Must first connect to FCP host via connectHost()"""

class FreenetHostConnectError(FreenetError):
    """Failed to connect to host FCP access port"""

class FreenetUriRawMustExcludeOthers(FreenetError):
    """When instantiating a freenet.uri object, must pass a
    raw text uri, or the uri components, not both."""

class FreenetInvalidUriError(FreenetError):
    """Invalid syntax in key URI"""

class FreenetInvalidUriKeyType(FreenetError):
    """URI Key Types must be CHK, SSK, KSK or SVK"""

class FreenetOperationFailed(FreenetError):
    """A freenet operation failed"""

class FreenetKeyNotFound(FreenetError):
    """Failed to retrieve a key"""

class FreenetKeyInsertFail(FreenetError):
    """Key Insertion failed"""

class FreenetKeyOpenFail(FreenetError):
    """Failed to open Key"""

class FreenetKeyCloseFail(FreenetError):
    """Failed to close Key"""

class FreenetKeyReadFail(FreenetError):
    """Failed to read from Key"""
    def __init__(self, val=None):
        self.val = val
    def __str__(self):
        return "Failed to read key %s" % self.val

class FreenetKeyWriteFail(FreenetError):
    """Failed to write from Key"""

class FreenetKeySequenceFail(FreenetError):
    """Failed to insert or retrieve sequenced key"""

class FreenetKeyCollision(FreenetError):
    """A key with the same URI has already been inserted"""

class FreenetEditionsExhausted(FreenetError):
    """An insert or fetch of an edition-based freesite has
    exhausted its editionMaxTries parameter"""

class FreenetMetadata(FreenetError):
    """Base class of metadata processing exceptions"""

class FreenetMetadataNotString(FreenetMetadata):
    """class metadata can only parse strings or MutableString objects"""

class FreenetMetadataBadHeader(FreenetMetadata):
    """Malformed header in metadata text"""

class FreenetMetadataBadFooter(FreenetMetadata):
    """Malformed footer in metadata text"""

class FreenetMetadataBadRevision(FreenetMetadata):
    """Malformed footer in metadata text"""

class FreenetMetadataSyntax(FreenetMetadata):
    """Catch-all for syntax errors in metadata"""

class FreenetMetadataBadLine(FreenetMetadata):
    """
    Malformed line in metadata
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "Bad Line: %s" % str(self.value)

class FreenetMetadataBadArguments(FreenetMetadata):
    """
    Illegal combination of arguments to freenet.metadata.addDoc()
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class FreenetFreesiteBadArgument(FreenetMetadata):
    """
    Malformed line in metadata
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "Bad argument: %s" % self.value

class FreenetFreesiteBadDir(FreenetMetadata):
    """
    Malformed line in metadata
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "Error reading directory: %s" % self.value

class FreenetFreesiteBadKeys(FreenetMetadata):
    """
    Malformed line in metadata
    """
    def __init__(self, pub, priv):
        self.pub = pub
        self.priv = priv
    def __str__(self):
        return "One or both SSK keys '%s' and '%s' are invalid" % (self.pub, self.priv)

class FreenetFreesiteCantRefresh(FreenetMetadata):
    """
    Malformed line in metadata
    """
    def __init__(self, val):
        self.val = val
    def __str__(self):
        return "Can't refresh freesite: %s" % self.val

class FreenetFreesiteCantDetermineUri(FreenetMetadata):
    """
    Cannot determine URI for request
    """
    def __str__(self):
        return "Cannot determine URI from method args or instance vars"

class FreenetMetadataNoSuchDocument(FreenetMetadata):
    """
    Document doesn't exist in metadata map
    """
    def __init__(self, val):
        self.val = val
    def __str__(self):
        return "Metadata map has no document called '%s'" % self.val

class FreenetIllegalDBR(FreenetMetadata):
    """
    Can't calculate DBR on this URI
    """
    def __init__(self, val):
        self.val = val
    def __str__(self):
        return "Cannot calculate date-based redirect for key %s" % self.val

class FreenetFcpError(FreenetError):
    """
    Some failure with talking FCP to node
    """
    def __init__(self, val):
        self.val = val
    def __str__(self):
        return self.val

class FreenetFcpConnectError(FreenetError):
    """
    Some failure with connecting to FCP port
    """
    def __init__(self, val):
        self.val = val
    def __str__(self):
        return self.val
</t>
<t tx="T104"></t>
<t tx="T105">#
# Makefile for building Python module for Freenet FCP access
#
# Written by David McNab, released under the GNU Lesser General
# Public License, no warrantee - yada yada yada

all: docs

clean:
	rm -rf *.pyc *~ build html dist

docs:
	PYFREENETDOC=1 epydoc freenet.py
	rm -rf doc/classref
	mv html doc/classref

install:
	python setup.py install

install-doc:
	mkdir -p /usr/share/doc/pyFreenet
	cp -rp doc/* /usr/share/doc/pyFreenet

</t>
<t tx="T106">@
README file for pyFreenet,
by David McNab &lt;david@freenet.org.nz&gt;
Feb 11, 2003
Updated Oct 30, 2003

pyFreenet is a Python package for accessing the Freenet
network.

In case you don't already know, Freenet is a network
infrastructure, running over the top of the regular
internet, which allows you to publish and access
materials with extremely high levels of anonymity,
privacy and encryption.

Freenet is the world-leading technology for preserving
the rights of the individual against the whims of
increasingly draconian governments around the world.

Visit the Freenet website at:
http://www.freenetproject.org
for more info and downloads.

With pyFreenet, you can access everything in freenet
from your own python programs. Once pyFreenet is installed,
all you need to do from your python code is:

  import freenet

then, use the methods in module 'freenet' to do whatever
you want to do.

Refer to the doco in the doc subdirectory for detailed
descriptions of the classes and methods.

</t>
<t tx="T107">@
INSTALL file for pyFreenet,
by David McNab &lt;david@freenet.org.nz&gt;
11 Feb, 2003
Updated 30 Oct, 2003


INTRODUCTION
------------

To install this software, you'll need a Python environment,
preferably 2.2 or later, with distutils installed.

If you want to modify, debug, extend or enhance this module,
it's best if you can install the Leo meta-structuring code
editor - http://leo.sourceforge.net. Leo is a great editor,
because it gives you an excellent hierarchical view of the
code, and it now allows for seamless integration with the
2 'official' programmers editors, vim and [x]emacs. The
code will be far more understandable if you view it with Leo.

Build and installation of pyfreenet is pretty similar to
building other python modules.


HOW TO AND INSTALL
------------------------

1) Prerequisites:
   You'll need the following software to be properly
   built, installed, set up and working:

     * Access to a Freenet node - preferably your own
     * The freenet node *must* be running over Java 1.4.1 or
       later - otherwise you might see weird lock-ups
     * If you're running your client code on a separate machine
       to that on which the node is running, you must configure
       your node to allow the FCP connections from your client machine
     * Python 2.1 or later
     * Python's distutils (installable on Debian as
       'python-dev' or 'python2.x-dev')

2) Type:

	su -c "make install install-doc"

3) Test your installation. Type:

    python testsuite.py

   This will run a rigorous series of tests of this API. If all
   the tests pass, you can be quite confident that the API should
   perform as expected.

You can find documentation for these classes in
/usr/share/doc/pyFreenet


TROUBLESHOOTING
---------------

Symptom:

	$ make
	python setup.py build
	Traceback (most recent call last):
	File "setup.py", line 12, in ?
	from distutils.core import setup, Extension
	ImportError: No module named distutils.core
	make: *** [freenet_.so] Error 1

Solution:

	You haven't got python's distutils
	installed. Please install python-dev
	package


Symptom:

	$ make install
	epydoc freenet.py freenet_.so
	make: epydoc: Command not found
	make: *** [doc] Error 127

Possible cause:

	You don't seem to have epydoc (the python documentation
    generator) installed.

Solution:

	Install the 'epydoc' package (on debian, this is
	'python-epydoc').


</t>
<t tx="T108">@first #!/usr/bin/env python
@language python

# This file does the python-specific build and install
# for pyFreenet
#
# Written David McNab, 11 Feb 2003

import sys,os
from distutils.core import setup, Extension

setup(name='freenet',
	  version = '0.2.4',
	  description = 'pyFreenet - Python API for Freenet access',
	  py_modules = ['freenet']
	  )

</t>
<t tx="T109"></t>
<t tx="T110">@language python
# You can ignore this file - it's just used for testing.
# If you set the env var PYTHONSTARTOP=autoexec.py, then
# running python will automatically execute this file.

#import freenet_
#print dir(freenet_)
#from freenet_ import *

#print "importing freenet"
import socket
from pdb import set_trace

#set_trace()

from freenet import *

#verbosity(4)

#connect("hermes")

#print "connected to FCP @ hermes"
#a = access()
#print "got access object 'a'"

#x = a.getKey("SSK@rdRr~qa898tOpfh4QPDV6mMY0jgPAgM/pyFreenet", raw=0)
#x = a.getKey("KSK@gpl.txt")
#m = x.metadata

#m = metadata()
#print "adding file1"
#m.add("file1", "Redirect", target="blah")
#print "adding file2"
#m.add("file2/file3", "Redirect", target="CHK@blah", mimetype="mimetype1")
#print "adding file3"
#m.add("file3/foo", "DateRedirect", target="KSK@haha", increment=3600)
#print "adding file4"
#m.add("file4", "SplitFile", splitsize=65536, splitchunks=['CHK@chunk1', 'CHK@chunk2'])

#print "Created empty metadata object 'm'"

#print "starting key insert"
#a.openKey("555", "w", htl=1)
#a.writeKey("Hi, this is KSK@555\n")
#a.closeKey()

#set_trace()
#print 'hello'
#def doit():
#	global mm
#	f = open('testmeta')
#	s = f.read()
#	f.close()
#	mm= metadata(s)
	#print "Revision = '%s'" % mm.metaRevision
	#print "Parts = ", mm.metaParts
	#print "Trailing = ", mm.metaTrailing

#ff = site(name="mysite",
#			  fromdir="/main/freesites/testsite",
#			  htl=0)
#print "Created freesite object 'ff'"
#ff.insert()

#lst = ff.readdir("/tmp/blah")
#for f in lst.keys():
#	print f, lst[f]

#doit()

#verbosity(2, 4)

#set_trace()
#a = key.put("KSK@123", "This is ksk@123", htl=0)

#fs = site.insert("/main/freesites/testsite", htl=0)

#k = key.get("CHK@eN0Em4wJUu7zeLlYm2w7kzEW3y8KAwI,kzjcBfGXhJvpseL7vS6RvA", raw=1)

#mysite = site.get("SSK@ADKF8pkxs3PnIdz-WruV~rmMmKMPAgM/site//", "/tmp/freesite")


#mysite = site.get("SSK@rdRr~qa898tOpfh4QPDV6mMY0jgPAgM/pyFreenet//",
#				  "/main/freesites/others/pyfreenet")

#site.get("SSK@fgbuxwSCCjOJHsUI-9-uijD1haQPAgM/flinks/8//",
#		 "/main/freesites/others/flinks",
#		 htl=1)


#site.get("SSK@h~ixmz11-tDOox9O1gQyjkzAUCcPAgM/fmb/5//",
#		 "/main/freesites/others/fmb",
#		 htl=12)

#f = fcp("hermes")

#set_trace()
#dat, met = f.getKey("KSK@aa")

#import freenet
#freenet.host = "hermes"

#freenet.verbosity(4)

#m = metadata()
#m.add('')
#m.set('', 'Info.Artist', 'Jimi Hendrix')

#set_trace()
#x = fcp.put("Purple Haze", m, None, 0)

#s = site.get("SSK@rdRr~qa898tOpfh4QPDV6mMY0jgPAgM/pyFreenet//", "/tmp/pyf")

#set_trace()
#connect("hermes")

#x = fproxyGet("KSK@aa")
#y = fproxyGet("SSK@rdRr~qa898tOpfh4QPDV6mMY0jgPAgM/pyFreenet//pyFreenet-0.1.tar.gz")


# freenet:CHK@GAe2NrIQsqLU9-wSdSrlImsgE2wLAwI,HNstQ496ceRzRuqhIbHksw
#k = fish.putfile("CHK@", "ian1.jpg", 0)

#set_trace()
#res = gj.getFecFile("CHK@GAe2NrIQsqLU9-wSdSrlImsgE2wLAwI,HNstQ496ceRzRuqhIbHksw",
#					"ian1-req.jpg", "hermes", 8481, 25)

#set_trace()
#k = fcp.get("CHK@GAe2NrIQsqLU9-wSdSrlImsgE2wLAwI,HNstQ496ceRzRuqhIbHksw")
#fd = open("/tmp/pic.jpg", "wb")
#fd.write(str(k))
#fd.close()

import testsuite
#testsuite.run()
#testsuite.test01()
#testsuite.test02()
#testsuite.test10()
#testsuite.test11()

# run a freesite insertion test using on-the-fly fileset

#verbosity(4)
#connect("hermes")
#n = node("hermes", htl=0)

#sskpub = 'Xe0bcIreriP-kNjrZzjEkT4fYOw'
#sskpriv = 'O0mOKEhVD-6F2OSKpQxnwaSR9Qs'
#sskpub, sskpriv = n.genkeypair()

#fileset={'index.html':{'mimetype':'text/html',
#                       'raw':'&lt;html&gt;&lt;body&gt;&lt;h1&gt;index dot fucking html&lt;/h1&gt;',
#                       },
#         'fred/mary.txt':{'mimetype':'text/plain',
#                          'raw':'this is fred/mary.txt',
#                          },
#         }

#set_trace()

#u = n.putsite(None, name="hello", htl=0, files=fileset, pub=sskpub, priv=sskpriv)
#su = str(u)

#k = n.get(su+"//index.html")

#sskpub, sskpriv = n.genkeypair()

#pxPub = "SSK@" + sskpub + "PAgM/"
#pxPriv = "SSK@" + sskpriv + "/"

#putseq(self, keyprefix, startnum=0, numtries=5, keydata='', keymeta=None, htl=None)

#k1 = n.putseq(pxPriv, 0, 3, "some stuff")

#set_trace()
#socket.setdefaulttimeout(5)
#k = n.get("CHK@betaep~u~KTIBZwOVX9t7tLXdmkPAwI,DiK612AcgoH4zUF57BCF9A")

if 0:
    verbosity(4)
    n = node("hermes", htl=0)
    import random
    print "Creating 48k of random shit"
    chars = []
    i = 0
    while i &lt; 48000:
        chars.append(chr(random.randint(0x20, 0x7f)))
        i = i + 1
    shit = "".join(chars)

    print "generating SSK URIs"
    sskPub, sskPriv = n.genkeypair()
    uriPriv = "SSK@%s/test" % sskPriv
    uriPub = "SSK@%sPAgM/test" % sskPub
    print "Public: ", uriPub
    print "Private:", uriPriv

    print "Inserting this shit"
    k = n.put(shit, '', uriPriv, 0)

    print "And retrieving it"
    kRet = n.get(uriPub)

    print "Comparing"
    if kRet != shit:
        print "ouch - different"
    else:
        print "identical - success"

if 1:
    verbosity(4)
    n = node("hermes", 8482, htl=0)

    pu, pr = n.genkeypair()

    uPu = "SSK@%sPAgM/0" % pu
    uPr = "SSK@%s/0" % pr

    k = n.put("hello, world", "", uPr)

</t>
<t tx="T111">@first #!/usr/bin/python

"""
Program which talks to two different freenet/entropy nodes, and measures the time
taken for a key inserted at one node to be visible on another
"""

node1Addr = "localhost"
node1Port = 8481

node2Addr = "localhost"
node2Port = 8491

htlInsert = 25
htlRetrieve = 25

verbosity = 2

numRuns = 10

import time, random, sys, os
import freenet

uriPrefix = "KSK@xfertest"

def runTests():
    
    global node1Addr, node1Port, node2Addr, node2Port, htlInsert, htlRetrieve
    global verbosity, numRuns

    node1Addr = raw_input(    "Node 1 hostname? [%s] " % node1Addr) or node1Addr
    node1Port = int(raw_input("Node 1 port? [%s] " % node1Port) or node1Port)
    htlInsert = int(raw_input("Insert HTL? [%s] " % htlInsert) or htlInsert)
    
    node2Addr = raw_input("Node 2 hostname? [%s] " % node2Addr) or node1Addr
    node2Port = int(raw_input("Node 2 port? [%s] " % node2Port) or node2Port)
    htlRetrieve = int(raw_input("Retrieve HTL? [%s] " % htlRetrieve) or htlRetrieve)

    verbosity = int(raw_input("Logging verbosity? (0-4) [%s] " % verbosity) or verbosity)
    numRuns = int(raw_input("Number of times to run? [%s] " % numRuns) or numRuns)

    freenet.verbosity(verbosity)
    node1 = freenet.node(node1Addr, node1Port, htl=25)
    node2 = freenet.node(node2Addr, node2Port, htl=25)
    
    teststr = "%04d" % random.randint(0, 10000)
    for run in range(0, numRuns):
        uri = "%s-%s-%s.txt" % (uriPrefix, teststr, run)
        print "runTests: starting test %d of %d" % (run, numRuns)
        runTest(node1, node2, uri)

def runTest(node1, node2, uri):

    rawstr = "This is the test key inserted at %s\n" % uri
    
    print "Inserting key %s into node1" % uri
    while 1:
        try:
            node1.put(rawstr, "", uri)
            break
        except freenet.FreenetRouteNotFound:
            pass
    print "Retrieving key %s from node1" % uri
    while 1:
        try:
            k = node1.get(uri)
            if k.data != rawstr:
                print "Error - what we retrieved is not what we inserted"
            else:
                print "Retrieve from node1 successful"
            break
        except freenet.FreenetDataNotFound:
            print "got DNF requesting %s from node1 !?!?!?" % uri
        except freenet.FreenetRouteNotFound:
            print "got RNF requesting %s from node1 !?!?!?" % uri
        
    then = time.time()
    print "Retrieving key %s from node2" % uri
    while 1:
        then1 = time.time()
        try:
            k = node2.get(uri)
            break
        except freenet.FreenetDataNotFound:
            now = time.time()
            if now - then1 &lt; 300:
                print "   got DNF requesting %s, retrying in %ds, %ds so far" % (
                             uri, 300-(now-then1), now-then)
        except freenet.FreenetRouteNotFound:
            now = time.time()
            if now - then1 &lt; 300:
                print "   got RNF requesting %s, retrying in %ds, %ds so far" % (
                             uri, 300-(now-then1), now-then)
        if now-then1 &lt; 300:
            time.sleep(300 - (now-then1))

    now = time.time()
    print "Finally got key %s from node2 after %ds" % (uri, now-then)

if __name__ == '__main__':
    runTests()
</t>
<t tx="T112">@first #!/usr/bin/python

"""
Test script for freesite inserts

Attempts inserts of a freesite as edition, dbr and oneshot
"""
import time
import freenet

node = freenet.node("hermes", 8482, htl=0, allowSplitfiles=0)
freenet.verbosity(2)

sskPub, sskPriv = node.genkeypair()

def insert_oneshot():
    # try the oneshot insert

    index_html_oneshot = "&lt;html&gt;&lt;body&gt;Here is index.html on oneshot site at %s&lt;/body&gt;&lt;/html&gt;" % time.asctime()
    mary_txt_oneshot = "This is fred/mary.txt on oneshot site inserted at %s" % time.asctime()
    
    files_oneshot =  {'index.html' :     {'mimetype' : 'text/html',
                                          'raw' : index_html_oneshot,
                                          },
                      '/fred/mary.txt' : {'mimetype' : 'text/plain',
                                          'raw' : mary_txt_oneshot,
                                          },
                      }


    k_oneshot = node.putsite(siteType='oneshot',
                             name='oneshot',
                             pub=sskPub,
                             priv=sskPriv,
                             files=files_oneshot,
                             )

    return k_oneshot

def insert_edition():

    keys = {}
    for edition_no in range(0, 4):

        index_html_edition = "&lt;html&gt;&lt;body&gt;Here is index.html on edition %s site, inserted at %s&lt;/body&gt;&lt;/html&gt;" % (
                                   edition_no, time.asctime())
        
        mary_txt_edition = "This is fred/mary.txt on edition %d site, created at %s" % (edition_no, time.asctime())
        
        files_edition =  {'index.html' :     {'mimetype' : 'text/html',
                                              'raw' : index_html_edition,
                                              },
                          '/fred/mary.txt' : {'mimetype' : 'text/plain',
                                              'raw' : mary_txt_edition,
                                              },
                          }
    
        k_edition = node.putsite(siteType='edition',
                                 name='edition',
                                 pub=sskPub,
                                 priv=sskPriv,
                                 files=files_edition,
                                 )
        keys[edition_no] = k_edition
    return keys

def insert_dbr():
    # try the dbr insert
    index_html_dbr = "&lt;html&gt;&lt;body&gt;Here is index.html on oneshot site, at %s&lt;/body&gt;&lt;/html&gt;" % time.asctime()
    mary_txt_dbr = "This is fred/mary.txt on dbr site inserted at %s" % time.asctime()
    files_dbr =  {'index.html' :     {'mimetype' : 'text/html',
                                      'raw' : index_html_dbr,
                                      },
                  '/fred/mary.txt' : {'mimetype' : 'text/plain',
                                      'raw' : mary_txt_dbr,
                                      },
                  }

    k_dbr = node.putsite(siteType='dbr',
                         name='dbr',
                         pub=sskPub,
                         priv=sskPriv,
                         files=files_dbr,
                         )
    return k_dbr

def insert():
    k_oneshot = insert_oneshot()
    k_edition = insert_edition()
    k_dbr = insert_dbr()

    return {'oneshot': k_oneshot, 'edition': k_edition, 'dbr': k_dbr}

if __name__ == '__main__':
    sites = insert()
    print sites</t>
<t tx="T113">@first #!/usr/bin/env python
@language python
@others

# Automated test suite for pyFreenet.

# If your pyFreenet installation was successfuly, you should 
# try running this script, which will put pyFreenet through
# 11 tests.

</t>
<t tx="T114">"""
testsuite.py
Runs a series of tests of pyFreenet package.
"""

import freenet


# set these to your freenet node's address

#freenet_fcp_host = "127.0.0.1"
#freenet_fcp_host = "192.168.2.1"
freenet_fcp_host = "192.168.1.3"

#freenet_fcp_port = 8481
freenet_fcp_port = 8482
randomshit = "some stuff which gets endlessly repeated in a key 123"
randomsize = 1400000

import sys, time, os
from pdb import set_trace

</t>
<t tx="T115">def test01():
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 01: import the module"
	import freenet
	freenet.verbosity(4)
	print "TESTSUITE: PASSED\n\n"


</t>
<t tx="T116">def test02():
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 02: connect to node"
	try:
		freenet.connect(freenet_fcp_host, freenet_fcp_port)
	except:
		print "TESTSUITE: failed"
		raise
	print "TESTSUITE: PASSED\n\n"


</t>
<t tx="T117">def test03():
	global keyname
	global myuri
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 03: Create a basic URI"
	keyname = "KSK@pyFreenetTest%s" % time.strftime("%H%M%S")
	myuri = freenet.uri(keyname)
	print "TESTSUITE: PASSED - key = '%s'" % str(myuri)

</t>
<t tx="T118">
def test04():
	global keyname
	global myuri
	global insertedksk
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 04: Insert a basic KSK key - raw"
	try:
		print "TESTSUITE: Inserting as URI: '%s'" % myuri
		insertedksk = freenet.node.put("This is key '%s'\n" % keyname, '', myuri, htl=0)
	except:
		print "TESTSUITE: failed"
		raise
	print "TESTSUITE: uri = '%s'" % insertedksk.uri
	print "TESTSUITE: PASSED\n\n" % insertedksk.uri

</t>
<t tx="T119">
def test05():
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 05: Retrieve the key back again"
	print "TESTSUITE: (any big delay here is probably a bug)"

	global insertedksk

	try:
		k = freenet.node.get(insertedksk.uri)
	except:
		print "TESTSUITE: failed"
		raise
	print "TESTSUITE: Key uri = %s" % k.uri
	print "TESTSUITE: Key data:\n", k
	print "TESTSUITE: PASSED\n\n"

</t>
<t tx="T120">
def test06():
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 06: Insert a key with metadata, and retrieve"
	try:
		m = freenet.metadata()
		m.add('', mimetype="text/html")
		txt = "&lt;html&gt;&lt;head&gt;&lt;title&gt;pyFreenet test 06&lt;/title&gt;&lt;/head&gt;&lt;body&gt;&lt;h1&gt;test 06&lt;/h1&gt;This is test 06 - seems ok&lt;/body&gt;&lt;/html&gt;\n"
		uri = freenet.uri("KSK@test06-%s" % time.strftime("%H%M%S"))
		k = freenet.node.put(txt, m, uri, htl=0)
		kr = freenet.node.get(uri)
		print "TESTSUITE: retrieved URI = ", kr.uri
		print "TESTSUITE: retrieved text:\n", kr
		print "TESTSUITE: with metadata:\n", kr.metadata
	except:
		#print failed
		raise
	print "TESTSUITE: PASSED\n\n"


</t>
<t tx="T121">
def test07():
	global pubkey
	global privkey
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 07: generate an SSK keypair"
	pubkey, privkey = freenet.node.genkeypair()
	print "TESTSUITE: pubkey='%s', privkey='%s'" % (pubkey, privkey)
	print "TESTSUITE: PASSED"

</t>
<t tx="T122">
def test08():
    global pubkey
    global privkey
    global siteuri
    global mydir

    print "TESTSUITE: ********************************************************"
    print "TESTSUITE: test 08: Create and insert a dummy freesite"
    print
    mydir = "testsite-%s" % time.strftime("%H%M%S")
    print "TESTSUITE: (creating freesite in directory '%s')" % mydir
    os.mkdir(mydir)
    fd = open(mydir+"/index.html", "w")
    fd.write('&lt;html&gt;&lt;head&gt;&lt;title&gt;my testsite&lt;/title&gt;&lt;/head&gt;\n')
    fd.write('&lt;body&gt;\n')
    fd.write('&lt;h1&gt;TestSite&lt;/h1&gt;\n')
    fd.write('File: &lt;a href="subdir/file.txt"&gt;subdir/file.txt&lt;/a&gt;\n')
    fd.write('&lt;/body&gt;&lt;/html&gt;\n')
    fd.close()
    os.mkdir(mydir+"/subdir")
    fd = open(mydir+"/subdir/file.txt", "w")
    fd.write("This is file.txt from the test freesite")
    fd.close()
    print "TESTSUITE: Freesite created at %s" % mydir
    print "TESTSUITE: Inserting freesite..."
    siteuri = freenet.site.put(mydir, name="testsite", pub=pubkey, priv=privkey, htl=0)
    print "TESTSUITE: Site URI = %s" % siteuri
    print "TESTSUITE: PASSED\n\n"

</t>
<t tx="T123">
def test09():
	global siteuri, mydir

	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 09: Retrieve this site back"
	print
	print "TESTSUITE: Retrieving site '%s'" % siteuri

	mysite = freenet.site.get(siteuri, mydir + "-get")
	print "TESTSUITE: site retrieved successfully"
	print "TESTSUITE: Retrieved URI = ", mysite.uri
	print "TESTSUITE: deleting site directories"
	os.system("rm -rf testsite-*")
	print "TESTSUITE: PASSED\n\n"

</t>
<t tx="T124">
def test10():
    print "TESTSUITE: ********************************************************"
    print "TESTSUITE: test 10: Generate and Insert a large file."
    print
    # Change the string below to create a unique file.
    # The purpose of creating the same file each time is so that you don't flood
    # your datastore with crap each time you run these tests.
    print "TESTSUITE: Note - edit this test script if you want to insert new random rubbish."
    print

    global biginsertedkey
    global fileOrig
    global fileCheck

    print "TESTSUITE: Creating large file..."
    fileOrig = freenet.tempFilename()
    fileCheck = freenet.tempFilename()
    fd = open(fileOrig, "wb")
    size = 0
    linenum = 1
    while size &lt; randomsize:
        nextline = "%s: line %d\n" % (randomshit, linenum)
        linenum += 1
        fd.write(nextline)
        size += len(nextline)
    fd.close()
    print "TESTSUITE: Done."

    # change this later to use fcp.putfile()
    print "TESTSUITE: Reading large file into memory..."
    fd = open(fileOrig)
    rawdata = fd.read()
    fd.close()
    print "TESTSUITE: Done."
    print "TESTSUITE: Inserting this large file - this might take ages..."

    #set_trace()

    #biginsertedkey = freenet.node.put(rawdata, None, None, 0)
    mynode = freenet.node(freenet_fcp_host, freenet_fcp_port)
    biginsertedkey = mynode.put(rawdata, None, None, 0, allowSplitfiles=0)
    print "TESTSUITE: Big file '%s' apparently inserted fine" % fileOrig
    print "TESTSUITE: Inserted URI: %s" % biginsertedkey.uri
    print "TESTSUITE: PASSED\n\n"
</t>
<t tx="T125">
def test11():
    print "TESTSUITE: ********************************************************"
    print "TESTSUITE: test 11: Get big file inserted in test10, and compare"
    print

    global biginsertedkey
    global fileOrig
    global fileCheck

    try:
        rxuri = biginsertedkey.uri
        print "TESTSUITE: Aiming to retrieve URI: %s" % rxuri
        print "TESTSUITE: This might take a while..."
        bigretrievedkey = freenet.node.get(rxuri)
        print "TESTSUITE: Seems to have retrieved OK - now compare!"
        insdata = str(biginsertedkey)
        retdata = str(bigretrievedkey)
        if insdata != retdata:
            print "TESTSUITE: Difference in files: orig size %d, retrieved size %d" % \
                  len(insdata), len(retdata)
            raise Exception("what we retrieved is not what we inserted!")
        else:
            print "TESTSUITE: Inserted file and retrieved file are identical"
            print "TESTSUITE: PASSED\n\n"
            
    except:
        print "TESTSUITE: **************************"
        print "TESTSUITE:  TEST 11 FAILED!!!! :((("
        print "TESTSUITE: **************************"
        raise

</t>
<t tx="T126">
def run():
    test01()
    test02()
    test03()
    test04()
    test05()
    test06()
    test07()
    test08()
    test09()
    test10()
    test11()

    print
    print "TESTSUITE: ********************************************************"
    print "TESTSUITE: All tests succeeded - module 'freenet' awaits you"
    print "TESTSUITE: ********************************************************"
    print


</t>
<t tx="T127">if __name__ == '__main__':
    run()
</t>
</tnodes>
</leo_file>
