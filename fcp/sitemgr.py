#@+leo-ver=4
#@+node:@file sitemgr.py
"""
new persistent SiteMgr class
"""

#@+others
#@+node:imports
import sys, os, threading, traceback, pprint, time, stat, sha

import fcp
from fcp import CRITICAL, ERROR, INFO, DETAIL, DEBUG, NOISY
from fcp.node import hashFile

#@-node:imports
#@+node:globals
defaultBaseDir = os.path.join(os.path.expanduser('~'), ".freesitemgr")

maxretries = -1

defaultMaxConcurrent = 10

testMode = False
#testMode = True

defaultPriority = 3

version = 1

minVersion = 0

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

        self.index = kw.get('index', 'index.html')
        self.mtype = kw.get('mtype', 'text/html')
        
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
            d = {}
            exec file(self.conffile).read() in d
            for k,v in d.items():
                setattr(self, k, v)
    
        # barf if configs are too old
        if getattr(self, 'version', 0) < minVersion:
            raise BadConfig(
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
        except:
            # limited functionality - no node
            self.node = None
            self.log = self.fallbackLogger
    
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
        f = file(self.conffile, "w")
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
            return filter(lambda s:s.name==name, self.sites)[0]
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
                print "---------------------------------------------------------------------"
                print "freesitemgr: updating site '%s' on %s" % (site.name, time.asctime())
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
            print
    
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
                    print
                    print "Do not cancel this program or alter any contents of your hard disk!"
                    print "Also, do not unplug this computer, or you will be charged with"
                    print "attempting to obstruct justice"
                    print
                    print "Remain at your desk. An agent will arrive at your door shortly"
                    print 
                    time.sleep(10)
                    print "Happy April 1 !"
                    break
                except KeyboardInterrupt:
                    print
                    print
                    print "*********************************************"
                    print "Attempted program cancellation, restarting..."
                    print
                    time.sleep(0.5)
    
    #@-node:securityCheck
    #@+node:fallbackLogger
    def fallbackLogger(self, level, msg):
        """
        This logger is used if no node FCP port is available
        """
        print msg
    
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
    
        self.kw = kw
    
        self.sitemgr = kw['sitemgr']
        self.node = self.sitemgr.node
    
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
            d = {}
            raw = file(self.path).read()
            try:
                exec raw in d
            except:
                traceback.print_exc()
                print "Error loading state file for site '%s' (%s)" % (
                    self.name, self.path)
                sys.exit(1)
        
            # execution succeeded, extract the data items
            for k,v in d.items():
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
                if not rec.has_key('id'):
                    needToSave = True
                    rec['id'] = None
                if not rec['id']:
                    rec['id'] = self.allocId(rec['name'])
                    needToSave = True
                if not rec.has_key('state'):
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
            f = file(tmpFile, "w")
            self.log(DETAIL, "save: writing to temp file %s" % tmpFile)
    
            pp = pprint.PrettyPrinter(width=72, indent=2, stream=f)
            
            w = f.write
    
            def writeVars(comment="", tail="", **kw):
                """
                Pretty-print a 'name=value' line, with optional tail string
                """
                if comment:
                    w("# " + comment + "\n")
                for name, value in kw.items():
                    w(name + " = ")
                    pp.pprint(value)
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
            writeVars(mtype=self.mtype)
            
            w("\n")
            writeVars("Detailed site contents", files=self.files)
    
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
                        "insert:%s: site is still inserting from before" % self.name)
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
        # select which files to insert, and get their CHKs
    
        # get records of files to insert    
        filesToInsert = filter(lambda r: r['state'] in ('changed', 'waiting'),
                               self.files)
        
        # compute CHKs for all these files, synchronously, and at the same time,
        # submit the inserts, asynchronously
        chkCounter = 0;
        for rec in filesToInsert:
            if rec['state'] == 'waiting':
                continue
            log(INFO, "Pre-computing CHK for file %s" % rec['name'])
            raw = file(rec['path'],"rb").read()
            uri = self.chkCalcNode.genchk(data=raw, mimetype=rec['mimetype'])
            rec['uri'] = uri
            rec['state'] = 'waiting'
    
            # get a unique id for the queue
            id = self.allocId(rec['name'])
    
            # and queue it up for insert, possibly on a different node
            raw = file(rec['path'], "rb").read()
            self.node.put(
                "CHK@",
                id=id,
                mimetype=rec['mimetype'],
                priority=self.priority,
                Verbosity=self.Verbosity,
                data=raw,
                async=True,
                chkonly=testMode,
                persistence="forever",
                Global=True,
                waituntilsent=True,
                maxretries=maxretries,
                )
            rec['state'] = 'inserting'
    
            chkCounter += 1;
            if( 0 == ( chkCounter % chkSaveInterval )):
                self.save()
            
        self.save()
    
        log(INFO, 
            "insert:%s: All CHK calculations for new/changed files complete" \
                 % self.name)
    
        # save here, in case user pulls the plug
        self.save()
    
        # ------------------------------------------------
        # may need to auto-generate an index.html
        self.createIndexIfNeeded()
    
        # -----------------------------------
        # create/insert manifest
        
        self.makeManifest()
        self.node._submitCmd(
            self.manifestCmdId, "ClientPutComplexDir",
            rawcmd=self.manifestCmdBuf,
            async=True,
            waituntilsent=True,
            keep=True,
            persistence="forever",
            Global="true",
            )
        
        self.updateInProgress = True
        self.insertingManifest = True
        self.save()
    
        # ----------------------------------
        # now insert each new/changed file to the global queue
    
        if 0:
            # now doing this as part of the chk precalc loop above
            for rec in filesToInsert:
            
                # get a unique id for the queue
                id = self.allocId(rec['name'])
        
                # and queue it up for insert
                raw = file(rec['path'], "rb").read()
                self.node.put(
                    "CHK@",
                    id=id,
                    mimetype=rec['mimetype'],
                    priority=self.priority,
                    Verbosity=self.Verbosity,
                    data=raw,
                    async=True,
                    chkonly=testMode,
                    persistence="forever",
                    Global=True,
                    waituntilsent=True,
                    maxretries=maxretries,
                    )
                rec['state'] = 'inserting'
    
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
            if not jobs.has_key("__manifest"):
                missing.append('__manifest')
            if self.insertingIndex and not jobs.has_key(self.index):
                missing.append(self.index)
            for rec in self.files:
                if rec['state'] == 'waiting' and not jobs.has_key(rec['name']):
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
            if rec:
                # that file is now done
                rec['uri'] = result
                rec['state'] = 'idle'
            elif name not in ['__manifest', self.index]:
                self.log(ERROR,
                         "insert:%s: Don't have a record for file %s" % (
                                    self.name, name))
        
        # now, make sure that all currently inserting files have a job on the queue
        for rec in self.files:
            if rec['state'] != 'inserting':
                continue
            if not queuedJobs.has_key(rec['name']):
                self.log(CRITICAL, "insert: node has forgotten job %s" % rec['name'])
                rec['state'] = 'waiting'
                self.needToUpdate = True
        
        # check for any uninserted files or manifests
        stillInserting = False
        for rec in self.files:
            if rec['state'] != 'idle':
                stillInserting = True
        if needToInsertIndex or needToInsertManifest:
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
    
        # scan the directory
        lst = fcp.node.readdir(self.dir)
    
        # convert records to the format we use
        physFiles = []
        physDict = {}
        for f in lst:
            rec = {}
            rec['name'] = f['relpath']
            rec['path'] = f['fullpath']
            rec['mimetype'] = f['mimetype']
            rec['hash'] = hashFile(rec['path'])
            rec['uri'] = ''
            rec['id'] = ''
            physFiles.append(rec)
            physDict[rec['name']] = rec
    
        # now, analyse both sets of records, and determine if update is needed
        
        # firstly, purge deleted files
        # also, pick up records without URIs, or which are already marked as changed
        for name, rec in self.filesDict.items():
            if not physDict.has_key(name):
                # file has disappeared, remove it and flag an update
                log(DETAIL, "scan: file %s has been removed" % name)
                del self.filesDict[name]
                self.files.remove(rec)
                structureChanged = True
            elif rec['state'] in ('changed', 'waiting'):
                structureChanged = True
            elif not rec.get('uri', None):
                structureChanged = True
                rec['state'] = 'changed'
        
        # secondly, add new/changed files
        for name, rec in physDict.items():
            if not self.filesDict.has_key(name):
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
                if knownrec['state'] in ('changed', 'waiting') \
                or knownrec['hash'] != rec['hash']:
                    # flag an update
                    log(DETAIL, "scan: file %s has changed" % name)
                    knownrec['hash'] = rec['hash']
                    knownrec['state'] = 'changed'
                    structureChanged = True
    
        # if structure has changed, gotta sort and save
        if structureChanged:
            self.needToUpdate = True
            self.files.sort(lambda r1,r2: cmp(r1['name'], r2['name']))
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
    #@+node:createIndexIfNeeded
    def createIndexIfNeeded(self):
        """
        generate and insert an index.html if none exists
        """
        # got an actual index file?
        indexRec = self.filesDict.get(self.index, None)
        if indexRec:
            # dumb hack - calculate uri if missing
            if not indexRec.get('uri', None):
                indexRec['uri'] = self.chkCalcNode.genchk(
                                    data=file(indexRec['path'], "rb").read(),
                                    mimetype=self.mtype)
                
            # yes, remember its uri for the manifest
            self.indexUri = indexRec['uri']
            
            # flag if being inserted
            if indexRec['state'] != 'idle':
                self.insertingIndex = True
                self.save()
            return
    
        # no, we have to create one
        self.insertingIndex = True
        self.save()
        
        # create an index.html with a directory listing
        title = "Freesite %s directory listing" % self.name,
        indexlines = [
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
            size = os.stat(rec['path'])[stat.ST_SIZE]
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
        raw = "\n".join(indexlines)
    
        # get its uri
        self.log(INFO, "Auto-Generated an index.html, calculating CHK...")
        self.indexUri = self.node.put(
            "CHK@",
            mimetype="text/html",
            priority=1,
            Verbosity=self.Verbosity,
            data=raw,
            async=False,
            chkonly=True,
            )
    
        # and insert it on global queue
        self.log(INFO, "Submitting auto-generated index.html to global queue")
        id = self.allocId("index.html")
        self.node.put(
            "CHK@",
            id=id,
            mimetype="text/html",
            priority=self.priority,
            Verbosity=self.Verbosity,
            data=raw,
            async=True,
            chkonly=testMode,
            persistence="forever",
            Global=True,
            waituntilsent=True,
            maxretries=maxretries,
            )
    
    #@-node:createIndexIfNeeded
    #@+node:allocId
    def allocId(self, name):
        """
        Allocates a unique ID for a given file
        """
        return "freesitemgr|%s|%s" % (self.name, name)
    
    #@-node:allocId
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
                    "PriorityClass=%s" % self.priority,
                    "URI=%s" % self.uriPriv,
                    "Persistence=forever",
                    "Global=true",
                    "DefaultName=%s" % self.index,
                    ]
    
        # add each file's entry to the command buffer
        n = 0
        default = None
    
        # start with index.html's uri
        msgLines.extend([
            "Files.%d.Name=%s" % (n, self.index),
            "Files.%d.UploadFrom=redirect" % n,
            "Files.%d.TargetURI=%s" % (n, self.indexUri),
            ])
        n += 1
    
        # now add the rest of the files, but not index.html
        for rec in self.files:
            if rec['name'] == self.index:
                continue
    
            # don't add if the file failed to insert
            if not rec['uri']:
                self.log(ERROR, "File %s has not been inserted" % rec['relpath'])
                raise Hell
                continue
    
            # otherwise, ok to add
            msgLines.extend([
                "Files.%d.Name=%s" % (n, rec['name']),
                "Files.%d.UploadFrom=redirect" % n,
                "Files.%d.TargetURI=%s" % (n, rec['uri']),
                ])
    
            # don't forget to up the count
            n += 1
        
        # finish the command buffer
        msgLines.append("EndMessage")
    
        # and save
        self.manifestCmdBuf = "\n".join(msgLines) + "\n"
    
    #@-node:makeManifest
    #@+node:fallbackLogger
    def fallbackLogger(self, level, msg):
        """
        This logger is used if no node FCP port is available
        """
        print msg
    
    #@-node:fallbackLogger
    #@-others

#@-node:class SiteState
#@+node:funcs
# utility funcs

#@+others
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
