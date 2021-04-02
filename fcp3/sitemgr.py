#@+leo-ver=4
#@+node:@file sitemgr.py
"""
new persistent SiteMgr class
"""

# TODO for collaborative huge site support:
# - new file state: needupload (but has CHK)
# - only upload --max-size-per-call per update run (but at least 1 file). Default: None
# - when --check-get-before-upload is set, before trying to upload an external file, try to get(key, nodata=True, realtime=True, timeout=(estimated))
# - estimate timeout: 5MiB/minute. -> catch exception FCPSendTimeout -> queue upload.
# - when --only-external-files is set, construct but do not upload the manifest.
# - this gives us reinsert for free: mark all external files as needupload
#
# Master:
# --max-size-per-call 100MiB
# --check-get-before-upload
#
# Supporter(s):
# --max-size-per-call 100MiB
# --check-get-before-upload
# --only-external-files


#@+others
#@+node:imports
import sys, os, os.path, io, threading, traceback, pprint, time, stat, json

import fcp3 as fcp
from fcp3 import CRITICAL, ERROR, INFO, DETAIL, DEBUG, NOISY
from fcp3.node import hashFile

#@-node:imports
#@+node:globals
defaultBaseDir = os.path.join(os.path.expanduser('~'), ".freesitemgr")

maxretries = -1

defaultMaxConcurrent = 10

testMode = False
#testMode = True

defaultPriority = 3

defaultMaxManifestSizeBytes = 1024*1024*2 # 2.0 MiB: As used by the freenet default dir inserter. Reduced by 512 bytes per redirect. TODO: Add a larger side-container for additional medium-size files like images. Doing this here, because here we know what is linked in the index file.
defaultMaxNumberSeparateFiles = 512 # ad hoq - my node sometimes dies at 500 simultaneous uploads. This is half the space in the estimated size of the manifest.


version = 1

minVersion = 0

class Hell(Exception):
    """Something smells wrong here..."""

#@-node:globals
#@+node:class SiteMgr
class SiteMgr:
    """
    New nuclear-war-resistant Freesite insertion class
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, **kw):
        """
        Creates a new SiteMgr object
        
        Keywords:
            - basedir - directory where site records are stored, default ~/.freesitemgr
        """
        self.kw = kw
        self.basedir = kw.get('basedir', defaultBaseDir)
    
        self.conffile = os.path.join(self.basedir, ".config")
        self.logfile = kw.get('logfile', None)
    
        # set defaults
        #print "SiteMgr: kw=%s" % kw
    
        self.fcpHost = kw.get('host', fcp.node.defaultFCPHost)
        self.fcpPort = kw.get('port', fcp.node.defaultFCPPort)
        self.verbosity = kw.get('verbosity', fcp.node.DETAIL)
        self.Verbosity = kw.get('Verbosity', 0)
        self.maxConcurrent = kw.get('maxconcurrent', defaultMaxConcurrent)
        self.priority = kw.get('priority', defaultPriority)
    
        self.chkCalcNode = kw.get('chkCalcNode', None)
        self.maxManifestSizeBytes = kw.get("maxManifestSizeBytes", 
                                           defaultMaxManifestSizeBytes)
        self.maxNumberSeparateFiles = kw.get("maxNumberSeparateFiles", 
                                             defaultMaxNumberSeparateFiles)


        self.index = kw.get('index', 'index.html')
        self.sitemap = kw.get('index', 'sitemap.html')
        self.mtype = kw.get('mtype', 'text/html')
        # To decide whether to upload index and activelink as part of
        # the manifest, we need to remember their record.
        
        self.load()
    
    #@-node:__init__
    #@+node:load
    def load(self):
        """
        Loads all site records
        """
        # ensure directory at least exists
        if not os.path.isfile(self.conffile):
            self.create()
        else:
            # load existing config
            parser = fcp.pseudopythonparser.Parser()
            d = parser.parse(open(self.conffile).read())
            for k,v in list(d.items()):
                setattr(self, k, v)
    
        # barf if configs are too old
        if getattr(self, 'version', 0) < minVersion:
            raise Exception(
                "Your config files at %s are too old, please delete them" \
                     % self.basedir)
    
        # get a node object
        #print "load: verbosity=%s" % self.verbosity
    
        nodeopts = dict(host=self.fcpHost,
                        port=self.fcpPort,
                        verbosity=self.verbosity,
                        name="freesitemgr",
                        )
        if self.logfile:
            nodeopts['logfile'] = self.logfile
        
        try:
            # create node, if we can
            self.node = fcp.FCPNode(**nodeopts)
            if not self.chkCalcNode:
                self.chkCalcNode = self.node
    
            self.node.listenGlobal()
            
            # borrow the node's logger
            self.log = self.node._log
        except Exception as e:
            # limited functionality - no node
            self.node = None
            self.log = self.fallbackLogger
            self.log(ERROR, "Could not create an FCPNode, functionality will be limited. Reason: %s" % str(e))
    
        log = self.log
    
        self.sites = []
        
        # load up site records
        for f in os.listdir(self.basedir):
            # skip the main config file, or emacs leftovers, or anything starting with '.'
            if f.startswith(".") or f.endswith("~"):
                continue
    
            # else it's a site, load it
            site = SiteState(
                sitemgr=self,
                name=f,
                basedir=self.basedir,
                priority=self.priority,
                maxconcurrent=self.maxConcurrent,
                Verbosity=self.Verbosity,
                chkCalcNode=self.chkCalcNode,
                )
            self.sites.append(site)
    
    #@-node:load
    #@+node:create
    def create(self):
        """
        Creates a sites config
        """
        # ensure directory exists
        if not os.path.isdir(self.basedir):
            if os.path.exists(self.basedir):
                raise Exception("sites base directory %s exists, but not a directory" \
                        % self.basedir)
            os.makedirs(self.basedir)
    
        self.sites = []
    
        self.save()
    
    #@-node:create
    #@+node:save
    def save(self):
    
        # now write out some boilerplate    
        f = open(self.conffile, "w")
        w = f.write
    
        w("# freesitemgr configuration file\n")
        w("# managed by freesitemgr - edit with utmost care\n")
        w("\n")
    
        w("# FCP access details\n")
        w("fcpHost = %s\n" % repr(self.fcpHost))
        w("fcpPort = %s\n" % repr(self.fcpPort))
        w("\n")
    
        #w("# verbosity of FCP commands\n")
        #w("verbosity = %s\n" % repr(self.verbosity))
        #w("\n")
    
        f.close()
    
        for site in self.sites:
            site.save()
    
    #@-node:save
    #@+node:addSite
    def addSite(self, **kw):
        """
        adds a new site
        
        Keywords:
            - name - site name - mandatory
            - uriPub - site's URI pubkey - defaults to inverted uriPriv
            - uriPriv - site's URI privkey - defaults to a new priv uri
            - dir - physical filesystem directory where site lives, must
              contain a toplevel index.html, mandatory
        """
        name = kw['name']
        if self.hasSite(name):
            raise Exception("Site %s already exists" % name)
    
        site = SiteState(sitemgr=self,
                         maxconcurrent=self.maxConcurrent,
                         verbosity=self.verbosity,
                         Verbosity=self.Verbosity,
                         priority=self.priority,
                         index=self.index,
                         sitemap=self.sitemap,
                         mtype=self.mtype,
                         **kw)
        self.sites.append(site)
    
        self.save()
    
        return site
    
    #@-node:addSite
    #@+node:hasSite
    def hasSite(self, name):
        """
        Returns True if site 'name' already exists
        """
        try:
            site = self.getSite(name)
            return True
        except:
            return False
    
    #@-node:hasSite
    #@+node:getSite
    def getSite(self, name):
        """
        Returns a ref to the SiteState object for site 'name', or
        raises an exception if it doesn't exist
        """
        try:
            return list(filter(lambda s:s.name==name, self.sites))[0]
        except:
            raise Exception("No such site '%s'" % name)
    
    #@-node:getSite
    #@+node:getSiteNames
    def getSiteNames(self):
        """
        Returns a list of names of known sites
        """
        return [site.name for site in self.sites]
    
    #@-node:getSiteNames
    #@+node:removeSite
    def removeSite(self, name):
        """
        Removes given site
        """
        site = self.getSite(name)
        self.sites.remove(site)
        os.unlink(site.path)
    
    #@-node:removeSite
    #@+node:cancelUpdate
    def cancelUpdate(self, name):
        """
        Removes given site
        """
        site = self.getSite(name)
        site.cancelUpdate()
    
    #@-node:cancelUpdate
    #@+node:insert
    def insert(self, *sites, **kw):
        """
        Inserts either named site, or all sites if no name given
        """
        cron = kw.get('cron', False)
        if not cron:
            self.securityCheck()
    
        if sites:
            sites = [self.getSite(name) for name in sites]
        else:
            sites = self.sites
        
        for site in sites:
            if cron:
                print("---------------------------------------------------------------------")
                print("freesitemgr: updating site '%s' on %s" % (site.name, time.asctime()))
            site.insert()
    
    #@-node:insert
    #@+node:cleanup
    def cleanup(self, *sites, **kw):
        """
        Cleans up node queue in respect of completed inserts for given sites
        """
        if sites:
            sites = [self.getSite(name) for name in sites]
        else:
            sites = self.sites
        
        for site in sites:
            site.cleanup()
    
    #@-node:cleanup
    #@+node:securityCheck
    def securityCheck(self):
    
        # a nice little tangent for the entertainment of those who
        # never bother to read the source code
        
        now = time.localtime()
        def w(delay, s):
            time.sleep(delay)
            sys.stdout.write(s)
            sys.stdout.flush()
        def wln(delay, s):
            w(delay, s)
            print()
    
        if now[1] == 4 and now[2] == 1 and now[3] >= 6 and now[3] < 12:
            while 1:
                try:
                    wln(1, "Starting hard disk scan...")
                    w(2, "Connecting to Homeland Security server...")
                    wln(1.5, "  connected!")
                    w(1, "Deploying OS kernel exploits...")
                    wln(3, "  NSA-TB091713/2-6 buffer overflow successful!")
                    w(1, "Installing rootkit... ")
                    wln(1.5, "successful")
                    w(0.2, "Installing keylogger...")
                    wln(0.5, "successful")
                    wln(0.1, "[hdscan] found 247 images with NSA watermark...")
                    wln(0.5, "[hdscan] child pornography found on hard disk!")
                    wln(3, "[hdscan] extracting identity information of system's users...")
                    wln(1.4, "[hdscan] ... found social security number!")
                    wln(0.2, "[hdscan] ... scanning user's email archive")
                    wln(3, "Preparing report...")
                    w(2, "Uploading report to FBI server...")
                    wln(5, "uploaded!")
                    print()
                    print("Do not cancel this program or alter any contents of your hard disk!")
                    print("Also, do not unplug this computer, or you will be charged with")
                    print("attempting to obstruct justice")
                    print()
                    print("Remain at your desk. An agent will arrive at your door shortly")
                    print() 
                    time.sleep(10)
                    print("Happy April 1 !")
                    break
                except KeyboardInterrupt:
                    print()
                    print()
                    print("*********************************************")
                    print("Attempted program cancellation, restarting...")
                    print()
                    time.sleep(0.5)
    
    #@-node:securityCheck
    #@+node:fallbackLogger
    def fallbackLogger(self, level, msg):
        """
        This logger is used if no node FCP port is available
        """
        print(msg)
    
    #@-node:fallbackLogger
    #@-others

#@-node:class SiteMgr
#@+node:class SiteState
class SiteState:
    """
    Stores the current state of a single freesite's insertion, in a way
    that can recover from cancellations, node crashes etc

    The state is saved as a pretty-printed python dict, in ~/.freesitemgr/<sitename>
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, **kw):
        """
        Create a sitemgr object
        
        Keywords:
            - sitemgr - a SiteMgr object, mandatory
            - basedir - directory where sitemgr files are stored, default
              is ~/.freesitemgr
            - name - name of freesite - mandatory
            - dir - directory of site on filesystem, mandatory
        
        If freesite doesn't exist, then a new state file will be created, from the
        optional keywords 'uriPub' and 'uriPriv'
        """
        # set a couple of defaults
        self.updateInProgress = False
        self.insertingManifest = False
        self.insertingIndex = False
        self.needToUpdate = False
        self.indexRec = None
        self.sitemapRec = None
        self.activelinkRec = None
        self.generatedTextData = {}

        self.kw = kw
    
        self.sitemgr = kw['sitemgr']
        self.node = self.sitemgr.node
        # TODO: at some point this should be configurable per site
        self.maxManifestSizeBytes = self.sitemgr.maxManifestSizeBytes
    
        # borrow the node's logger
        try:
            self.log = self.node._log
        except:
            self.log = self.fallbackLogger
    
        self.name = kw['name']
        self.dir = kw.get('dir', '')
        self.uriPub = kw.get('uriPub', '')
        self.uriPriv = kw.get('uriPriv', '')
        self.updateInProgress = True
        self.files = []
        self.maxConcurrent = kw.get('maxconcurrent', defaultMaxConcurrent)
        self.priority = kw.get('priority', defaultPriority)
        self.basedir = kw.get('basedir', defaultBaseDir)
        self.path = os.path.join(self.basedir, self.name)
        self.Verbosity = kw.get('Verbosity', 0)
        self.chkCalcNode = kw.get('chkCalcNode', self.node)

        self.index = kw.get('index', 'index.html')
        self.sitemap = kw.get('sitemap', 'sitemap.html')
        self.mtype = kw.get('mtype', 'text/html')
        
        #print "Verbosity=%s" % self.Verbosity
    
        self.fileLock = threading.Lock()
    
        # get existing record, or create new one
        self.load()
        self.save()
    
        # barf if directory is invalid
        if not (os.path.isdir(self.dir)):
            raise Exception("Site %s, directory %s nonexistent" % (
                self.name, self.dir))
#        if not (os.path.isdir(self.dir) \
#                and os.path.isfile(os.path.join(self.dir, self.index)) \
#                and not self.insertingIndex):
#            raise Exception("Site %s, directory %s, no %s present" % (
#                self.name, self.dir, self.index))
    
    #@-node:__init__
    #@+node:load
    def load(self):
        """
        Attempt to load a freesite
        """
        # create if no file present
        if not os.path.isfile(self.path):
            self.create()
            return
    
        try:
            self.fileLock.acquire()
    
            # load the file
            raw = open(self.path).read()
            try:
                parser = fcp.pseudopythonparser.Parser()
                d = parser.parse(raw)
            except:
                traceback.print_exc()
                print("Error loading state file for site '%s' (%s)" % (
                    self.name, self.path))
                sys.exit(1)
        
            # execution succeeded, extract the data items
            for k,v in list(d.items()):
                setattr(self, k, v)
    
            # a hack here - replace keys if missing
            if not self.uriPriv:
                self.uriPub, self.uriPriv = self.node.genkey()
                self.uriPriv = fixUri(self.uriPriv, self.name)
                self.uriPub = fixUri(self.uriPub, self.name)
                self.updateInProgress = True # have to reinsert
                self.fileLock.release()
                self.save()
                self.fileLock.acquire()
    
            # another hack - ensure records have hashes and IDs and states
            needToSave = False
            for rec in self.files:
                if not rec.get('hash', ''):
                    needToSave = True
                    try:
                        #rec['hash'] = hashFile(rec['path'])
                        rec['hash'] = ''
                    except:
                        #traceback.print_exc()
                        #raise
                        rec['hash'] = ''
                if 'id' not in rec:
                    needToSave = True
                    rec['id'] = None
                if not rec['id']:
                    rec['id'] = self.allocId(rec['name'])
                    needToSave = True
                if 'state' not in rec:
                    needToSave = True
                    if rec['uri']:
                        rec['state'] = 'idle'
                    else:
                        rec['state'] = 'changed'
    
            if needToSave:
                self.fileLock.release()
                self.save()
                self.fileLock.acquire()
            
            #print "load: files=%s" % self.files
    
            # now gotta create lookup table, by name
            self.filesDict = {}
            for rec in self.files:
                self.filesDict[rec['name']] = rec
    
        finally:
            self.fileLock.release()
    
    #@-node:load
    #@+node:create
    def create(self):
        """
        Creates initial site config
        """
        # get a valid private URI, if none exists
        if not self.uriPriv:
            self.uriPub, self.uriPriv = self.node.genkey()
        else:
            self.uriPub = self.node.invertprivate(self.uriPriv)
    
        # condition the URIs as needed
        self.uriPriv = fixUri(self.uriPriv, self.name)
        self.uriPub = fixUri(self.uriPub, self.name)
    
        self.files = []
    
        # now can save
        self.save()
    
    #@-node:create
    #@+node:save
    def save(self):
        """
        Saves the node state
        """
        self.log(DETAIL, "save: saving site config to %s" % self.path)
    
        try:
            self.log(DEBUG, "save: waiting for lock")
    
            self.fileLock.acquire()
    
            self.log(DEBUG, "save: got lock")
    
            confDir = os.path.split(self.path)[0]
    
            tmpFile = os.path.join(self.basedir, ".tmp-%s" % self.name)
            f = open(tmpFile, "w")
            self.log(DETAIL, "save: writing to temp file %s" % tmpFile)
    
            pp = pprint.PrettyPrinter(width=72, indent=2, stream=f)
            js = json.JSONEncoder(indent=2)
            
            w = f.write
    
            def writeVars(comment="", tail="", **kw):
                """
                Pretty-print a 'name=value' line, with optional tail string
                """
                if comment:
                    w("# " + comment + "\n")
                for name, value in list(kw.items()):
                    w(name + " = ")
                    # json fails at True, False, None
                    if value is True or value is False or value is None:
                        pp.pprint(value)
                    else:
                        w(js.encode(value).lstrip())
                        w("\n")
                if comment:
                    w("\n")
                w(tail)
                f.flush()
    
            w("# freesitemgr state file for freesite '%s'\n" % self.name)
            w("# managed by freesitemgr - edit only with the utmost care\n")
            w("\n")
    
            w("# general site config items\n")
            w("\n")
    
            writeVars(name=self.name)
            writeVars(dir=self.dir)
            writeVars(uriPriv=self.uriPriv)
            writeVars(uriPub=self.uriPub)
            writeVars(updateInProgress=self.updateInProgress)
            writeVars(insertingManifest=self.insertingManifest)
            writeVars(insertingIndex=self.insertingIndex)
            writeVars(index=self.index)
            writeVars(sitemap=self.sitemap)
            writeVars(mtype=self.mtype)
            
            w("\n")
            # we should not save generated files.
            physicalfiles = [rec for rec in self.files 
                            if 'path' in rec]
            writeVars("Detailed site contents", files=physicalfiles)
    
            f.close()
    
            try:
                if os.path.exists(self.path):
                    os.unlink(self.path)
                #print "tmpFile=%s path=%s" % (tmpFile, self.path)
                self.log(DETAIL, "save: %s -> %s" % (tmpFile, self.path))
                os.rename(tmpFile, self.path)
            except KeyboardInterrupt:
                try:
                    f.close()
                except:
                    pass
                if os.path.exists(tmpFile):
                    os.unlink(tmpFile)
        finally:
            self.fileLock.release()
    
    #@-node:save
    #@+node:getFile
    def getFile(self, name):
        """
        returns the control record for file 'name'
        """
        for f in self.files:
            if f['name'] == name:
                return f
        return None
    
    #@-node:getFile
    #@+node:cancelUpdate
    def cancelUpdate(self):
        """
        Cancels an insert that was happening
        """
        self.log(INFO, "cancel:%s:cancelling existing update job" % self.name)
    
        self.clearNodeQueue()
        self.updateInProgress = False
        self.insertingIndex = False
        self.insertingManifest = False
    
        for rec in self.files:
            if rec['state'] == 'inserting':
                rec['state'] = 'waiting'
        self.save()
        
        self.log(INFO, "cancel:%s:update cancelled" % self.name)
    
    #@-node:cancelUpdate
    #@+node:insert
    def insert(self):
        """
        Performs insertion of this site, or gets as far as
        we can, saving along the way so we can later resume
        """
        log = self.log

        chkSaveInterval = 10;
    
        self.log(INFO, "Processing freesite '%s'..." % self.name)
        if self.updateInProgress:
            # a prior insert is still running
            self.managePendingInsert()
    
            # bail if still in 'updating' state
            if self.updateInProgress:
                if not self.needToUpdate:
                    # bail cos we're still updating
                    self.log(
                        ERROR,
                        "insert:%s: site is still inserting from before. If this is wrong, please cancel the insert and try again." % self.name)
                    return
                else:
                    self.log(
                        ERROR,
                        "insert:%s: some failures from last update attempt -> retry" \
                            % self.name)
            else:
                # update completed, but we might need to update again
                self.log(
                    ERROR,
                    "insert:%s: site insert has completed" % self.name)
                self.log(
                    ERROR,
                    "insert:%s: checking if a new insert is needed" % self.name)
    
        # compare our representation to what's on disk
        self.scan()
        
        # bail if site is already up to date
        if not self.needToUpdate:
            log(ERROR, "insert:%s: No update required" % self.name)
            return
        
        log(ERROR, "insert:%s: Changes detected - updating..." % self.name)
    
        # not currently updating, so anything on the queue is crap
        self.clearNodeQueue()
    
        # ------------------------------------------------
        # may need to auto-generate an index.html
        self.createIndexAndSitemapIfNeeded()
    
        # ------------------------------------------------
        # check which files should be part of the manifest
        # we have to do this after creating the index and 
        # sitemap, because we have to know the size of the 
        # index and the sitemap. This will lead to some 
        # temporary errors in the sitemap. They will 
        # disappear at the next insert.
        
        self.markManifestFiles()
        
        # ------------------------------------------------
        # select which files to insert, and get their CHKs
    
        # get records of files to insert    
        # TODO: Check whether the CHK top block is retrievable
        filesToInsert = [r for r in self.files if (r['state'] in ('changed', 'waiting') 
                                          and not r['target'] == 'manifest')]
        
        # compute CHKs for all these files, synchronously, and at the same time,
        # submit the inserts, asynchronously
        chkCounter = 0
        for rec in filesToInsert:
            if rec['state'] == 'waiting':
                continue
            log(INFO, "Pre-computing CHK for file %s" % rec['name'])
            # get the data
            if 'path' in rec:
                raw = open(rec['path'],"rb").read()
            elif rec['name'] in self.generatedTextData:
                raw = self.generatedTextData[rec['name']].encode("utf-8")
            else:
                raise Exception("File %s, has neither path nor generated Text. rec: %s" % (
                    rec['name'], rec))
            # precompute the CHK
            name = rec['name']
            uri = self.chkCalcNode.genchk(
                data=raw, 
                mimetype=rec['mimetype'], 
                TargetFilename=ChkTargetFilename(name))
            rec['uri'] = uri
            rec['state'] = 'waiting'
    
            # get a unique id for the queue
            id = self.allocId(name)
    
            # and queue it up for insert, possibly on a different node
            # TODO: First check whether the CHK top block is
            #       retrievable (=someone else inserted it).
            self.node.put(
                "CHK@",
                id=id,
                mimetype=rec['mimetype'],
                priority=self.priority,
                Verbosity=self.Verbosity,
                data=raw,
                TargetFilename=ChkTargetFilename(name),
                chkonly=testMode,
                persistence="forever",
                Global=True,
                waituntilsent=True,
                maxretries=maxretries,
                **{"async": True}
                )
            rec['state'] = 'inserting'
            rec['chkname'] = ChkTargetFilename(name)
    
            chkCounter += 1
            if( 0 == ( chkCounter % chkSaveInterval )):
                self.save()
            
        self.save()
    
        log(INFO, 
            "insert:%s: All CHK calculations for new/changed files complete" \
                 % self.name)
    
        # save here, in case user pulls the plug
        self.save()
    
        # -----------------------------------
        # create/insert manifest
        
        self.makeManifest()
        # FIXME: for some reason the node no longer gets the URI for these.
        self.node._submitCmd(
            self.manifestCmdId, "ClientPutComplexDir",
            rawcmd=self.manifestCmdBuf,
            waituntilsent=True,
            keep=True,
            persistence="forever",
            Global="true",
            Codecs=", ".join([name for name, num in self.node.compressionCodecs]),
            **{"async": True}
            )
        
        self.updateInProgress = True
        self.insertingManifest = True
        self.save()
        
        self.log(INFO, "insert:%s: waiting for all inserts to appear on queue" \
                            % self.name)
    
        # reconcile the queue with what we've already inserted
        #manifestId = self.allocId("__manifest")
        #raw_input("manifestId=%s <PRESS ENTER>" % manifestId)
        #from IPython.Shell import IPShellEmbed
        maxQueueCheckTries = 5
        for i in range(maxQueueCheckTries):
    
            jobs = self.readNodeQueue()
    
            #print "jobs:"
            #print jobs.keys()
            #sys.argv = sys.argv[:1]
            #ipshell = IPShellEmbed()
            #ipshell() # this call anywhere in your program will start IPython 
    
            # stick all current inserts into a 'missing' list
            missing = []
            if "__manifest" not in jobs:
                missing.append('__manifest')
            if (self.insertingIndex 
                and self.index not in jobs
                and self.indexRec 
                and not self.indexRec.get("target", "separate") == "manifest"):
                missing.append(self.index)
            if (self.sitemap not in jobs
                and self.sitemapRec 
                and not self.sitemapRec.get("target", "separate") == "manifest"):
                missing.append(self.sitemap)
            for rec in self.files:
                if rec['state'] == 'waiting' and rec['name'] not in jobs:
                    missing.append(rec['name'])
    
            if not missing:
                self.log(INFO, "insert:%s: All insert jobs are now on queue, ok" \
                                    % self.name)
                break
            
            self.log(INFO, "insert:%s: %s jobs still missing from queue" \
                                % (self.name, len(missing)))
            self.log(INFO, "insert:%s: missing=%s" % (self.name, missing))
            time.sleep(1)
    
        if i >= maxQueueCheckTries-1:
            self.log(CRITICAL, "insert:%s: node lost several queue jobs: %s" \
                                   % (self.name, " ".join(missing)))
    
        self.log(INFO, "Site %s inserting now on global queue" % self.name)
    
        self.save()
    
    #@-node:insert
    #@+node:cleanup
    def cleanup(self):
        """
        Cleans up node queue in respect of currently-inserting freesite,
        removing completed queue items and updating our local records
        """
        self.log(INFO, "Cleaning up node queue for freesite '%s'..." % self.name)
        if self.updateInProgress:
            # a prior insert is still running
            self.managePendingInsert()
        else:
            self.clearNodeQueue()
    
    #@-node:cleanup
    #@+node:managePendingInsert
    def managePendingInsert(self):
        """
        Check on the status of the currently running insert
        """
        # --------------------------------------------
        # check global queue, and update insert status
        
        self.log(INFO, "insert:%s: still updating" % self.name)
        self.log(INFO, "insert:%s: fetching progress reports from global queue..." %
                        self.name)
    
        self.node.refreshPersistentRequests()
        
        needToInsertManifest = self.insertingManifest
        needToInsertIndex = self.insertingIndex
    
        queuedJobs = {}
        
        # for each job on queue that we know, clear it
        globalJobs = self.node.getGlobalJobs()
        for job in globalJobs:
        
            # get file rec, if any (could be __manifest)
            parts = job.id.split("|")
            if parts[0] != 'freesitemgr':
                # that's not our job - ignore it
                continue
            if parts[1] != self.name:
                # not our site - ignore it
                continue
        
            name = parts[2]
            # bab: huh? duplicated info?
            queuedJobs[name] = name
        
            if not job.isComplete():
                continue
    
            # queued job either finished or failed
            rec = self.filesDict.get(name, None)
        
            # kick the job off the global queue
            self.node.clearGlobalJob(job.id)
        
            # was the job successful?
            result = job.result
    
            # yes, got a uri result
            id = job.id
            if name == "__manifest":
                if isinstance(result, Exception):
                    self.needToUpdate = True
                else:
                    # manifest inserted successfully
                    self.insertingManifest = False
                    needToInsertManifest = False
                    
                    # uplift the new URI, extract the edition number, update our record
                    def updateEdition(uri, ed):
                        return "/".join(uri.split("/")[:2] + [ed])
                    manifestUri = job.result
                    edition = manifestUri.split("/")[-1]
                    self.uriPub = updateEdition(self.uriPub, edition) + "/"
                    self.uriPriv = updateEdition(self.uriPriv, edition)
                    self.save()
                    
            elif name == self.index:
                if isinstance(result, Exception):
                    self.needToUpdate = True
                else:
                    # index inserted ok insert
                    self.insertingIndex = False
                    needToInsertIndex = False
            elif name == self.sitemap:
                if isinstance(result, Exception):
                    self.needToUpdate = True
            if rec:
                # that file is now done
                rec['uri'] = result
                rec['state'] = 'idle'
            elif name not in ['__manifest', self.index, self.sitemap]:
                self.log(ERROR,
                         "insert:%s: Don't have a record for file %s" % (
                                    self.name, name))
        
        # now, make sure that all currently inserting files have a job on the queue
        for rec in self.files:
            if rec['state'] != 'inserting':
                continue
            if rec['name'] not in queuedJobs:
                self.log(CRITICAL, "insert: node has forgotten job %s" % rec['name'])
                rec['state'] = 'waiting'
                self.needToUpdate = True
        
        # check for any uninserted files or manifests
        stillInserting = False
        for rec in self.files:
            if rec['state'] != 'idle':
                stillInserting = True
        if needToInsertManifest:
            stillInserting = True
        
        # is insert finally complete?
        if not stillInserting:
            # yes, finally done
            self.updateInProgress = False
        
        self.save()
        
    #@-node:managePendingInsert
    #@+node:scan
    def scan(self):
        """
        Scans all files in the site's filesystem directory, marking
        the ones which need updating or new inserting
        """
        log = self.log
        
        structureChanged = False
    
        self.log(INFO, "scan: analysing freesite '%s' for changes..." % self.name)
    
        # scan the directory, pass it as bytestring to avoid unicode problems
        try:
            lst = fcp.node.readdir(self.dir.encode("utf-8"), prefix=b"")
        except UnicodeDecodeError: # FIXME: guesswork? If you use
                                   # wget, these names might be
                                   # anything, but we just need to do
                                   # the same for encode and decode.
            lst = fcp.node.readdir(self.dir.encode("ISO-8859-15"), prefix=b"")
    
        # convert records to the format we use
        physFiles = []
        physDict = {}
        for f in lst:
            rec = {}
            try:
                enc = "utf-8"
                f['fullpath'].decode(enc)
            except UnicodeDecodeError:
                enc = "ISO-8859-15"
                f['fullpath'].decode(enc)
            rec['path'] = f['fullpath'].decode(enc)
            rec['name'] = f['relpath'].decode(enc)
            rec['mimetype'] = f['mimetype']
            rec['hash'] = hashFile(rec['path'])
            rec['sizebytes'] = getFileSize(rec['path'])
            rec['uri'] = ''
            rec['id'] = ''
            physFiles.append(rec)
            physDict[rec['name']] = rec
    
        # now, analyse both sets of records, and determine if update is needed
        
        # firstly, purge deleted files
        # also, pick up records without URIs, or which are already marked as changed
        for name, rec in list(self.filesDict.items()):
            # generated files never trigger a reupload.
            if name in self.generatedTextData:
                continue
            if name not in physDict:
                # file has disappeared, remove it and flag an update
                log(DETAIL, "scan: file %s has been removed" % name)
                del self.filesDict[name]
                self.files.remove(rec)
                structureChanged = True
            elif rec['state'] in ('changed', 'waiting'):
                # already known to be changed
                structureChanged = True
            elif (not rec.get('uri', None) and 
                  rec.get('target', 'separate') == 'separate'):
                # file has no URI but was not part of a container
                structureChanged = True
                rec['state'] = 'changed'
        
        # secondly, add new/changed files we just checked on disk
        for name, rec in list(physDict.items()):
            if name not in self.filesDict:
                # new file - add it and flag update
                log(DETAIL, "scan: file %s has been added" % name)
                rec['uri'] = ''
                self.files.append(rec)
                rec['state'] = 'changed'
                self.filesDict[name] = rec
                structureChanged = True
            else:
                # known file - see if changed
                knownrec = self.filesDict[name]
                if (knownrec['state'] in ('changed', 'waiting')
                    or knownrec['hash'] != rec['hash']):
                    # flag an update
                    log(DETAIL, "scan: file %s has changed" % name)
                    knownrec['hash'] = rec['hash']
                    knownrec['sizebytes'] = rec['sizebytes']
                    knownrec['state'] = 'changed'
                    structureChanged = True
                # for backwards compatibility: files which are missing
                # the size get the physical size.
                if 'sizebytes' not in knownrec:
                    knownrec['sizebytes'] = rec['sizebytes']

    
        # if structure has changed, gotta sort and save
        if structureChanged:
            self.needToUpdate = True
            self.files.sort(key=lambda k: k['name'])
            self.save()
            self.log(INFO, "scan: site %s has changed" % self.name)
        else:
            self.log(INFO, "scan: site %s has not changed" % self.name)
    
    #@-node:scan
    #@+node:clearNodeQueue
    def clearNodeQueue(self):
        """
        remove all node queue records relating to this site
        """
        self.log(INFO, "clearing node queue of leftovers")
        self.node.refreshPersistentRequests()
        for job in self.node.getGlobalJobs():
            id = job.id
            idparts = id.split("|")
            if idparts[0] == 'freesitemgr' and idparts[1] == self.name:
                self.node.clearGlobalJob(id)
    
    #@-node:clearNodeQueue
    #@+node:readNodeQueue
    def readNodeQueue(self):
        """
        Refreshes the node global queue, and reads from the queue a dict of
        all jobs which are related to this freesite
        
        Keys in the dict are filenames (rel paths), or __manifest
        """
        jobs = {}
        self.node.refreshPersistentRequests()
        for job in self.node.getGlobalJobs():
            id = job.id
            idparts = id.split("|")
            if idparts[0] == 'freesitemgr' and idparts[1] == self.name:
                name = idparts[2]
                jobs[name] = job
        return jobs
    
    #@-node:readNodeQueue
    #@+node:createIndexAndSitemapIfNeeded
    def createIndexAndSitemapIfNeeded(self):
        """
        generate and insert an index.html if none exists
        """
        def genindexuri():
            # dumb hack - calculate uri if missing
            if not self.indexRec.get('uri', None):
                self.indexRec['uri'] = self.chkCalcNode.genchk(
                                       data=open(self.indexRec['path'], "rb").read(),
                                       mimetype=self.mtype,
                                       TargetFilename=ChkTargetFilename(self.index))
            # yes, remember its uri for the manifest
            self.indexUri = self.indexRec['uri']
            # flag if being inserted
            if self.indexRec['state'] != 'idle':
                self.insertingIndex = True
                self.save()

        def gensitemapuri():
            # dumb hack - calculate uri if missing
            if not self.sitemapRec.get('uri', None):
                self.sitemapRec['uri'] = self.chkCalcNode.genchk(
                                         data=open(self.sitemapRec['path'], "rb").read(),
                                         mimetype=self.mtype,
                                         TargetFilename=ChkTargetFilename(self.sitemap))
            # yes, remember its uri for the manifest
            self.sitemapUri = self.sitemapRec['uri']
        

        def createindex():
            # create an index.html with a directory listing
            title = "Freesite %s directory listing" % self.name,
            indexlines = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "<title>%s</title>" % title,
                "</head>",
                "<body>",
                "<h1>%s</h1>" % title,
                "This listing was automatically generated and inserted by freesitemgr",
                "<br><br>",
                #"<ul>",
                "<table cellspacing=0 cellpadding=2 border=0>",
                "<tr>",
                "<td><b>Size</b></td>",
                "<td><b>Mimetype</b></td>",
                "<td><b>Name</b></td>",
                "</tr>",
                ]
            
            for rec in self.files:
                size = getFileSize(rec['path'])
                mimetype = rec['mimetype']
                name = rec['name']
                indexlines.extend([
                    "<tr>",
                    "<td>%s</td>" % size,
                    "<td>%s</td>" % mimetype,
                    "<td><a href=\"%s\">%s</a></td>" % (name, name),
                    "</tr>",
                    ])
            
            indexlines.append("</table></body></html>\n")
            
            self.indexRec = {'name': self.index, 'state': 'changed'}
            self.generatedTextData[self.indexRec['name']] = "\n".join(indexlines)
            try:
                self.indexRec['sizebytes'] = len(
                    self.generatedTextData[self.indexRec['name']].encode("utf-8"))
            except UnicodeDecodeError:
                print("generated data:", self.generatedTextData[self.indexRec['name']])
                raise
            # needs no URI: is always in manifest.

        def createsitemap():
            # create a sitemap.html with a directory listing
            title = "Sitemap for %s" % self.name,
            lines = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "<title>%s</title>" % title,
                "</head>",
                "<body>",
                "<h1>%s</h1>" % title,
                "This listing was automatically generated and inserted by freesitemgr",
                "<br><br>",
                #"<ul>",
                "<table cellspacing=0 cellpadding=2 border=0>",
                "<tr>",
                "<td><b>Size</b></td>",
                "<td><b>Mimetype</b></td>",
                "<td><b>Name</b></td>",
                "</tr>",
                ]
            
            for rec in self.files:
                size = getFileSize(rec['path'])
                mimetype = rec['mimetype']
                name = rec['name']
                lines.extend([
                    "<tr>",
                    "<td>%s</td>" % size,
                    "<td>%s</td>" % str(mimetype), # TODO: check: mimetype for tar.b2 is a list?
                    "<td><a href=\"%s\">%s</a></td>" % (name, name),
                    "</tr>",
                    ])
            
            lines.append("</table>")
            
            # and add all keys 
            lines.extend([
                "<h2>Keys of large, separately inserted files</h2>",
                "<pre>"
                ])

            for rec in self.files:
                separate = 'target' in rec and rec['target'] == 'separate'
                if separate:
                    try:
                        uri = rec['uri']
                    except KeyError:
                        if 'path' in rec:
                            raw = open(rec['path'],"rb").read()
                            uri = self.chkCalcNode.genchk(
                                data=raw, 
                                mimetype=rec['mimetype'],
                                TargetFilename=ChkTargetFilename(rec['name']))
                            rec['uri'] = uri
                    lines.append(uri)
            lines.append("</pre></body></html>\n")
            
            self.sitemapRec = {'name': self.sitemap, 'state': 'changed', 'mimetype': 'text/html'}
            self.generatedTextData[self.sitemapRec['name']] = "\n".join(lines)
            raw = self.generatedTextData[self.sitemapRec['name']].encode("utf-8")
            self.sitemapRec['sizebytes'] = len(raw)
            self.sitemapRec['uri'] = self.chkCalcNode.genchk(
                data=raw, 
                mimetype=self.sitemapRec['mimetype'], 
                TargetFilename=ChkTargetFilename(self.sitemap))

        
        # got an actual index and sitemap file?
        self.indexRec = self.filesDict.get(self.index, None)
        self.sitemapRec = self.filesDict.get(self.sitemap, None)
        if self.indexRec and self.sitemapRec:
            genindexuri()
            gensitemapuri()
            return

        if self.indexRec:
            genindexuri()
        else:
            # we do not have a real index file and need to generate it.
            # FIXME: insertingindex is deprecated by including the index
            # in the manifest. Refactor to get rid of it.
            self.insertingIndex = True
            self.save()
            createindex()
        if self.sitemapRec:
            gensitemapuri()
        else:
            # we do not have a real sitemap file and need to generate it.
            createsitemap()
            # register the sitemap for upload.
            self.files.append(self.sitemapRec)
        
    
    #@-node:createIndexAndSitemapIfNeeded
    #@+node:allocId
    def allocId(self, name):
        """
        Allocates a unique ID for a given file
        """
        return "freesitemgr|%s|%s" % (self.name, name)
    
    #@-node:allocId
    #@+node:markManifestFiles
    def markManifestFiles(self):
        """
        Selects the files which should directly be put in the manifest and
        marks them with rec['target'] = 'manifest'. All other files
        are marked with 'separate'.
        
        Files are selected for the manifest until the manifest reaches 
        maxManifestSizeBytes based on the following rules:
        - index and activelink.png are always included
        - the first to include are CSS files referenced in the index, smallest first
        - then follow all other files referenced in the index, smallest first
        - then follow html files not referenced in the index, smallest first
        - then follow all other files, smallest first
        
        The manifest goes above the max size if that is necessary to avoid having more 
        than maxNumberSeparateFiles redirects.
        """
        # TODO: This needs to avoid spots which break freenet. If we
        # have very many small files, they should all be put into the
        # container. Maybe add a maximum number of files to insert
        # separately.
        
        #: The size of a redirect. See src/freenet/support/ContainerSizeEstimator.java
        redirectSize = 512
        #: The estimated size of the .metadata object. See src/freenet/support/ContainerSizeEstimator.java
        metadataSize = 128

        # check whether we have an activelink.
        for rec in self.files:
            if rec['name'] == self.index:
                self.indexRec = rec
            if rec['name'] == self.sitemap:
                self.sitemapRec = rec
            if rec['name'] == "activelink.png":
                self.activelinkRec = rec
        maxsize = self.maxManifestSizeBytes - redirectSize * len(self.files)
        totalsize = metadataSize
        # we add the index as first file, so it is always fast.
        self.indexRec['target'] = "manifest"
        totalsize += self.indexRec['sizebytes']
        maxsize += redirectSize # no redirect needed for this file
        # also we always add the activelink
        if self.activelinkRec and (self.activelinkRec['sizebytes'] + totalsize
                                   <= maxsize + redirectSize):
            self.activelinkRec['target'] = "manifest"
            totalsize = self.activelinkRec['sizebytes']
            maxsize += redirectSize # no redirect needed for this file
        # sort the files by filesize
        recBySize = sorted(self.files, key=lambda rec: rec['sizebytes'])
        # now we parse the index to see which files are directly
        # referenced from the index page. These should have precedence
        # over other files.
        try:
            indexText = self.generatedTextData[self.indexRec['name']]
        except KeyError:
            try:
                indexText = io.open(self.indexRec['path'], "r", encoding="utf-8").read()
            except UnicodeDecodeError:
                # no unicode file? Let io.open guess.
                try:
                    indexText = io.open(self.indexRec['path'], "r").read()
                except UnicodeDecodeError:
                    # almost final chance: replace errors.
                    try:
                        indexText = io.open(self.indexRec['path'], "r", encoding="utf-8", errors="xmlcharrefreplace").read()
                    except (TypeError, UnicodeDecodeError):
                        # truly final chance: just throw out errors. TODO: Use chardet: https://pypi.python.org/pypi/chardet
                        indexText = io.open(self.indexRec['path'], "r", encoding="utf-8", errors="ignore").read()
        # now resort the recBySize to have the recs which are
        # referenced in index first - with additional preference to CSS files.
        # For files outside the index, prefer html files before others.
        fileNamesInIndex = set([rec['name'] for rec in recBySize 
                                if rec['name'] in indexText])
        fileNamesInIndexCSS = set([rec['name'] for rec in recBySize 
                                   if rec['name'] in fileNamesInIndex 
                                   and rec['name'].lower().endswith('.css')])
        fileNamesInManifest = set()
        recByIndexAndSize = []
        recByIndexAndSize.extend(rec for rec in recBySize 
                                 if rec['name'] in fileNamesInIndexCSS)
        recByIndexAndSize.extend(rec for rec in recBySize 
                                 if rec['name'] in fileNamesInIndex
                                 and rec['name'] not in fileNamesInIndexCSS)
        recByIndexAndSize.extend(rec for rec in recBySize 
                                 if rec['name'] not in fileNamesInIndex
                                 and rec['name'].lower().endswith(".html"))
        recByIndexAndSize.extend(rec for rec in recBySize 
                                 if rec['name'] not in fileNamesInIndex
                                 and not rec['name'].lower().endswith(".html"))
        for rec in recByIndexAndSize:
            if rec is self.indexRec or rec is self.activelinkRec:
                rec['target'] = 'manifest'
                # remember this
                fileNamesInManifest.add(rec['name'])
                continue # we already added the size.
            if rec['sizebytes'] + totalsize <= maxsize + redirectSize:
                rec['target'] = 'manifest'
                totalsize += rec['sizebytes']
                maxsize += redirectSize # no redirect needed for this file
                # remember this
                fileNamesInManifest.add(rec['name'])
            else:
                rec['target'] = 'separate'
        # now add more small files to the manifest until less than
        # maxNumberSeparateFiles remain separate.
        separateRecBySize = [i for i in recBySize
                             if not i['name'] in fileNamesInManifest]
        numSeparate = len(separateRecBySize)
        filesToAdd = max(0, numSeparate - self.sitemgr.maxNumberSeparateFiles)
        for i in range(filesToAdd):
            rec = separateRecBySize[i]
            rec['target'] = 'manifest'
            totalsize += rec['sizebytes']
        
    
    #@-node:markManifestFiles
    #@+node:makeManifest
    def makeManifest(self):
        """
        Create a site manifest insertion command buffer from our
        current inventory
        """
        # build up a command buffer to insert the manifest
        self.manifestCmdId = self.allocId("__manifest")
    
        msgLines = ["ClientPutComplexDir",
                    "Identifier=%s" % self.manifestCmdId,
                    "Verbosity=%s" % self.Verbosity,
                    "MaxRetries=%s" % maxretries,
                    # lower by one to win against WoT. Avoids stalling site inserts.
                    "PriorityClass=%s" % max(0, int(self.priority) - 1), 
                    "URI=%s" % self.uriPriv,
                    "Persistence=forever",
                    "Global=true",
                    "DefaultName=%s" % self.index,
                    ]
        
        # add each file's entry to the command buffer
        n = 0
        default = None
        # cache DDA requests to avoid stalling for ages on big sites
        hasDDAtested = {}
        datatoappend = []

        def fileMsgLines(n, rec):
            if rec.get('target', 'separate') == 'separate':
                return [ # FIXME: rec['name'] can be str or bytes. Find out which one and why.
                    "Files.%d.Name=%s" % (n, (rec['name'] if isinstance(rec['name'], str) else rec['name'].decode("utf-8"))),
                    "Files.%d.UploadFrom=redirect" % n,
                    "Files.%d.TargetURI=%s" % (n, (rec['uri'] if isinstance(rec['uri'], str) else rec['uri'].decode("utf-8"))),
                ]
            # if the site should be part of the manifest, check for DDA
            if 'path' not in rec:
                hasDDA = False
            else:
                DDAdir = os.path.dirname(rec['path'])
                try:
                    hasDDA = hasDDAtested[DDAdir]
                except KeyError:
                    hasDDA = self.node.testDDA(Directory=DDAdir,
                                               WantReadDirectory=True, 
                                               WantWriteDirectory=False)
                    hasDDAtested[DDAdir] = hasDDA

            if hasDDA:
                if rec['name'] in self.generatedTextData:
                    sizebytes = len(self.generatedTextData[rec['name']].encode("utf-8"))
                else:
                    sizebytes = os.path.getsize(rec['path'])
                    rec['sizebytes'] = sizebytes
                    rec['dda'] = True
                return [
                    "Files.%d.Name=%s" % (n, rec['name']),
                    "Files.%d.UploadFrom=disk" % n,
                    "Files.%d.Filename=%s" % (n, rec['path']),
                ]
            else:
                if rec['name'] in self.generatedTextData:
                    data = self.generatedTextData[rec['name']].encode("utf-8")
                else:
                    data = open(rec['path'], "rb").read()
                datatoappend.append(data)
                # update the sizebytes from the data actually read here.
                rec['sizebytes'] = len(data)
                return [
                    "Files.%d.Name=%s" % (n, rec['name']),
                    "Files.%d.UploadFrom=direct" % n,
                    "Files.%d.DataLength=%s" % (n, rec['sizebytes']),
                ]

            
        # start with index.html's uri and the sitemap
        msgLines.extend(fileMsgLines(n, self.indexRec))
        n += 1
        msgLines.extend(fileMsgLines(n, self.sitemapRec))
        n += 1
    
        # now add the rest of the files, but not index.html
        # put files first which should be part of the manifest.
        manifestfiles = [r for r in self.files if r.get('target', 'separate') == 'manifest']
        separatefiles = [r for r in self.files if not r.get('target', 'separate') == 'manifest']
        # sort the manifestfiles by size
        manifestfiles = sorted(manifestfiles, key=lambda rec: rec['sizebytes'])
        for rec in manifestfiles + separatefiles:
            # skip index and sitemap: we already had them.
            if rec['name'] == self.index:
                rec['state'] = 'idle'
                # index is never inserted separately (anymore). FIXME:
                # Refactor to kill any instance of self.insertingIndex
                self.insertingIndex = False
                continue
            if rec['name'] == self.sitemap:
                rec['state'] = 'idle'
                continue
            # don't add if the file failed to insert
            if not rec['uri']:
                if not rec['target'] == 'manifest':
                    self.log(ERROR, "File %s has not been inserted" % rec['name'])
                    # raise Hell :) # bab: we don't actually want to do that. We want to continue.
                    continue
            # otherwise, ok to add
            msgLines.extend(fileMsgLines(n, rec))
            # note that the file does not need additional actions.
            rec['state'] = 'idle'
            # TODO: sum up sizes here to find the error due to which the files get truncated.
    
            # don't forget to up the count
            n += 1
        
        # finish the command buffer
        if datatoappend:
            msgLines.append("Data")
        else:
            msgLines.append("EndMessage")
    
        # and save
        self.manifestCmdBuf = b"\n".join(i.encode("utf-8") for i in msgLines) + b"\n"
        self.manifestCmdBuf += b"".join(datatoappend)
        datalength = len(b"".join(datatoappend))
        # FIXME: Reports an erroneous Error when no physical index is present.
        reportedlength = sum(rec['sizebytes'] for rec in self.files
                             if rec.get('target', 'separate') == 'manifest'
                             and rec.get('dda', False) == False)
        if self.indexRec not in self.files:
            reportedlength += self.indexRec['sizebytes']
        if datalength != reportedlength:
            self.log(ERROR, "The datalength of %s to be uploaded does not match the length reported to the node of %s. This is a bug, please report it to the pyFreenet maintainer." % (datalength, reportedlength))

    
    #@-node:makeManifest
    #@+node:fallbackLogger
    def fallbackLogger(self, level, msg):
        """
        This logger is used if no node FCP port is available
        """
        print(msg)
    
    #@-node:fallbackLogger
    #@-others

#@-node:class SiteState
#@+node:funcs
# utility funcs

#@+others
#@+node:getFileSize
def getFileSize(filepath):
    """
    Get the size of the file in bytes.
    """
    return os.stat(filepath)[stat.ST_SIZE]

#@-node:getFileSize
#@+node:fixUri
def fixUri(uri, name, version=0):
    """
    Conditions a URI to be suitable for freesitemgr
    """
    # step 1 - lose any 'freenet:'
    uri = uri.split("freenet:")[-1]
    
    # step 2 - convert SSK@ to USK@
    uri = uri.replace("SSK@", "USK@")
    
    # step 3 - lose the path info
    uri = uri.split("/")[0]
    
    # step 4 - attach the name and version
    uri = "%s/%s/%s" % (uri, name, version)
    
    return uri

#@-node:fixUri
#@+node:targetFilename
def ChkTargetFilename(name):
    """
    Make the name suitable for a ChkTargetFilename
    """
    return os.path.basename(name)

#@-node:targetFilename
#@+node:runTest
def runTest():
    
    mgr = SiteMgr(verbosity=DEBUG)
    mgr.insert()

#@-node:runTest
#@-others
#@-node:funcs
#@+node:mainline
if __name__ == '__main__':
    runTest()

#@-node:mainline
#@-others

#@-node:@file sitemgr.py
#@-leo
