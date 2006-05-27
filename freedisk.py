#! /usr/bin/env python
#@+leo-ver=4
#@+node:@file freedisk.py
#@@first
"""
A FUSE-based filesystem for freenet

Written May 2006 by aum

Released under the GNU Lesser General Public License

Requires:
    - python2.3 or later
    - FUSE kernel module installed and loaded
      (apt-get install fuse-source, crack tarball, build and install)
    - python2.3-fuse
    - libfuse2
"""

#@+others
#@+node:imports
import sys, os, time, stat, errno
from StringIO import StringIO
import thread
from threading import Lock
import traceback
from Queue import Queue
import sha, md5
from UserString import MutableString

from errno import *
from stat import *

try:
    import warnings
    warnings.filterwarnings('ignore',
                            'Python C API version mismatch',
                            RuntimeWarning,
                            )
except:
    pass
 
from _fuse import main, FuseGetContext, FuseInvalidate
from string import join
import sys
from errno import *

import fcp

#@-node:imports
#@+node:globals
fcpHost = fcp.node.defaultFCPHost
fcpPort = fcp.node.defaultFCPPort

defaultVerbosity = fcp.DETAIL

quiet = 0

myuid = os.getuid()
mygid = os.getgid()

inodes = {}
inodesNext = 1

# set this to disable hits to node, for debugging
_no_node = 0

#@-node:globals
#@+node:class ErrnoWrapper
class ErrnoWrapper:

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kw):
        try:
            return apply(self.func, args, kw)
        except (IOError, OSError), detail:
            traceback.print_exc()
            # Sometimes this is an int, sometimes an instance...
            if hasattr(detail, "errno"): detail = detail.errno
            return -detail


#@-node:class ErrnoWrapper
#@+node:class Fuse
class Fuse:

    #@    @+others
    #@+node:attribs
    _attrs = ['getattr', 'readlink', 'getdir', 'mknod', 'mkdir',
          'unlink', 'rmdir', 'symlink', 'rename', 'link', 'chmod',
          'chown', 'truncate', 'utime', 'open', 'read', 'write', 'release',
          'statfs', 'fsync']
    
    flags = 0
    multithreaded = 0
    
    #@-node:attribs
    #@+node:__init__
    def __init__(self, *args, **kw):
    
        # default attributes
        if args == ():
            # there is a self.optlist.append() later on, make sure it won't
            # bomb out.
            self.optlist = []
        else:
            self.optlist = args
        self.optdict = kw
    
        if len(self.optlist) == 1:
            self.mountpoint = self.optlist[0]
        else:
            self.mountpoint = None
        
        # grab command-line arguments, if any.
        # Those will override whatever parameters
        # were passed to __init__ directly.
        argv = sys.argv
        argc = len(argv)
    
        #self.log("argv=%s" % argv)
    
        ## physical thing to mount
        #self.configfile = argv[1]
    
        if argc > 2:
            # we've been given the mountpoint
            self.mountpoint = argv[2]
        if argc > 3:
            # we've received mount args
            optstr = argv[4]
            opts = optstr.split(",")
            for o in opts:
                try:
                    k, v = o.split("=", 1)
                    self.optdict[k] = v
                except:
                    self.optlist.append(o)
    
    #@-node:__init__
    #@+node:GetContent
    def GetContext(self):
        return FuseGetContext(self)
    
    #@-node:GetContent
    #@+node:Invalidate
    def Invalidate(self, path):
        return FuseInvalidate(self, path)
    
    #@-node:Invalidate
    #@+node:main
    def main(self):
    
        d = {'mountpoint': self.mountpoint}
        d['multithreaded'] = self.multithreaded
        if hasattr( self, 'debug'):
            d['lopts'] = 'debug';
    
        #opts = self.optdict
        #for k in ['wsize', 'rsize']:
        #    if opts.has_key(k):
        #        d[k] = int(opts[k])
    
        k=[]
        if hasattr(self,'allow_other'):
            k.append('allow_other')
    
        if hasattr(self,'kernel_cache'):
            k.append('kernel_cache')
    
        if len(k):
            d['kopts'] = join(k,',')
    
        for a in self._attrs:
            if hasattr(self,a):
                d[a] = ErrnoWrapper(getattr(self, a))
        #apply(main, (), d)
        main(**d)
    
    #@-node:main
    #@-others
#@-node:class Fuse
#@+node:class FreenetFS
class FreenetFS(Fuse):

    #@	@+others
    #@+node:attribs
    flags = 1
    
    # Files and directories already present in the filesytem.
    # Note - directories must end with "/"
    
    initialFiles = [
        "/",
    #    "/cmd/",
    #    "/cmd/genkey",
    #    "/cmd/genkeypair",
        "/get/",
        "/put/",
        #"/cmd/invertprivatekey/",
        "/keys/",
    #    "/private/",
        "/usr/",
        ]
    
    chrFiles = [
        "/cmd/genkey",
        "/cmd/genkeypair",
        ]
    
    #@-node:attribs
    #@+node:__init__
    def __init__(self, *args, **kw):
    
        Fuse.__init__(self, *args, **kw)
    
        if 0:
            self.log("xmp.py:Xmp:mountpoint: %s" % repr(self.mountpoint))
            self.log("xmp.py:Xmp:unnamed mount options: %s" % self.optlist)
            self.log("xmp.py:Xmp:named mount options: %s" % self.optdict)
    
        opts = self.optdict
    
        host = opts.get('host', fcpHost)
        port = opts.get('port', fcpPort)
        verbosity = int(opts.get('verbosity', defaultVerbosity))
    
        self.configfile = opts.get('config', None)
        if not self.configfile:
            raise Exception("Missing 'config=filename.conf' argument")
    
        self.loadConfig()
    
        self.setupFiles()
    
        self.fcpHost = host
        self.fcpPort = port
        self.fcpVerbosity = verbosity
    
        self.privKeyQueue = []
        self.privKeyLock = Lock()
        self.privKeypairQueue = []
        self.privKeypairLock = Lock()
    
        try:
            self.node = None
            self.connectToNode()
        except:
            #raise
            pass
    
        # do stuff to set up your filesystem here, if you want
        #thread.start_new_thread(self.mythread, ())
    
    #@-node:__init__
    #@+node:loadConfig
    def loadConfig(self):
        """
        The 'physical device' argument to mount should be the pathname
        of a configuration file, with 'name=val' lines, including the
        following items:
            - publickey=<freenet public key URI>
            - privatekey=<freenet private key URI> (optional, without which we
              will have the fs mounted readonly
        """
        opts = {}
    
        # build a dict of all the 'name=value' pairs in config file
        for line in [l.strip() for l in file(self.configfile).readlines()]:
            if line == '' or line.startswith("#"):
                continue
            try:
                name, val = line.split("=", 1)
                opts[name.strip()] = val.strip()
            except:
                pass
    
        # mandate a pubkey
        try:
            self.pubkey = opts['pubkey'].replace("SSK@", "USK@").split("/")[0] + "/"
        except:
            raise Exception("Config file %s: missing or invalid publickey" \
                            % self.configfile)
    
        # accept optional privkey
        if opts.has_key("privkey"):
    
            try:
                self.privkey = opts['privkey'].replace("SSK@",
                                                     "USK@").split("/")[0] + "/"
            except:
                raise Exception("Config file %s: invalid privkey" \
                                % self.configfile)
    
        # mandate cachepath
        try:
            self.cachedir = opts['cachedir']
            if not os.path.isdir(self.cachedir):
                raise hell
        except:
            raise Exception("config file %s: missing or invalid cache directory" \
                            % self.configfile)
    
    #@-node:loadConfig
    #@+node:setupFiles
    def setupFiles(self):
        """
        Create initial file/directory layout, according
        to attributes 'initialFiles' and 'chrFiles'
        """
        # easy map of files
        self.files = {}
    
        # now create records for initial files
        for path in self.initialFiles:
    
            # initial attribs
            isReg = isDir = isChr = isSock = isFifo = False
            perm = size = 0
    
            # determine file type
            if path.endswith("/"):
                isDir = True
                path = path[:-1]
                if not path:
                    path = "/"
            elif path in self.chrFiles:
                # it's a char file
                #isChr = True
                isReg = True
                perm |= 0666
                size = 1024
            else:
                # by default, it's a regular file
                isReg = True
    
            # create permissions field
            if isDir:
                perm |= 0755
            else:
                perm |= 0444
    
            # create record for this path
            self.addToCache(
                path=path,
                perm=perm,
                size=size,
                isdir=isDir, isreg=isReg, ischr=isChr,
                issock=isSock, isfifo=isFifo,
                )
    
    #@-node:setupFiles
    #@+node:connectToNode
    def connectToNode(self):
        """
        Attempts a connection to an fcp node
        """
        if self.node:
            return
        self.node = fcp.FCPNode(host=self.fcpHost,
                                port=self.fcpPort,
                                verbosity=self.fcpVerbosity)
        #self.log("pubkey=%s" % self.pubkey)
        #self.log("privkey=%s" % self.privkey)
        #self.log("cachedir=%s" % self.cachedir)
    
    #@-node:connectToNode
    #@+node:log
    def log(self, msg):
        if not quiet:
            print "freedisk:"+msg
    #@-node:log
    #@+node:mythread
    def mythread(self):
    
        """
        The beauty of the FUSE python implementation is that with the python interp
        running in foreground, you can have threads
        """    
        self.log("mythread: started")
        #while 1:
        #    time.sleep(120)
        #    print "mythread: ticking"
    
    #@-node:mythread
    #@+node:fs primitives
    # primitives required for actual fs operations
    
    #@+others
    #@+node:getattr
    def getattr(self, path):
    
        rec = self.files.get(path, None)
        if not rec:
            # retrieving a key?
            if path.startswith("/keys/"):
                #@            <<generate keypair>>
                #@+node:<<generate keypair>>
                # generate a new keypair
                self.connectToNode()
                pubkey, privkey = self.node.genkey()
                rec = self.addToCache(
                    path=path,
                    isreg=True,
                    data=pubkey+"\n"+privkey,
                    perm=0444,
                    )
                #@-node:<<generate keypair>>
                #@nl
            elif path.startswith("/get/"):
                #@            <<retrieve/cache key>>
                #@+node:<<retrieve/cache key>>
                # check the cache
                if _no_node:
                    print "FIXME: returning IOerror"
                    raise IOError(errno.ENOENT, path)
                
                # get a key
                uri = path.split("/", 2)[-1]
                try:
                    self.connectToNode()
                    mimetype, data = self.node.get(uri)
                    rec = FileRecord(path=path,
                                     isreg=True,
                                     perm=0644,
                                     data=data,
                                     )
                    self.addToCache(rec)
                
                except:
                    traceback.print_exc()
                    #print "ehhh?? path=%s" % path
                    raise IOError(errno.ENOENT, path)
                
                #@-node:<<retrieve/cache key>>
                #@nl
            else:
                #@            <<try host fs>>
                #@+node:<<try host fs>>
                # try the host filesystem
                print "getattr: no rec for %s, hitting main fs" % path
                rec = FileRecord(os.lstat(path), path=path)
                
                print rec
                
                #@-node:<<try host fs>>
                #@nl
    
        self.log("getattr: path=%s" % path)
        self.log("  mode=0%o" % rec.mode)
        self.log("  inode=0x%x" % rec.inode)
        self.log("  dev=0x%x" % rec.dev)
        self.log("  nlink=0x%x" % rec.nlink)
        self.log("  uid=%d" % rec.uid)
        self.log("  gid=%d" % rec.gid)
        self.log("  size=%d" % rec.size)
        self.log("  atime=%d" % rec.atime)
        self.log("  mtime=%d" % rec.mtime)
        self.log("  ctime=%d" % rec.ctime)
        self.log("rec=%s" % str(rec))
    
        return tuple(rec)
    
    #@-node:getattr
    #@+node:readlink
    def readlink(self, path):
    
    	ret = os.readlink(path)
        self.log("readlink: path=%s\n  => %s" % (path, ret))
    	return ret
    
    #@-node:readlink
    #@+node:getdir
    def getdir(self, path):
    
        rec = self.files.get(path, None)
    
        if rec:
            files = [os.path.split(child.path)[-1] for child in rec.children]
            files.sort()
            if rec.isdir:
                if  path != "/":
                    files.insert(0, "..")
                files.insert(0, ".")
        else:
            self.log("Hit main fs for %s" % path)
            files = os.listdir(path)
    
        ret = map(lambda x: (x,0), files)
    
        self.log("getdir: path=%s\n  => %s" % (path, ret))
        return ret
    
    #@-node:getdir
    #@+node:unlink
    def unlink(self, path):
    
        # remove existing file?
        if path.startswith("/get/") \
        or path.startswith("/put/") \
        or path.startswith("/keys/"):
            rec = self.files.get(path, None)
            if not rec:
                raise IOError(2, path)
            self.delFromCache(rec)
            return 0
    
        # fallback on host fs
    	ret = os.unlink(path)
        self.log("unlink: path=%s\n  => %s" % (path, ret))
    	return ret
    
    #@-node:unlink
    #@+node:rmdir
    def rmdir(self, path):
    
    	ret = os.rmdir(path)
        self.log("rmdir: path=%s\n  => %s" % (path, ret))
    	return ret
    
    #@-node:rmdir
    #@+node:symlink
    def symlink(self, path, path1):
    
    	ret = os.symlink(path, path1)
        self.log("symlink: path=%s path1=%s\n  => %s" % (path, path1, ret))
    	return ret
    
    #@-node:symlink
    #@+node:rename
    def rename(self, path, path1):
    
    	ret = os.rename(path, path1)
        self.log("rename: path=%s path1=%s\n  => %s" % (path, path1, ret))
    	return ret
    
    #@-node:rename
    #@+node:link
    def link(self, path, path1):
    
    	ret = os.link(path, path1)
        self.log("link: path=%s path1=%s\n  => %s" % (path, path1, ret))
    	return ret
    
    #@-node:link
    #@+node:chmod
    def chmod(self, path, mode):
    
    	ret = os.chmod(path, mode)
        self.log("chmod: path=%s mode=%s\n  => %s" % (path, mode, ret))
    	return ret
    
    #@-node:chmod
    #@+node:chown
    def chown(self, path, user, group):
    
    	ret = os.chown(path, user, group)
        self.log("chmod: path=%s user=%s group=%s\n  => %s" % (path, user, group, ret))
    	return ret
    
    #@-node:chown
    #@+node:truncate
    def truncate(self, path, size):
    
    	f = open(path, "w+")
    	ret = f.truncate(size)
        self.log("truncate: path=%s size=%s\n  => %s" % (path, size, ret))
        return ret
    
    #@-node:truncate
    #@+node:mknod
    def mknod(self, path, mode, dev):
        """ Python has no os.mknod, so we can only do some things """
        # start key write, if needed
        if path.startswith("/put/"):
    
            # see if an existing file
            if self.files.has_key(path):
                raise IOError(errno.EEXIST, path)
    
            rec = self.addToCache(
                path=path, isreg=True, iswriting=True,
                perm=0644)
            ret = 0
    
        else:
            # fall back on host os
            if S_ISREG(mode):
                file(path, "w").close()
                ret = 0
            else:
                ret = -EINVAL
    
        self.log("mknod: path=%s mode=0%o dev=%s\n  => %s" % (
                    path, mode, dev, ret))
    
        return ret
    
    #@-node:mknod
    #@+node:mkdir
    def mkdir(self, path, mode):
    
    	ret = os.mkdir(path, mode)
        self.log("mkdir: path=%s mode=%s\n  => %s" % (path, mode, ret))
        return ret
    
    #@-node:mkdir
    #@+node:utime
    def utime(self, path, times):
    
    	ret = os.utime(path, times)
        self.log("utime: path=%s times=%s\n  => %s" % (path, times, ret))
    	return ret
    
    #@-node:utime
    #@+node:open
    def open(self, path, flags):
    
        self.log("open: path=%s flags=%s" % (path, flags))
    
        # see if it's an existing file
        rec = self.files.get(path, None)
        
        if rec:
            # barf if not regular file
            if not (rec.isreg or rec.ischr):
                self.log("open: %s is not regular file" % path)
                raise IOError(errno.EIO, "Not a regular file: %s" % path)
    
        else:
            # fall back to host fs
            os.close(os.open(path, flags))
    
        self.log("open: open of %s succeeded" % path)
    
        # seems ok
        return 0
    
    #@-node:open
    #@+node:read
    def read(self, path, length, offset):
        """
        """
        # forward to existing file if any
        rec = self.files.get(path, None)
        if rec:
            rec.seek(offset)
            buf = rec.read(length)
            
            self.log("read: path=%s length=%s offset=%s\n => %s" % (
                                        path, length, offset, len(buf)))
            #print repr(buf)
            return buf
            
        else:
            # fall back on host fs
            f = open(path, "r")
            f.seek(offset)
            buf = f.read(length)
    
        self.log("read: path=%s length=%s offset=%s\n  => (%s bytes)" % (
                                        path, length, offset, len(buf)))
    
        return buf
    
    #@-node:read
    #@+node:write
    def write(self, path, buf, off):
    
        dataLen = len(buf)
    
        rec = self.files.get(path, None)
        if rec:
            # write to existing 'file'
            rec.seek(off)
            rec.write(buf)
        else:
            f = open(path, "r+")
            f.seek(off)
            nwritten = f.write(buf)
            f.flush()
    
        self.log("write: path=%s buf=[%s bytes] off=%s" % (path, len(buf), off))
    
    	#return nwritten
    	return dataLen
    
    #@-node:write
    #@+node:release
    def release(self, path, flags):
    
        rec = self.files.get(path, None)
        if not rec:
            return
    
        # if writing, save the thing
        if rec.iswriting:
            # what uri?
            rec.iswriting = False
            uri = os.path.split(path)[1]
    
            # frigs to allow fancy CHK@ inserts
            if uri.startswith("CHK@"):
                putUri = "CHK@"
            else:
                putUri = uri
            ext = os.path.splitext(uri)[1]
    
            try:
                self.log("release: inserting %s" % uri)
    
                mimetype = fcp.node.guessMimetype(path)
                data = rec.data
    
                # empty the pseudo-file till a result is through
                rec.data = 'inserting'
    
                self.connectToNode()
    
                #print "FIXME: data=%s" % repr(data)
    
                if _no_node:
                    print "FIXME: not inserting"
                    getUri = "NO_URI"
                else:
                    # perform the insert
                    getUri = self.node.put(
                                putUri,
                                data=data,
                                mimetype=mimetype)
    
                    # strip 'freenet:' prefix
                    if getUri.startswith("freenet:"):
                        getUri = getUri[8:]
    
                    # restore file extension
                    if getUri.startswith("CHK@"):
                        getUri += ext
    
                    # now cache the read-back
                    self.addToCache(
                        path="/get/"+getUri,
                        data=data,
                        perm=0444,
                        isreg=True,
                        )
            
                    # and adjust the written file to reveal read uri
                    rec.data = getUri
    
                self.log("release: inserted %s as %s ok" % (
                            uri, mimetype))
    
            except:
                traceback.print_exc()
                rec.data = 'failed'
                self.log("release: insert of %s failed" % uri)
                raise IOError(errno.EIO, "Failed to insert")
    
            self.log("release: done with insertion")
            return 0
    
        self.log("release: path=%s flags=%s" % (path, flags))
        return 0
    
    #@-node:release
    #@+node:statfs
    def statfs(self):
        """
        Should return a tuple with the following 6 elements:
            - blocksize - size of file blocks, in bytes
            - totalblocks - total number of blocks in the filesystem
            - freeblocks - number of free blocks
            - totalfiles - total number of file inodes
            - freefiles - nunber of free file inodes
    
        Feel free to set any of the above values to 0, which tells
        the kernel that the info is not available.
        """
        self.log("statfs: returning fictitious values")
        blocks_size = 1024
        blocks = 100000
        blocks_free = 25000
        files = 100000
        files_free = 60000
        namelen = 80
    
        return (blocks_size, blocks, blocks_free, files, files_free, namelen)
    
    #@-node:statfs
    #@+node:fsync
    def fsync(self, path, isfsyncfile):
    
        self.log("fsync: path=%s, isfsyncfile=%s" % (path, isfsyncfile))
        return 0
    
    #@-node:fsync
    #@-others
    
    #@-node:fs primitives
    #@+node:hashpath
    def hashpath(self, path):
        
        return sha.new(path).hexdigest()
    
    #@-node:hashpath
    #@+node:addToCache
    def addToCache(self, rec=None, **kw):
        """
        Tries to 'cache' a given file/dir record, and
        adds it to parent dir
        """
        if rec == None:
            rec = FileRecord(**kw)
    
        path = rec.path
    
        # barf if file/dir already exists
        if self.files.has_key(path):
            self.log("addToCache: already got %s !!!" % path)
            return
    
        #print "path=%s" % path
    
        # if not root, add to parent
        if path != '/':
            parentPath = os.path.split(path)[0]
            parentRec = self.files.get(parentPath, None)
            parentRec.addChild(rec)
            if not parentRec:
                self.log("addToCache: no parent of %s ?!?!" % path)
                return
    
        # ok, add to our table
        self.files[path] = rec
    
        # done
        return rec
    
    #@-node:addToCache
    #@+node:delFromCache
    def delFromCache(self, rec):
        """
        Tries to remove file/dir record from cache
        """
        path = rec.path
        parentPath = os.path.split(path)[0]
        
        if self.files.has_key(path):
            del self.files[path]
        
        parentRec = self.files.get(parentPath, None)
        if parentRec:
            parentRec.delChild(rec)
    
    #@-node:delFromCache
    #@+node:getDirStat
    def getDirStat(self, path):
        """
        returns a stat tuple for given path
        """
        return FileRecord(mode=0700, path=path, isdir=True)
    
    #@-node:getDirStat
    #@+node:statFromKw
    def statFromKw(self, **kw):
        """
        Constructs a stat tuple from keywords
        """
        tup = [0] * 10
    
        # build mode mask
        mode = kw.get('mode', 0)
        if kw.get('isdir', False):
            mode |= stat.S_IFDIR
        if kw.get('ischr', False):
            mode |= stat.S_IFCHR
        if kw.get('isblk', False):
            mode |= stat.S_IFBLK
        if kw.get('isreg', False):
            mode |= stat.S_IFREG
        if kw.get('isfifo', False):
            mode |= stat.S_IFIFO
        if kw.get('islink', False):
            mode |= stat.S_IFLNK
        if kw.get('issock', False):
            mode |= stat.S_IFSOCK
    
        path = kw['path']
    
        # get inode number
        inode = self.pathToInode(path)
        
        dev = 0
        
        nlink = 1
        uid = myuid
        gid = mygid
        size = 0
        atime = mtime = ctime = timeNow()
    
        return (mode, inode, dev, nlink, uid, gid, size, atime, mtime, ctime)
    
        # st_mode, st_ino, st_dev, st_nlink,
        # st_uid, st_gid, st_size,
        # st_atime, st_mtime, st_ctime
    
    #@-node:statFromKw
    #@+node:statToDict
    def statToDict(self, info):
        """
        Converts a tuple returned by a stat call into
        a dict with keys:
            
            - isdir
            - ischr
            - isblk
            - isreg
            - isfifo
            - islnk
            - issock
            - mode
            - inode
            - dev
            - nlink
            - uid
            - gid
            - size
            - atime
            - mtime
            - ctime
        """
        print "statToDict: info=%s" % str(info)
    
        mode = info[stat.ST_MODE]
        return {
            'isdir'  : stat.S_ISDIR(mode),
            'ischr'  : stat.S_ISCHR(mode),
            'isblk'  : stat.S_ISBLK(mode),
            'isreg'  : stat.S_ISREG(mode),
            'isfifo' : stat.S_ISFIFO(mode),
            'islink'  : stat.S_ISLNK(mode),
            'issock' : stat.S_ISSOCK(mode),
            'mode'   : mode,
            'inode'  : info[stat.ST_INO],
            'dev'    : info[stat.ST_DEV],
            'nlink'  : info[stat.ST_NLINK],
            'uid'    : info[stat.ST_UID],
            'gid'    : info[stat.ST_GID],
            'size'   : info[stat.ST_SIZE],
            'atime'  : info[stat.ST_ATIME],
            'mtime'  : info[stat.ST_MTIME],
            'ctime'  : info[stat.ST_CTIME],
            }
    
    #@-node:statToDict
    #@+node:getReadURI
    def getReadURI(self, path):
        """
        Converts to a pathname to a freenet URI for insertion,
        using public key
        """
        return self.pubkey + self.hashpath(path) + "/0"
    
    #@-node:getReadURI
    #@+node:getWriteURI
    def getWriteURI(self, path):
        """
        Converts to a pathname to a freenet URI for insertion,
        using private key if any
        """
        if not self.privkey:
            raise Exception("cannot write: no private key")
        
        return self.privkey + self.hashpath(path) + "/0"
    
    #@-node:getWriteURI
    #@-others

#@-node:class FreenetFS
#@+node:class FileRecord
class FileRecord(list):
    """
    Encapsulates the info for a file, and can
    be returned by getattr
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, statrec=None, **kw):
        """
        """
        # got a statrec arg?
        if statrec:
            # yes, extract main items
            dev = statrec[stat.ST_DEV]
            nlink = statrec[stat.ST_NLINK]
            uid = statrec[stat.ST_UID]
            gid = statrec[stat.ST_GID]
            size = statrec[stat.ST_SIZE]
        else:
            # no, fudge a new one
            statrec = [0,0,0,0,0,0,0,0,0,0]
            dev = 0
            nlink = 1
            uid = myuid
            gid = mygid
            size = 0
    
        # convert tuple to list if need be
        if not hasattr(statrec, '__setitem__'):
            statrec = list(statrec)
    
        # build mode mask
        mode = kw.get('mode', 0)
        if kw.get('isdir', False):
            mode |= stat.S_IFDIR
        if kw.get('ischr', False):
            mode |= stat.S_IFCHR
        if kw.get('isblk', False):
            mode |= stat.S_IFBLK
        if kw.get('isreg', False):
            mode |= stat.S_IFREG
        if kw.get('isfifo', False):
            mode |= stat.S_IFIFO
        if kw.get('islink', False):
            mode |= stat.S_IFLNK
        if kw.get('issock', False):
            mode |= stat.S_IFSOCK
    
        # handle non-file-related keywords
        perm = kw.get('perm', 0)
        mode |= perm
    
        path = kw['path']
        self.path = path
    
        self.stream = StringIO()
    
        data = kw.get('data', '')
        self.stream = StringIO(data)
    
        for key in ['iswriting']:
            if kw.has_key(key):
                setattr(self, key, kw[key])
    
        # child files/dirs
        self.children = []
        
        #print "FileRecord.__init__: path=%s" % path
    
        # get inode number
        inode = pathToInode(path)
        
        #size = kw.get('size', 0)
        now = timeNow()
        atime = kw.get('atime', now)
        mtime = kw.get('mtime', now)
        ctime = kw.get('ctime', now)
    
        #print "statrec[stat.ST_MODE]=%s" % statrec[stat.ST_MODE]
        #print "mode=%s" % mode
    
        statrec[stat.ST_MODE] |= mode
        statrec[stat.ST_INO] = inode
        statrec[stat.ST_DEV] = dev
        statrec[stat.ST_NLINK] = nlink
        statrec[stat.ST_UID] = uid
        statrec[stat.ST_GID] = gid
    
        statrec[stat.ST_SIZE] = len(self.stream.getvalue())
    
        statrec[stat.ST_ATIME] = atime
        statrec[stat.ST_MTIME] = atime
        statrec[stat.ST_CTIME] = atime
        
        list.__init__(self, statrec)
    
        self.iswriting = kw.get('iswriting', False)
        
    #@-node:__init__
    #@+node:__getattr__
    def __getattr__(self, attr):
        """
        Support read of pseudo-attributes:
            - mode, isdir, ischr, isblk, isreg, isfifo, islnk, issock,
            - inode, dev, nlink, uid, gid, size, atime, mtime, ctime
        """
        if attr == 'mode':
            return self[stat.ST_MODE]
    
        if attr == 'isdir':
            return stat.S_ISDIR(self.mode)
    
        if attr == 'ischr':
            return stat.S_ISCHR(self.mode)
    
        if attr == 'isblk':
            return stat.S_ISBLK(self.mode)
    
        if attr == 'isreg':
            return stat.S_ISREG(self.mode)
    
        if attr == 'isfifo':
            return stat.S_ISFIFO(self.mode)
    
        if attr == 'islnk':
            return stat.S_ISLNK(self.mode)
    
        if attr == 'issock':
            return stat.S_ISSOCK(self.mode)
    
        if attr == 'inode':
            return self[stat.ST_INO]
        
        if attr == 'dev':
            return self[stat.ST_DEV]
        
        if attr == 'nlink':
            return self[stat.ST_NLINK]
        
        if attr == 'uid':
            return self[stat.ST_UID]
    
        if attr == 'gid':
            return self[stat.ST_GID]
    
        if attr == 'size':
            return self[stat.ST_SIZE]
        
        if attr == 'atime':
            return self[stat.ST_ATIME]
        
        if attr == 'mtime':
            return self[stat.ST_ATIME]
        
        if attr == 'ctime':
            return self[stat.ST_ATIME]
    
        if attr == 'data':
            return self.stream.getvalue()
        
        try:
            return getattr(self.stream, attr)
        except:
            pass
    
        raise AttributeError(attr)
    
    #@-node:__getattr__
    #@+node:__setattr__
    def __setattr__(self, attr, val):
        """
        Support write of pseudo-attributes:
            - mode, isdir, ischr, isblk, isreg, isfifo, islnk, issock,
            - inode, dev, nlink, uid, gid, size, atime, mtime, ctime
        """
        if attr == 'isdir':
            if val:
                self[stat.ST_MODE] |= stat.S_IFDIR
            else:
                self[stat.ST_MODE] &= ~stat.S_IFDIR
        elif attr == 'ischr':
            if val:
                self[stat.ST_MODE] |= stat.S_IFCHR
            else:
                self[stat.ST_MODE] &= ~stat.S_IFCHR
        elif attr == 'isblk':
            if val:
                self[stat.ST_MODE] |= stat.S_IFBLK
            else:
                self[stat.ST_MODE] &= ~stat.S_IFBLK
        elif attr == 'isreg':
            if val:
                self[stat.ST_MODE] |= stat.S_IFREG
            else:
                self[stat.ST_MODE] &= ~stat.S_IFREG
        elif attr == 'isfifo':
            if val:
                self[stat.ST_MODE] |= stat.S_IFIFO
            else:
                self[stat.ST_MODE] &= ~stat.S_IFIFO
        elif attr == 'islnk':
            if val:
                self[stat.ST_MODE] |= stat.S_IFLNK
            else:
                self[stat.ST_MODE] &= ~stat.S_IFLNK
        elif attr == 'issock':
            if val:
                self[stat.ST_MODE] |= stat.S_IFSOCK
            else:
                self[stat.ST_MODE] &= ~stat.S_IFSOCK
    
        elif attr == 'mode':
            self[stat.ST_MODE] = val
        elif attr == 'inode':
            self[stat.ST_IMO] = val
        elif attr == 'dev':
            self[stat.ST_DEV] = val
        elif attr == 'nlink':
            self[stat.ST_NLINK] = val
        elif attr == 'uid':
            self[stat.ST_UID] = val
        elif attr == 'gid':
            self[stat.ST_GID] = val
        elif attr == 'size':
            self[stat.ST_SIZE] = val
        elif attr == 'atime':
            self[stat.ST_ATIME] = val
        elif attr == 'mtime':
            self[stat.ST_MTIME] = val
        elif attr == 'ctime':
            self[stat.ST_CTIME] = val
    
        elif attr == 'data':
            oldPos = self.stream.tell()
            self.stream = StringIO(val)
            self.stream.seek(min(oldPos, len(val)))
            self.size = len(val)
    
        else:
            self.__dict__[attr] = val
    
    #@-node:__setattr__
    #@+node:write
    def write(self, buf):
        
        self.stream.write(buf)
        self.size = len(self.stream.getvalue())
    
    #@-node:write
    #@+node:addChild
    def addChild(self, rec):
        """
        Adds a child file rec as a child of this rec
        """
        if not isinstance(rec, FileRecord):
            raise Exception("Not a FileRecord: %s" % rec)
    
        self.children.append(rec)
        self.size += 1
    
    #@-node:addChild
    #@+node:delChild
    def delChild(self, rec):
        """
        Tries to remove a child entry
        """
        if rec in self.children:
            self.children.remove(rec)
            self.size -= 1
    
        else:
            print "eh? trying to remove %s from %s" % (rec.path, self.path)
    
    #@-node:delChild
    #@-others

#@-node:class FileRecord
#@+node:pathToInode
def pathToInode(path):
    """
    Comes up with a unique inode number given a path
    """
    # try for existing known path/inode    
    inode = inodes.get(path, None)
    if inode != None:
        return inode

    # try hashing the path to 32bit
    inode = int(md5.new(path).hexdigest()[:7], 16)
    
    # and ensure it's unique
    while inodes.has_key(inode):
        inode += 1

    # register it
    inodes[path] = inode

    # done
    return inode
    
#@-node:pathToInode
#@+node:timeNow
def timeNow():
    return int(time.time()) & 0xffffffffL

#@-node:timeNow
#@+node:mainline
if __name__ == '__main__':

	server = FreenetFS()
	server.multithreaded = 1;
	server.main()

#@-node:mainline
#@-others

#@-node:@file freedisk.py
#@-leo
