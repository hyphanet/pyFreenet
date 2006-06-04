#! /usr/bin/env python
#@+leo-ver=4
#@+node:@file freedisk.py
#@@first
#@@language python
#@+others
#@+node:freedisk app
"""
freedisk is a command-line utility for creating,
mounting and synchronising freenet freedisks

Invoke with -h for help
"""
#@+others
#@+node:imports
import sys, os
import getopt
import traceback
import time
import sha
import getpass

try:
    import fcp
    from fcp import node, freenetfs
    from fcp.xmlobject import XMLFile, XMLNode
except:
    print "** PyFCP core module 'fcp' not installed."
    print "** Please refer to the INSTALL file within the PyFCP source package"
    sys.exit(1)

try:
    import SSLCrypto


except:
    SSLCrypto = None
    print "** WARNING! SSLCrypto module not installed"
    print "** Please refer to the INSTALL file within the PyFCP source package"

#@-node:imports
#@+node:globals
# args shorthand
argv = sys.argv
argc = len(argv)
progname = argv[0]

# default config file stuff
homedir = os.path.expanduser("~")
configFile = os.path.join(homedir, ".freediskrc")

defaultMountpoint = os.path.join(homedir, "freedisk")

#@-node:globals
#@+node:class FreediskMgr
class FreediskMgr:
    """
    Freedisk manager class
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, *args, **kw):
    
        self.args = args
        self.kw = kw
    
        configFile = self.configFile = kw['configFile']
        conf = self.conf = FreediskConfig(configFile)
        #ipython(conf)
    
    
        # validate args
        nargs = len(args)
        if nargs == 0:
            usage("No command given")
    
        cmd = self.cmd = args[0]
        
        # barf if not 'init' and no config
        if cmd != 'init' and not os.path.isfile(configFile):
            usage("Config file %s does not exist\nRun '%s init' to create it" % (
                configFile, progname))
        
        # validate args count for cmds needing diskname arg
        if cmd in ['new', 'add', 'del', 'update', 'commit']:
            if nargs < 2:
                usage("%s: Missing argument <freediskname>" % cmd)
            diskname = self.diskname = args[1]
        
            # get paths to freedisk dir and pseudo-files
            self.diskPath = os.path.join(conf.mountpoint, "usr", diskname)
            self.pubKeyPath = os.path.join(self.diskPath, ".publickey")
            self.privKeyPath = os.path.join(self.diskPath, ".privatekey")
            self.passwdPath = os.path.join(self.diskPath, ".passwd")
            self.cmdPath = os.path.join(self.diskPath, ".cmd")
            self.statusPath = os.path.join(self.diskPath, ".status")
    
        # implement command synonyms
        self.cmd_setup = self.cmd_init
        self.cmd_mount = self.cmd_start
        self.cmd_unmoutn = self.cmd_umount = self.cmd_stop
        
    #@-node:__init__
    #@+node:execute
    def execute(self):
        """
        Executes the given command
        """
        cmd = self.cmd
        method = getattr(self, "cmd_"+cmd, None)
        if not method:
            usage("Unrecognised command '%s'" % cmd)
        
        return method(*self.args[1:])
    
    #@-node:execute
    #@+node:cmd_init
    def cmd_init(self, *args):
    
        conf = self.conf
    
        # initialise/change freedisk config
        
        print "Freedisk configuration"
        print
        print "Your freedisk config will normally be stored in the file:"
        print "  %s" % self.configFile
        
        # allow password change
        if conf.passwd:
            # got a password already
            prmt = "Do you wish to change your config password"
        else:
            # new password
            prmt = "Do you wish to encrypt this file"
        if getyesno(prmt):
            passwd = getpasswd("New Password", True)
            conf.setPassword(passwd)
            print "Password successfully changed"
        
        # host parms
        fcpHost = raw_input("Freenet FCP Hostname: [%s] " % conf.fcpHost).strip()
        if fcpHost:
            conf.fcpHost = fcpHost
        
        fcpPort = raw_input("Freenet FCP Port: [%s] "%  conf.fcpPort).strip()
        if fcpPort:
            conf.fcpPort = fcpPort
        
        print "Freenet verbosity:"
        print "  (0=SILENT, 1=FATAL, 2=CRITICAL, 3=ERROR"
        print "   4=INFO, 5=DETAIL, 6=DEBUG)"
        v = raw_input("[%s] " % conf.fcpVerbosity).strip()
        if v:
            conf.fcpVerbosity = v
        
        while 1:
            m = raw_input("Mountpoint [%s] " % conf.mountpoint).strip() \
                or conf.mountpoint
            if m:
                if not os.path.isdir(m):
                    print "No such directory '%s'" % m
                elif not os.path.exists(m):
                    print "%s is not a directory" % m
                else:
                    conf.mountpoint = m
                    mountpoint = m
                    break
        
        print "Freedisk configuration successfully changed"
        
    #@-node:cmd_init
    #@+node:cmd_start
    def cmd_start(self, *args):
    
        print "starting freedisk service..."
        fs = freenetfs.FreenetFS(
                conf.mountpoint,
                fcpHost=conf.fcpHost,
                fcpPort=conf.fcpPort,
                verbosity=conf.fcpVerbosity,
                debug=debug,
                multithreaded=multithreaded,
                )
        
        # spawn a process to run it
        if os.fork() == 0:
            print "Mounting freenet fs at %s" % conf.mountpoint
            fs.run()
        else:
            # parent process
            keyDir = os.path.join(conf.mountpoint, "keys")
            print "Waiting for disk to come up..."
            while not os.path.isdir(keyDir):
                time.sleep(1)
            disks = conf.getDisks()
        
            if disks:
                print "Freenetfs now mounted, adding existing disks..."
            else:
                print "Freenetfs now mounted, no freedisks at present"
        
            for disk in disks:
        
                diskPath = os.path.join(conf.mountpoint, "usr", disk.name)
        
                # barf if a freedisk of that name is already mounted
                if os.path.exists(diskPath):
                    usage("Freedisk %s seems to be already mounted" % disk.name)
                
                # mkdir to create the freedisk dir
                os.mkdir(diskPath)
        
                pubKeyPath = os.path.join(diskPath, ".publickey")
                privKeyPath = os.path.join(diskPath, ".privatekey")
                passwdPath = os.path.join(diskPath, ".passwd")
        
                # wait for the pseudo-files to come into existence
                while not os.path.isfile(privKeyPath):
                    time.sleep(0.1)
        
                # set the key and password
                file(pubKeyPath, "w").write(disk.uri)
                file(privKeyPath, "w").write(disk.privUri)
                file(passwdPath, "w").write(disk.passwd)
                
        
    #@nonl
    #@-node:cmd_start
    #@+node:cmd_stop
    def cmd_stop(self, *args):
        """
        Unmount the freenetfs
        """
        os.system("umount %s" % self.conf.mountpoint)
    
    #@-node:cmd_stop
    #@+node:cmd_new
    def cmd_new(self, *args):
        """
        Creates a new freedisk with a random key
        """
        #print "new: %s: NOT IMPLEMENTED" % diskname
        
        conf = self.conf
        diskname = self.diskname
        diskPath = self.diskPath
    
        if os.path.exists(diskPath):
            usage("Freedisk %s seems to be already mounted" % diskname)
        
        # get a password if desired
        passwd = getpasswd("Encrypt disk with password", True)
        
        # get a new private key
        keyDir = os.path.join(conf.mountpoint, "keys")
        if not os.path.isdir(keyDir):
            print "No keys directory %s" % keyDir
            print "Is your freenetfs mounted?"
            usage("Freenetfs not mounted")
        keyName = "freedisk_%s_%s" % (diskname, int(time.time()*1000000))
        keyPath = os.path.join(keyDir, keyName)
        
        keys = file(keyPath).read().strip().split("\n")
        pubKey, privKey = [k.split("/")[0].split("freenet:")[-1] for k in keys]
        
        # mkdir to create the freedisk dir
        os.mkdir(diskPath)
        
        # wait for the pseudo-files to come into existence
        while not os.path.isfile(privKeyPath):
            time.sleep(0.1)
        
        #status("About to write to %s" % privKeyPath)
        
        file(self.pubKeyPath, "w").write(pubKey)
        file(self.privKeyPath, "w").write(privKey)
        file(self.passwdPath, "w").write(passwd)
        
        # and, of course, update config
        conf.addDisk(diskname, pubKey, privKey, passwd)
        
        
    #@nonl
    #@-node:cmd_new
    #@+node:cmd_add
    def cmd_add(self, *args):
    
        nargs = len(args)
    
        # get uri
        if nargs < 3:
            usage("add: Missing URI")
        uri = args[1]
    
        #print "add: %s: NOT IMPLEMENTED" % diskname
        
        # barf if a freedisk of that name is already mounted
        if os.path.exists(self.diskPath):
            usage("Freedisk %s seems to be already mounted" % diskname)
        
        # mkdir to create the freedisk dir
        os.mkdir(self.diskPath)
        
        # wait for the pseudo-files to come into existence
        while not os.path.isfile(self.privKeyPath):
            time.sleep(0.1)
        
        # set the keys
        
        if fcp.node.uriIsPrivate(uri):
            path = privKeyPath
        else:
            path = pubKeyPath
        f = file(path, "w")
        f.write(uri)
        f.flush()
        f.close()
        
        
    #@nonl
    #@-node:cmd_add
    #@+node:cmd_del
    def cmd_del(self, *args):
        """
        unmounts a freedisk
        """
        conf = self.conf
        diskname = self.diskname
    
        disk = conf.getDisk(diskname)
        
        if not isinstance(disk, XMLNode):
            usage("No such disk '%s'" % diskname)
        
        conf.delDisk(diskname)
        
        path = os.path.join(conf.mountpoint, "usr", diskname)
        os.rmdir(path)
    
    #@-node:cmd_del
    #@+node:cmd_update
    def cmd_update(self, *args):
        """
        Updates a freedisk *from* freenet
        """
        cmdPath = self.cmdPath
        diskname = self.diskname
    
        print "update: %s: NOT IMPLEMENTED" % diskname
        
        f = file(cmdPath, "w")
        f.write("update")
        f.flush()
        f.close()
    
    #@-node:cmd_update
    #@+node:cmd_commit
    print "commit: %s: launching.." % diskname
    
    f = file(cmdPath, "w")
    f.write("commit")
    f.flush()
    f.close()
    
    #@-node:cmd_commit
    #@+node:cmd_list
    disks = conf.getDisks()
    
    if disks:
        print "Currently mounted freedisks:"
        for d in disks:
            print "  %s:" % d.name
            print "    uri=%s" % d.uri
            print "    passwd=%s" % d.passwd
    else:
        print "No freedisks mounted"
    
    #@-node:cmd_list
    #@+node:cmd_cmd
    def cmd_cmd(self, *args):
    
        # arbitrary command, for testing
        cmd = " ".join(args)
        print repr(doFsCommand(cmd))
    
    #@-node:cmd_cmd
    #@-others

#@-node:class FreediskMgr
#@+node:class FreediskConfig
class FreediskConfig:
    """
    allows for loading/saving/changing freedisk configs
    """
    #@    @+others
    #@+node:attribs
    _intAttribs = ["fcpPort", "fcpVerbosity"]
    
    _strAttribs = ["fcpHost", "mountpoint"]
    
    #@-node:attribs
    #@+node:__init__
    def __init__(self, path, passwd=None):
        """
        Create a config object from file at 'path', if it exists
        """
        #print "FreediskConfig: path=%s" % path
    
        self.path = path
        self.passwd = passwd
        
        if os.path.isfile(path):
            self.load()
        else:
            self.create()
    
        self.root = self.xml.root
    
    #@-node:__init__
    #@+node:load
    def load(self):
        """
        Loads config from self.config
        """
        # get the raw xml, plain or encrypted
        ciphertext = file(self.path, "rb").read()
    
        plaintext = ciphertext
    
        # try to wrap into xml object
        try:
            xml = self.xml = XMLFile(raw=plaintext)
        except:
            i = 0
            while i < 3:
                passwd = self.passwd = getpasswd("Freedisk config password")
                plaintext = decrypt(self.passwd, ciphertext)
                try:
                    xml = XMLFile(raw=plaintext)
                    break
                except:
                    i += 1
                    continue
            if i == 3:
                self.abort()
    
        self.xml = xml
        self.root = xml.root
    
    #@-node:load
    #@+node:create
    def create(self):
        """
        Creates a new config object
        """
        self.xml = XMLFile(root="freedisk")
        root = self.root = self.xml.root
    
        self.fcpHost = fcp.node.defaultFCPHost
        self.fcpPort = fcp.node.defaultFCPPort
        self.fcpVerbosity = fcp.node.defaultVerbosity
        self.mountpoint = defaultMountpoint
    
        self.save()
    
    #@-node:create
    #@+node:save
    def save(self):
    
        plain = self.xml.toxml()
    
        if self.passwd:
            cipher = encrypt(self.passwd, plain)
        else:
            cipher = plain
        
        f = file(self.path, "wb")
        f.write(cipher)
        f.flush()
        f.close()
    
    #@-node:save
    #@+node:abort
    def abort(self):
    
        print "freedisk: Cannot decrypt freedisk config file '%s'" % self.path
        print
        print "If you truly can't remember the password, your only"
        print "option now is to delete the config file and start again"
        sys.exit(1)
    
    #@-node:abort
    #@+node:setPassword
    def setPassword(self, passwd):
        
        self.passwd = passwd
        self.save()
    
    #@-node:setPassword
    #@+node:addDisk
    def addDisk(self, name, uri, privUri, passwd):
    
        d = self.getDisk(name)
        if isinstance(d, XMLNode):
            raise Exception("Disk '%s' already exists" % name)
        
        diskNode = self.root._addNode("disk")
        diskNode.name = name
        diskNode.uri = uri
        diskNode.privUri = privUri
        diskNode.passwd = passwd
        
        self.save()
    
    #@-node:addDisk
    #@+node:getDisk
    def getDisk(self, name):
        """
        Returns a record for a freedisk of name <name>
        """
        disks = self.root._getChild("disk")
        
        for d in disks:
            if d.name == name:
                return d
        
        return None
    
    #@-node:getDisk
    #@+node:getDisks
    def getDisks(self):
        """
        Returns all freedisk records
        """
        return self.root._getChild("disk")
    
    #@-node:getDisks
    #@+node:delDisk
    def delDisk(self, name):
        """
        Removes disk of given name
        """
        d = self.getDisk(name)
        if not isinstance(d, XMLNode):
            raise Exception("No such freedisk '%s'" % name)
        
        self.root._delChild(d)
    
        self.save()
    
    #@-node:delDisk
    #@+node:__getattr__
    def __getattr__(self, attr):
        
        if attr in self._intAttribs:
            try:
                return int(getattr(self.root, attr))
            except:
                raise AttributeError(attr)
    
        elif attr in self._strAttribs:
            try:
                return str(getattr(self.root, attr))
            except:
                raise AttributeError(attr)
    
        else:
            raise AttributeError(attr)
    
    #@-node:__getattr__
    #@+node:__setattr__
    def __setattr__(self, attr, val):
        
        if attr in self._intAttribs:
            val = str(val)
            setattr(self.root, attr, val)
            self.save()
        elif attr in self._strAttribs:
            setattr(self.root, attr, val)
            self.save()
        else:
            self.__dict__[attr] = val
    
    #@-node:__setattr__
    #@-others

#@-node:class FreediskConfig
#@+node:usage
def usage(msg=None, ret=1):
    """
    Prints usage message then exits
    """
    if msg:
        sys.stderr.write(msg+"\n")
    sys.stderr.write("Usage: %s [options] [<command> [<args>]]\n" % progname)
    sys.stderr.write("Type '%s -h' for help\n" % progname)
    sys.exit(ret)

#@-node:usage
#@+node:help
def help():
    """
    Display help info then exit
    """
    print "%s: manage a freenetfs filesystem" % progname
    print "Usage: %s [<options>] <command> [<arguments>]" % progname
    print "Options:"
    print "  -h, --help            Display this help"
    print "  -c, --config=         Specify config file, default ~/.freediskrc"
    print "Commands:"
    print "  init                  Edit configuration interactively"
    print "  mount                 Mount the freenetfs"
    print "  unmount               Unmount the freenetfs"
    print "  new <name>            Create a new freedisk of name <name>"
    print "                        A new keypair will be generated."
    print "  add <name> <URI>      Add an existing freedisk of name <name>"
    print "                        and public key URI <URI>"
    print "  del <name>            Remove freedisk of name <name>"
    print "  update <name>         Sync freedisk <name> from freenet"
    print "  commit <name>         Commit freedisk <name> into freenet"
    print
    print "Environment variables:"
    print "  FREEDISK_CONFIG - set this in place of '-c' argument"

    sys.exit(0)

#@-node:help
#@+node:removeDirAndContents
def removeDirAndContents(path):
    
    files = os.listdir(path)
    
    for f in files:
        fpath = os.path.join(path, f)
        if os.path.isfile(fpath):
            os.unlink(fpath)
        elif os.path.isdir(fpath):
            removeDirAndContents(fpath)
    os.rmdir(path)

#@-node:removeDirAndContents
#@+node:status
def status(msg):
    sys.stdout.write(msg + "...")
    time.sleep(1)
    print


#@-node:status
#@+node:encrypt
def encrypt(passwd, s):

    passwd = sha.new(passwd).digest()

    if SSLCrypto:
        # encrypt with blowfish 256, key=sha(password), IV=00000000
        return SSLCrypto.blowfish(passwd).encrypt(s)
    else:
        # no encyrption available, return plaintext
        return s

#@-node:encrypt
#@+node:decrypt
def decrypt(passwd, s):

    passwd = sha.new(passwd).digest()

    if SSLCrypto:
        # decrypt with blowfish 256, key=sha(password), IV=00000000
        return SSLCrypto.blowfish(passwd).decrypt(s)
    else:
        # no encyrption available, return plaintext
        return s

#@-node:decrypt
#@+node:getpasswd
def getpasswd(prompt="Password", confirm=False):

    if not confirm:
        return getpass.getpass(prompt+": ").strip()

    while 1:
        passwd = getpass.getpass(prompt+": ").strip()
        if passwd:
            passwd1 = getpasswd("Verify password").strip()
            if passwd == passwd1:
                break
            print "passwords do not match, please try again"
        else:
            break

    return passwd

#@-node:getpasswd
#@+node:doFsCommand
def doFsCommand(cmd):
    """
    Executes a command via base64-encoded file
    """
    cmdBase64 = fcp.node.base64encode(cmd)
    path = conf.mountpoint + "/cmds/" + cmdBase64
    return file(path).read()

#@-node:doFsCommand
#@+node:ipython
def ipython(o=None):

    from IPython.Shell import IPShellEmbed

    ipshell = IPShellEmbed()

    ipshell() # this call anywhere in your program will start IPython 

#@-node:ipython
#@+node:getyesno
def getyesno(prmt, dflt=True):
    
    if dflt:
        ynprmt = "[Y/n] "
    else:
        ynprmt = "[y/N] "

    resp = raw_input(prmt + "? " + ynprmt).strip()
    if not resp:
        return dflt
    resp = resp.lower()[0]
    return resp == 'y'

#@-node:getyesno
#@+node:main
def main():
    """
    Front end
    """
    #@    <<set defaults>>
    #@+node:<<set defaults>>
    # create defaults
    
    opts = {
        'debug' : False,
        'multithreaded' : False,
        'configFile' : configFile,
        'verbosity' : fcp.ERROR,
        'Verbosity' : 1023,
        }
    
    #@-node:<<set defaults>>
    #@nl

    #@    <<process args>>
    #@+node:<<process args>>
    # process args
    
    try:
        cmdopts, args = getopt.getopt(
            sys.argv[1:],
            "?hvc:dm",
            ["help", "verbose",
             "multithreaded",
             "config=", "debug",
             ]
            )
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    
    #print cmdopts
    for o, a in cmdopts:
    
        if o in ("-?", "-h", "--help"):
            help()
    
        if o in ("-v", "--verbose"):
            opts['verbosity'] = fcp.node.DETAIL
            opts['Verbosity'] = 1023
            verbose = True
    
        if o in ("-c", "--config"):
            opts['configFile'] = a
    
        if o in ("-d", "--debug"):
            opts['debug'] = True
    
        if o in ("-m", "--multithreaded"):
            opts['multithreaded'] = True
    
    #@-node:<<process args>>
    #@nl

    #@    <<execute command>>
    #@+node:<<execute command>>
    mgr = FreediskMgr(*args, **opts)
    
    mgr.run()
    
    #@-node:<<execute command>>
    #@nl

#@-node:main
#@+node:mainline
if __name__ == '__main__':
    main()

#@-node:mainline
#@-others

#@-node:freedisk app
#@-others
#@-node:@file freedisk.py
#@-leo
