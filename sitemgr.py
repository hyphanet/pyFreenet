#! /usr/bin/env python
#@+leo-ver=4
#@+node:@file sitemgr.py
#@@first
"""
A small freesite insertion/management utility
"""
#@+others
#@+node:imports
import fcp, sys, os, sha

from ConfigParser import SafeConfigParser

#@-node:imports
#@+node:config
fcpHost = "thoth"
fcpPort = None
#verbosity = fcp.DETAIL
verbosity = None
logfile = None

#@-node:config
#@+node:class SiteMgr
class SiteMgr:
    """
    Manages insertion and updating of freesites
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, configFile=None, **kw):
        """
        Creates a site manager object.
        
        Arguments:
            - configFile - ini-format file containing site specifications,
              defaults to ~/.freesitesrc on *nix or ~/freesites.ini
        """
        # get a node handle
        self.createNode(**kw)
    
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
                
        self.loadConfig()
    
    #@-node:__init__
    #@+node:createConfig
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
    
    #@-node:createConfig
    #@+node:createNode
    def createNode(self, **kw):
    
        kw = {}
    
        if fcpHost and not kw.has_key("fcpHost"):
            kw['host'] = fcpHost
        if fcpPort and not kw.has_key("fcpPort"):
            kw['port'] = fcpPort
        if verbosity and not kw.has_key("verbosity"):
            kw['verbosity'] = verbosity
        if logfile and not kw.has_key("logfile"):
            kw['logfile'] = logfile
        
        self.node = fcp.FCPNodeConnection(**kw)
    
    #@-node:createNode
    #@+node:loadConfig
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
    
    #@-node:loadConfig
    #@+node:saveConfig
    def saveConfig(self):
        """
        Saves the amended config file to disk
        """
        self.createConfig()
    
        f = file(self.configFile, "a")
    
        self.config.write(f)
    
        f.close()
    
    #@-node:saveConfig
    #@+node:update
    def update(self):
        """
        Insert/update all registered freesites
        """
        noSites = True
    
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
                print "Updating site %s" % sitename
                print "privatekey=%s" % privatekey
                noSites = False
                self.node.put(privatekey, dir=dir, name=sitename, version=version, usk=True)
                conf.set(sitename, "hash", hashNew)
    
        self.saveConfig()
    
        if noSites:
            print "No sites needed updating"
    
    #@-node:update
    #@-others

#@-node:class SiteMgr
#@+node:mainline
if __name__ == '__main__':

    if '-v' in sys.argv:
        verbosity = fcp.DETAIL

    s = SiteMgr()
    s.update()

#@-node:mainline
#@-others
#@-node:@file sitemgr.py
#@-leo
