#@+leo-ver=4
#@+node:@file sitemgr.py
"""
new persistent SiteMgr class
"""

#@+others
#@+node:imports
import sys, os, threading, traceback, pprint, time, stat, sha

import fcp
from fcp import ERROR, INFO, DETAIL, DEBUG, NOISY
from fcp.node import hashFile

#@-node:imports
#@+node:globals
defaultBaseDir = os.path.join(os.path.expanduser('~'), ".freesitemgr")

maxretries = 3

defaultMaxConcurrent = 10

testMode = False
#testMode = True

defaultPriority = 3

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
            # skip the main config file, or emacs leftovers
            if f == ".config" or f.endswith("~"):
                continue
    
            # else it's a site, load it
            site = SiteState(
                name=f,
                basedir=self.basedir,
                node=self.node,
                priority=self.priority,
                maxconcurrent=self.maxConcurrent,
                Verbosity=self.Verbosity,
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
    
        site = SiteState(node=self.node,
                         maxconcurrent=self.maxConcurrent,
                         verbosity=self.verbosity,
                         Verbosity=self.Verbosity,
                         priority=self.priority,
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
    #@+node:insert
    def insert(self, name=None):
        """
        Inserts either named site, or all sites if no name given
        """
        if name == None:
            sites = self.sites
        else:
            sites = [self.getSite(name)]
        
        for site in sites:
            site.insert()
    
    #@-node:insert
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
            - node - a live FCPNode object, mandatory
            - basedir - directory where sitemgr files are stored, default
              is ~/.freesitemgr
            - name - name of freesite - mandatory
            - dir - directory of site on filesystem, mandatory
        
        If freesite doesn't exist, then a new state file will be created, from the
        optional keywords 'uriPub' and 'uriPriv'
        """
        self.kw = kw
    
        self.node = kw['node']
    
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
        
        #print "Verbosity=%s" % self.Verbosity
    
        self.fileLock = threading.Lock()
    
        # set a couple of defaults
        self.insertingManifest = False
        self.updateInProgress = False
    
        # get existing record, or create new one
        self.load()
        self.save()
    
        # barf if directory is invalid
        #if not (os.path.isdir(self.dir) \
        #        and os.path.isfile(os.path.join(self.dir, "index.html"))):
        #    raise Exception("Site %s, directory %s, no index.html present" % (
        #        self.name, self.dir))
        if not (os.path.isdir(self.dir)):
            raise Exception("Site %s, directory %s nonexistent" % (
                self.name, self.dir))
    
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
    
            f = file(self.path, "w")
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
            
            w("\n")
            writeVars("Detailed site contents", files=self.files)
        
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
        for name, rec in self.filesDict.items():
            if not physDict.has_key(name):
                # file has disappeared, remove it and flag an update
                log(DETAIL, "scan: file %s has been removed" % name)
                del self.filesDict[name]
                self.files.remove(rec)
                self.updateInProgress = True
                structureChanged = True
        
        # secondly, add new/changed files
        for name, rec in physDict.items():
            if not self.filesDict.has_key(name):
                # new file - add it and flag update
                log(DETAIL, "scan: file %s has been added" % name)
                #rec['uri'] = '' # kill the uri so it has to insert
                self.files.append(rec)
                rec['state'] = 'changed'
                self.filesDict[name] = rec
                self.updateInProgress = True
                structureChanged = True
            else:
                # known file - see if hash has changed
                knownrec = self.filesDict[name]
                if knownrec['hash'] != rec['hash']:
                    # hashes have changed, flag an update
                    log(DETAIL, "scan: file %s has changed" % name)
                    knownrec['hash'] = rec['hash']
                    knownrec['uri'] = '' # kill the uri so it has to insert
                    knownrec['state'] = 'changed'
                    self.updateInProgress = True
                    structureChanged = True
    
        # if structure has changed, gotta sort and save
        if structureChanged:
            self.files.sort(lambda r1,r2: cmp(r1['name'], r2['name']))
            self.save()
            self.log(INFO, "scan: site %s has changed" % self.name)
        else:
            self.log(INFO, "scan: site %s has not changed" % self.name)
    
    #@-node:scan
    #@+node:insert
    def insert(self):
        """
        Performs insertion of this site, or gets as far as
        we can, saving along the way so we can later resume
        """
        #@    <<check status>>
        #@+node:<<check status>>
        # --------------------------------------------
        # check global queue, and update insert status
        
        self.node.refreshPersistentRequests()
        
        needToSave = False
        filesOutstanding = False
        
        for job in self.node.getGlobalJobs():
        
            # get file rec, if any (could be __manifest)
            parts = job.id.split("|")
            if parts[0] != 'freesitemgr':
                # that's not our job - ignore it
                continue
            if parts[1] != self.name:
                # not our site - ignore it
                continue
        
            name = parts[2]
        
            rec = self.filesDict.get(name, None)
            
            #print "insert: job id=%s, rec=%s" % (job.id, rec)
        
            if job.isComplete():
        
                # kick it off the global queue
                self.node.clearGlobalJob(job.id)
        
                # was the job successful?
                result = job.result
                if isinstance(result, str):
        
                    needToSave = True
        
                    # yes, got a uri result
                    id = job.id
                    if id == self.allocId("__manifest"):
                        self.insertingManifest = False
                    else:
                        if rec:
                            rec['uri'] = result
                            rec['state'] = 'idle'
                        else:
                            self.log(ERROR, "insert:%s: Don't have a record for file %s" % (
                                                self.name, name))
        
        if self.updateInProgress:
        
            filesOutstanding = self.insertingManifest
        
            # check for any uninserted files or manifests
            for rec in self.files:
                if rec['state'] != 'idle':
                    filesOutstanding = True
        
        # is insert finally complete?
        if not filesOutstanding:
            # yes
            if self.updateInProgress:
                self.updateInProgress = False
                self.log(ERROR, "Insert of site %s completed successfully" % self.name)
                self.save()
                return
        
        if needToSave:
            self.save()
        
        # bail if still outstanding files
        if self.updateInProgress:
            self.log(ERROR, "insert: site %s is still inserting from before" % self.name)
            return
        
        #@-node:<<check status>>
        #@nl
    
        #@    <<skip if updating>>
        #@+node:<<skip if updating>>
        # -----------------------------------------
        # skip insert, if site is already updating
        
        if self.updateInProgress:
            self.log(INFO, "insert: freesite %s update still in progress from last time" \
                             % self.name)
        
        #@-node:<<skip if updating>>
        #@nl
    
        #@    <<need update?>>
        #@+node:<<need update?>>
        # -------------------------------------
        # does this site need an update?
        
        # compare our representation to what's on disk
        self.scan()
        
        # containers to keep track of file inserts
        waiting = []
        pending = []
        done = []
        failures = []
        
        # bail if site is already up to date
        if not self.updateInProgress:
            self.log(ERROR, "insert:%s: No update required" % self.name)
            return
        #@-node:<<need update?>>
        #@nl
    
        self.log(ERROR, "insert:%s: Updating..." % self.name)
    
        #@    <<class JobHandler>>
        #@+node:<<class JobHandler>>
        lock = threading.Lock()
        
        # a little class to help manage asynchronous job completion
        class JobHandler:
            
            def __init__(inst, rec):
                
                inst.rec = rec
        
            def __call__(inst, result, value):
        
                rec = inst.rec
        
                lock.acquire()            
        
                if result == 'failed':
                    pending.remove(rec)
                    failures.append(rec)
                    self.node.clearGlobalJob(rec['id'])
        
                elif result == 'successful':
                    # the 'value' will be the insert uri
                    rec['uri'] = value
                    pending.remove(rec)
                    done.append(rec)
                    self.node.clearGlobalJob(rec['id'])
        
                    # save state now
                    self.save()
        
                lock.release()
        
        #@-node:<<class JobHandler>>
        #@nl
    
        #@    <<select files to insert>>
        #@+node:<<select files to insert>>
        # ------------------------------------------------
        # select which files to insert, get their CHKs
        
        # stick all records without uris into the inbox
        waiting.extend(filter(lambda r: not r['uri'], self.files))
        
        # compute CHKs for all these jobs, asynchronous
        chkJobs = {}
        for rec in waiting:
            raw = file(rec['path'],"rb").read()
            job = self.node.genchk(data=raw, mimetype=rec['mimetype'], async=True)
            job.rec = rec
            chkJobs[rec['name']] = job
        
        # wait for all these asynchronous jobs to complete
        while chkJobs:
            for name,job in chkJobs.items():
                if job.isComplete():
                    job.rec['uri'] = job.result
                    del chkJobs[name]
            time.sleep(1)
        
        #@-node:<<select files to insert>>
        #@nl
    
        #@    <<create index.html?>>
        #@+node:<<create index.html?>>
        # ------------------------------------------
        # generate an index.html if none exists
        
        try:
            indexHtmlRec = self.getFile("index.html")
            needToInsertIndex = False
        except:
            indexHtmlRec = None
            needToInsertIndex = True
        
        if not indexHtmlRec:
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
            #file("%s/index.html" % tmpDir, "w").write(indexhtml)
        
            # now enqueue the insert
            indexHtmlRec = {
                'name':'index.html',
                'uri':'', 'mimetype':'text/html',
                'id': self.allocId("index.html"),
                }
            pending.append(indexHtmlRec)
            
        #@-node:<<create index.html?>>
        #@nl
    
        #@    <<create manifest>>
        #@+node:<<create manifest>>
        # -----------------------------------
        # create/insert manifest
        
        self.makeManifest(indexHtmlRec, waiting)
        manifestRec = {'name':'__manifest', 'uri':'', 'id':self.allocId("__manifest")}
        pending.append(manifestRec)
        hdlr = JobHandler(manifestRec)
        
        self.insertingManifest = True
        self.save()
        
        #@-node:<<create manifest>>
        #@nl
    
        #@    <<reset uris and save>>
        #@+node:<<reset uris and save>>
        # ----------------------------------------
        # wipe the URIs of files needing insertion
        
        #print waiting
        #sys.exit(0)
        
        for rec in waiting:
            rec['uri'] = ''
        self.save()
        
        #@-node:<<reset uris and save>>
        #@nl
    
        #@    <<insert index.html>>
        #@+node:<<insert index.html>>
        # ---------------------------------------
        # insert our generated index.html
        
        if needToInsertIndex:
            
            # get a callback handler
            hdlr = JobHandler(indexHtmlRec)
            
            # and queue it up for insert
            self.node.put(
                "CHK@",
                id=indexHtmlRec['id'],
                mimetype=indexHtmlRec['mimetype'],
                priority=self.priority,
                Verbosity=self.Verbosity,
                data=raw,
                async=True,
                chkonly=testMode,
                #callback=hdlr,
                persistence="forever",
                Global=True,
                )
        
        #@-node:<<insert index.html>>
        #@nl
        
        #@    <<insert manifest>>
        #@+node:<<insert manifest>>
        # ---------------------------------------
        # dispatch the manifest insertion
        
        self.node._submitCmd(
            self.manifestCmdId, "ClientPutComplexDir",
            rawcmd=self.manifestCmdBuf,
            async=True,
            #callback=hdlr,
            )
        
        #@-node:<<insert manifest>>
        #@nl
    
        #@    <<insert files>>
        #@+node:<<insert files>>
        # ----------------------------------
        # now do the file insertions, and
        # await their completion
        
        # total number of jobs
        ntotal = len(waiting) + len(pending)
        
        for rec in waiting:
        
            # get a callback handler
            id = self.allocId(rec['name'])
            hdlr = JobHandler(rec)
            
            # and queue it up for insert
            raw = file(rec['path'], "rb").read()
            job = self.node.put(
                "CHK@",
                id=id,
                mimetype=rec['mimetype'],
                priority=self.priority,
                Verbosity=self.Verbosity,
                data=raw,
                async=True,
                chkonly=testMode,
                #callback=hdlr,
                persistence="forever",
                Global=True,
                )
            job.waitTillReqSent()
        
        # and loop around, shuffling from inbox
        #lastProgressTime = 0
        #while True:
        if 0:
            
            lock.acquire()
            nwaiting = len(waiting)
            npending = len(pending)
            ndone = len(done)
            nfailures = len(failures)
            lock.release()
            
            # print a report if due
            now = time.time()
            if now - lastProgressTime > 10:
                lastProgressTime = now
                self.log(
                    INFO,
                    "insert:%s: waiting=%s pending=%s done=%s failed=%s total=%s" \
                        % (self.name, nwaiting, npending, ndone, nfailures, ntotal))
        
            # can bail here if done
            if nwaiting + npending == 0:
                break
        
            # add jobs if we have slots
            freeSlots = self.maxConcurrent - npending
        
            if freeSlots and waiting:
                try:
                    lock.acquire()
                    for i in xrange(freeSlots):
                        # move a rec from waiting to pending
                        if not waiting:
                            break
                        rec = waiting.pop(0)
                        pending.append(rec)
                        
                        # get a callback handler
                        id = self.allocId(rec['name'])
                        hdlr = JobHandler(rec)
                        
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
                            #callback=hdlr,
                            persistence="forever",
                            Global=True,
                            )
        
                finally:
                    lock.release()
        
            # and doze off for a bit
            time.sleep(2)
        #@nonl
        #@-node:<<insert files>>
        #@nl
    
    
        # and mark site as up to date
        #self.updateInProgress = False
        #self.save()
        #self.log(INFO, "Site %s updated" % self.name)
        #self.log(INFO, "=> %s" % indexHtmlRec['uri'])
        #return indexHtmlRec['uri']
    
        self.log(INFO, "Site %s inserting now on global queue" % self.name)
    
        # done
    
    #@-node:insert
    #@+node:allocId
    def allocId(self, name):
        """
        Allocates a unique ID for a given file
        """
        return "freesitemgr|%s|%s" % (self.name, name)
    
    #@-node:allocId
    #@+node:makeManifest
    def makeManifest(self, indexHtmlRec=None, fileset=None):
        """
        Create a site manifest insertion command buffer from our
        current inventory
        """
        # fileset defaults to self.files
        if not fileset:
            fileset = self.files
    
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
                    "DefaultName=index.html",
                    ]
    
        # add each file's entry to the command buffer
        n = 0
        default = None
    
        # add supplied index.html rec if any
        if indexHtmlRec:
            msgLines.extend([
                "Files.%d.Name=index.html" % n,
                "Files.%d.UploadFrom=redirect" % n,
                "Files.%d.TargetURI=%s" % (n, indexHtmlRec['uri']),
                ])
            n += 1
    
        for filerec in fileset:
            relpath = filerec['name']
            fullpath = filerec['path']
            uri = filerec['uri']
            mimetype = filerec['mimetype']
        
            # don't add if the file failed to insert
            if not uri:
                self.log(ERROR, "File %s has not been inserted" % relpath)
                raise Hell
                continue
        
            msgLines.extend([
                "Files.%d.Name=%s" % (n, relpath),
                "Files.%d.UploadFrom=redirect" % n,
                "Files.%d.TargetURI=%s" % (n, uri),
                ])
    
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
