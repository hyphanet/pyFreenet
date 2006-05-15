#! /usr/bin/env python
"""
A small freesite insertion/management utility
"""
import fcp, sys, os, sha, traceback

# get log level constants
from fcp import SILENT, FATAL, CRITICAL, ERROR, INFO, DETAIL, DEBUG

from ConfigParser import SafeConfigParser

fcpHost = "thoth"
fcpPort = None
#verbosity = fcp.DETAIL
verbosity = None
logfile = None

class SiteMgr:
    """
    Manages insertion and updating of freesites
    """
    def __init__(self, configFile=None, **kw):
        """
        Creates a site manager object.
        
        Arguments:
            - configFile - ini-format file containing site specifications,
              defaults to ~/.freesitesrc on *nix or ~/freesites.ini
    
        Keywords:
            - logfile - a pathname or open file object to which to write
              log messages, defaults to sys.stdout
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
    
        # get a node handle
        self.createNode(logfile=logfile, **kw)
    
        # determine pathname for sites ini file
        if configFile == None:
            isDoze = sys.platform.lower().startswith("win")
            homedir = os.path.expanduser("~")
            if isDoze:
                filename = "freesites.ini"
            else:
                filename = ".freesites"
            configFile = os.path.join(homedir, filename)
    
        self.configFile = configFile
    
        if not os.path.isfile(configFile):
            self.createConfig()
            self._log(CRITICAL, "New config file created at %s" % configFile)
            self._log(CRITICAL, "Please edit that file and add your freesites")
                
        self.loadConfig()
    
    def __del__(self):
    
        try:
            if hasattr(self, 'node'):
                self.node.shutdown()
            del self.node
            self.node = None
        except:
            pass
    
    def createConfig(self):
        """
        Creates a whole new config
        """
        file(self.configFile, "w").write("\n".join([
            "# config file for freesites",
            "# being inserted via pyfcp 'sitemgr' utility",
            "#",
            "# edit this file with care",
            "",
            "# ignore this, it's not used",
            "[DEFAULT]",
            "",
            "# for each new site, just take a copy of the following",
            "# 2 lines, uncomment them and change as needed",
            "",
            "# [mysite]",
            "# dir=/path/to/mysite/directory",
            "",
            "",
            ]))
    
    def createNode(self, **kw):
    
        #kw = {}
    
        if fcpHost and not kw.has_key("fcpHost"):
            kw['host'] = fcpHost
        if fcpPort and not kw.has_key("fcpPort"):
            kw['port'] = fcpPort
        if verbosity and not kw.has_key("verbosity"):
            kw['verbosity'] = verbosity
        if logfile and not kw.has_key("logfile"):
            kw['logfile'] = logfile
    
        #print kw
        
        self.node = fcp.FCPNodeConnection(**kw)
    
    def loadConfig(self):
        """
        Loads the sites config file into self.config as a SafeConfigParser
        object
        """
        conf = self.config = SafeConfigParser()
        conf.read(self.configFile)
    
        needToSave = False
    
        # fill in any incomplete details with site entries
        for sitename in conf.sections():
    
            if not conf.has_option(sitename, "dir"):
                raise Exception("Config file error: No directory specified for site '%s'" \
                                % sitename)
    
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
    
    def saveConfig(self):
        """
        Saves the amended config file to disk
        """
        self.createConfig()
    
        f = file(self.configFile, "a")
    
        self.config.write(f)
    
        f.close()
    
    def update(self):
        """
        Insert/update all registered freesites
        """
        noSites = True
    
        log = self._log
    
        conf = self.config
        for sitename in conf.sections():
            uri = conf.get(sitename, "uri")
            dir = conf.get(sitename, "dir")
            hash = conf.get(sitename, "hash")
            version = conf.get(sitename, "version")
            privatekey = conf.get(sitename, "privatekey")
            
            files = fcp.readdir(dir, gethashes=True)
            h = sha.new()
            for f in files:
                h.update(f['hash'])
            hashNew = h.hexdigest()
            if hashNew != hash:
                log(INFO, "Updating site %s" % sitename)
                log(INFO, "privatekey=%s" % privatekey)
                noSites = False
                try:
                    res = self.node.put(privatekey,
                                        dir=dir,
                                        name=sitename,
                                        version=version,
                                        usk=True)
                    log(INFO, "site %s updated successfully" % sitename)
                except:
                    traceback.print_exc()
                    log(ERROR, "site %s failed to update" % sitename)
                conf.set(sitename, "hash", hashNew)
    
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

if __name__ == '__main__':

    if '-h' in sys.argv:
        help()

    if '-v' in sys.argv:
        verbosity = fcp.DETAIL

    s = SiteMgr()
    s.update()
    s.shutdown()

