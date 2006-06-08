#! /usr/bin/env python
"""
A small freesite insertion/management utility
"""
# standard lib imports
import sys, os, sha, traceback, getopt
from ConfigParser import SafeConfigParser

# fcp imports
import node
from node import FCPNode, guessMimetype
from node import SILENT, FATAL, CRITICAL, ERROR, INFO, DETAIL, DEBUG

fcpHost = node.defaultFCPHost
fcpPort = node.defaultFCPPort
#verbosity = DETAIL
verbosity = None
logfile = None

class SiteMgr:
    """
    Manages insertion and updating of freesites
    """
    def __init__(self, **kw):
        """
        Creates a site manager object.
        
        Arguments:
    
        Keywords:
            - configfile - pathname of where config file lives, defaults
              to ~/.freesites (or ~/freesites.ini on doze)
            - logfile - a pathname or open file object to which to write
              log messages, defaults to sys.stdout
            - verbosity - logging verbosity level, refer to fcp.node
            - fcphost - hostname of fcp, default fcp.node.defaultFCPHost
            - fcpport - port number of fcp, default fcp.node.defaultFCPPort
            - filebyfile - default False - if True, inserts files manually
              as chks, then builds a manifest full of redirects
            - allatonce - default False - if True, then enables multiple
              concurrent file inserts, up to the value of 'maxconcurrent'.
              Setting this True sets filebyfile to True as well
            - maxconcurrent - default 10 - if set, this also sets filebyfile
              and allatonce both to True. Value of maxconcurrent is the
              maximum number of concurrent inserts
            - insertall - default False - if set, reinserts all files whether
              they have changed or not. Otherwise, only inserts new or changed
              files
        """
        # set up the logger
        logfile = kw.pop('logfile', sys.stderr)
        if not hasattr(logfile, 'write'):
            # might be a pathname
            if not isinstance(logfile, str):
                raise Exception("Bad logfile, must be pathname or file object")
            logfile = file(logfile, "a")
        self.logfile = logfile
        self.verbosity = kw.get('verbosity', 0)
        self.Verbosity = kw.get('Verbosity', 0)
    
        #print "SiteMgr: verbosity=%s" % self.verbosity
    
        self.fcpHost = fcpHost
        self.fcpPort = fcpPort
    
        self.filebyfile = kw.get('filebyfile', False)
    
        if kw.has_key('allatonce'):
            self.allatonce = kw['allatonce']
            self.filebyfile = True
        else:
            self.allatonce = False
    
        if kw.has_key('maxconcurrent'):
            self.maxconcurrent = kw['maxconcurrent']
            self.filebyfile = True
            self.allatonce = True
        else:
            self.maxconcurrent = 10
    
        self.insertall = kw.get('insertall', False)
    
        self.kw = kw
    
        self.node = None
    
        # determine pathname for sites ini file
        configFile = kw.get('configfile', None)
        if configFile == None:
            isDoze = sys.platform.lower().startswith("win")
            homedir = os.path.expanduser("~")
            if isDoze:
                filename = "freesites.ini"
            else:
                filename = ".freesites"
            configFile = os.path.join(homedir, filename)
    
        self.configFile = configFile
    
        # a map of sitenames -> filesets
        self.siteManifests = {}
    
        if os.path.isfile(configFile):
            self.loadConfig()
        else:
            self.config = SafeConfigParser()
            self.config.set("DEFAULT", "fcphost", self.fcpHost)
            self.config.set("DEFAULT", "fcpport", str(self.fcpPort))
    def __del__(self):
    
        try:
            if hasattr(self, 'node'):
                self.node.shutdown()
            del self.node
            self.node = None
        except:
            pass
    
    def createConfig(self, **kw):
        """
        Creates a whole new config
        """
        #if not kw.has_key("fcpHost"):
        #    kw['fcpHost'] = node.defaultFCPHost
        #if not kw.has_key("fcpPort"):
        #    kw['fcpPort'] = node.defaultFCPPort
    
        #self.fcpHost = kw['fcpHost']
        #self.fcpPort = kw['fcpPort']
    
        file(self.configFile, "w").write("\n".join([
            "# config file for freesites",
            "# being inserted via pyfcp 'sitemgr' utility",
            "#",
            "# edit this file with care",
            "",
    #        "# FCP access details",
    #        "[DEFAULT]",
    #        "fcpHost=%s" % self.fcpHost,
    #        "fcpPort=%s" % self.fcpPort,
            "",
            "# for each new site, just copy the following two lines",
            "# to the end of this file, uncomment them, change as needed",
            "",
            "# [mysite]",
            "# dir=/path/to/mysite/directory",
            "",
            "",
            ]))
    
    def loadConfig(self):
        """
        Loads the sites config file into self.config as a SafeConfigParser
        object
        """
        conf = self.config = SafeConfigParser()
        conf.read(self.configFile)
    
        try:
            self.fcpHost = conf.get("DEFAULT", "fcphost")
        except:
            conf.set("DEFAULT", "fcphost", self.fcpHost)
        try:
            self.fcpPort = conf.getint("DEFAULT", "fcpport")
        except:
            conf.set("DEFAULT", "fcpport", str(self.fcpPort))
        
    
        manifests = self.siteManifests
    
        for sitename in conf.sections():
    
            if not conf.has_option(sitename, "dir"):
                raise Exception("Config file error: No directory specified for site '%s'" \
                                % sitename)
    
            # get or create a site record dict
            siterec = manifests.get(sitename, None)
            if not siterec:
                siterec = manifests[sitename] = {}
    
            # grab the manifests
            for name in conf.options(sitename):
                #print "name=%s" % name
                
                if name.startswith("files."):
                    # get or create a file record
                    _ignore, n, attr = name.split(".")
                    n = int(n)
                    val = conf.get(sitename, name)
    
                    filerec = siterec.get(n, None)
                    if not filerec:
                        filerec = siterec[n] = {}
                    filerec[attr] = val
                    
                    # now remove from section
                    conf.remove_option(sitename, name)
    
            # change the siterec to a dict of filename->uri 
            newrec = {}
            siteDir = conf.get(sitename, "dir")
            for rec in siterec.values():
                newrec[rec['relpath']] = {
                    'fullpath': os.path.join(siteDir, rec['relpath']),
                    'uri': rec['uri'],
                    'hash': rec['hash'],
                    'mimetype' : guessMimetype(rec['relpath']),
                    'changed' : False,
                    }
            manifests[sitename] = newrec
               
        #print manifests
    
    
    def saveConfig(self):
        """
        Saves the amended config file to disk
        """
        self.createConfig()
    
        self.config.set("DEFAULT", "fcphost", self.fcpHost)
        self.config.set("DEFAULT", "fcpport", str(self.fcpPort))
    
        f = file(self.configFile, "a")
    
        self.config.write(f)
    
        f.close()
    
    def createNode(self, **kw):
        """
        Creates and saves a node object, if one not already present
        """
        if isinstance(self.node, FCPNode):
            return
    
        opts = {}
    
        if kw.has_key("fcpHost"):
            opts['host'] = kw['fcpHost']
        else:
            opts['host'] = self.fcpHost
    
        if kw.has_key("fcpPort"):
            opts['port'] = self.fcpPort
        else:
            opts['port'] = self.fcpPort
    
        if kw.has_key("verbosity"):
            opts['verbosity'] = kw['verbosity']
        else:
            opts['verbosity'] = node.INFO
    
        opts['Verbosity'] = self.Verbosity
    
        if kw.has_key("logfile"):
            opts['logfile'] = kw['logfile'] or sys.stdout
        else:
            opts['logfile'] = sys.stdout
    
        opts['name'] = 'freesitemgr'
    
        #print "createNode:"
        #print "  kw=%s"% kw
        #print "  opts=%s" % opts
        #sys.exit(0)
        
        self.node = FCPNode(**opts)
    
    def hasSite(self, sitename):
        """
        returns True if site is known in this config
        """
        return self.config.has_section(sitename)
    
    def addSite(self, sitename, sitedir):
        
        if self.hasSite(sitename):
            raise Exception("Site %s already exists" % sitename)
    
        conf = self.config
        conf.add_section(sitename)
        conf.set(sitename, "dir", sitedir)
        
        self.saveConfig()
    
    def removeSite(self, sitename):
        """
        Drops a freesite from the config
        """
        if not self.hasSite(sitename):
            raise Exception("No such site '%s'" % sitename)
    
        conf = self.config
        conf.remove_section(sitename)
        
        self.saveConfig()
    
    def getSiteInfo(self, sitename):
        """
        returns a record of info about given site
        """
        if not self.hasSite(sitename):
            raise Exception("No such freesite '%s'" % sitename)
    
        conf = self.config
    
        if conf.has_option(sitename, "hash"):
            hash = conf.get(sitename, "hash")
        else:
            hash = None
        
        if conf.has_option(sitename, "version"):
            version = conf.getint(sitename, "version")
        else:
            version = None
    
        if conf.has_option(sitename, "privatekey"):
            privkey = conf.get(sitename, "privatekey")
        else:
            privkey = None
        
        if conf.has_option(sitename, "uri"):
            uri = conf.get(sitename, "uri")
        else:
            uri = None
    
        return {'name' : sitename,
                'dir' : conf.get(sitename, 'dir'),
                'hash' : hash,
                'version' : version,
                'privatekey' : privkey,
                'uri' : uri,
                }
    
    def getSiteNames(self):
        return self.config.sections()
    
    def update(self):
        """
        Insert/update all registered freesites
        """
        noSites = True
    
        log = self._log
    
        kw = self.kw
    
        # get a node handle
        self.createNode(logfile=logfile, **kw)
    
        conf = self.config
        for sitename in conf.sections():
            
            print "Updating site '%s'" % sitename
    
            # fill in any incomplete details with site entries
            needToSave = False
            if not conf.has_option(sitename, "hash"):
                needToSave = True
                conf.set(sitename, "hash", "")
    
            if not conf.has_option(sitename, "version"):
                needToSave = True
                conf.set(sitename, "version", "0")
    
            if not conf.has_option(sitename, "privatekey"):
                needToSave = True
                pub, priv = self.node.genkey()
                uri = pub.replace("SSK@", "USK@") + sitename + "/0"
                conf.set(sitename, "uri", uri)
                conf.set(sitename, "privatekey", priv)
    
            if needToSave:
                self.saveConfig()
    
            uri = conf.get(sitename, "uri")
            dir = conf.get(sitename, "dir")
            hash = conf.get(sitename, "hash")
            version = conf.get(sitename, "version")
            privatekey = conf.get(sitename, "privatekey")
            
            files = node.readdir(dir, gethashes=True)
    
            # get old manifest - dict of path->{'uri':uri, 'hash':hash} mappings
            siterec = self.siteManifests[sitename]
    
            #print "readdir files:"
            #print files
            #print "siterec files:"
            #print siterec
    
            # determine 'site hash'
            h = sha.new()
            for f in files:
                relpath = f['relpath']
                if siterec.has_key(relpath):
                    filerec = siterec[relpath]
                    filehash = f['hash']
                    if (filerec['hash'] != f['hash']) or self.insertall:
                        #print "File: %s" % relpath
                        #print "  oldhash=%s" % filerec['hash']
                        #print "  newhash=%s" % f['hash']
                        filerec['changed'] = True
                else:
                    # new file, create new record and mark as changed
                    #print "new file %s" % relpath
                    siterec[relpath] = {'uri':"",
                                        'hash':f['hash'],
                                        'changed':True,
                                        'fullpath': os.path.join(dir, relpath),
                                        'mimetype': guessMimetype(relpath),
                                        }
                h.update(f['hash'])
    
            # dump deleted files from siterec
            filenames = [f['relpath'] for f in files]
            for relpath in siterec.keys():
                if relpath not in filenames:
                    del siterec[relpath]
            
            hashNew = h.hexdigest()
    
            # don't insert site if it hasn't changed
            if (hashNew == hash) and not self.insertall:
                print "Site '%s' unchanged, skipping update" % sitename
            else:
                # site has changed, so better insert it
                log(INFO, "Updating site %s" % sitename)
                log(INFO, "privatekey=%s" % privatekey)
                noSites = False
                try:
                    res = self.node.put(privatekey,
                                        id="freesite:%s" % sitename,
                                        dir=dir,
                                        name=sitename,
                                        version=version,
                                        usk=True,
                                        verbosity=self.Verbosity,
                                        filebyfile=self.filebyfile,
                                        allatonce=self.allatonce,
                                        maxconcurrent=self.maxconcurrent,
                                        manifest=siterec,
                                        insertall=self.insertall)
        
                    print "Site '%s' updated successfully" % sitename
                except:
                    traceback.print_exc()
                    print "site '%s' failed to update" % sitename
    
            # update the site's global hash
            conf.set(sitename, "hash", hashNew)
    
            # and re-populate the manifest
            i = 0
            for relpath, attrdict in siterec.items():
                #print attrdict
                conf.set(sitename, "files.%d.relpath" % i, relpath)
                conf.set(sitename, "files.%d.uri" % i, attrdict['uri'])
                conf.set(sitename, "files.%d.hash" % i, attrdict['hash'])
                conf.set(sitename, "files.%d.mimetype" % i, attrdict['mimetype'])
                i += 1
    
        # save the updated config
        self.saveConfig()
    
        if noSites:
            log(INFO, "No sites needed updating")
    def shutdown(self):
        self.node.shutdown()
    
    def _log(self, level, msg):
        """
        Logs a message. If level > verbosity, don't output it
        """
        if level > self.verbosity:
            return
    
        if not msg.endswith("\n"): msg += "\n"
    
        self.logfile.write(msg)
        self.logfile.flush()
    

def help():

    print "%s: A console-based, cron-able freesite inserter" % sys.argv[0]
    print "That manages and inserts your freesites as USKs"
    print
    print "Usage: %s" % sys.argv[0]

    print "This utility inserts/updates freesites, and is"
    print "driven by a simple config file."
    print
    print "The first time you run this utility, a config file"
    print "will be created for you in your home directory,"
    print "You will be told where this file is (~/.freesites on *nix"
    print "or ~/freesites.ini on doze)"
    print "then you can edit this file and add details of"
    print "your freesites, and run it again."
    print
    print "Note - freesites are only updated if they have"
    print "changed since the last update, because a hash"
    print "of each site gets stored in the config"

    sys.exit(0)

def run():
    """
    Runs the sitemgr in a console environment
    """
    import getopt

    opts = {'verbosity': node.INFO,
            'host':xmlrpcHost,
            'port':xmlrpcPort,
            'fcpHost':node.defaultFCPHost,
            'fcpPort':node.defaultFCPPort,
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
        if o in ("-h", "--help"):
            usage(ret=0)
        elif o == "--host":
            opts['host'] = a
        elif o == "--port":
            opts['port'] = int(a)

if __name__ == '__main__':

    if '-h' in sys.argv:
        help()

    if '-v' in sys.argv:
        verbosity = node.DETAIL

    s = SiteMgr()
    s.update()
    s.shutdown()

