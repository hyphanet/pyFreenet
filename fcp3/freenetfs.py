#! /usr/bin/env python
#@+leo-ver=4
#@+node:@file freenetfs.py
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
from io import StringIO
import _thread
from threading import Lock
import traceback
from queue import Queue
from hashlib import md5, sha1

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
 
import sys
from errno import *

import fcp3 as fcp

from fcp3.xmlobject import XMLFile
from fcp3.node import guessMimetype, base64encode, base64decode, uriIsPrivate

#@-node:imports
#@+node:globals
argv = sys.argv
argc = len(argv)
progname = argv[0]

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

# special filenames in freedisk toplevel dirs
freediskSpecialFiles = [
    '.privatekey', '.publickey', '.cmd', '.status', ".passwd",
    ]

showAllExceptions = False

#@-node:globals
#@+node:class ErrnoWrapper
class ErrnoWrapper:

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kw):
        try:
            return self.func(*args, **kw)
        except (IOError, OSError) as detail:
            if showAllExceptions:
                traceback.print_exc()
            # Sometimes this is an int, sometimes an instance...
            if hasattr(detail, "errno"): detail = detail.errno
            return -detail


#@-node:class ErrnoWrapper
#@+node:class FreenetBaseFS
class FreenetBaseFS:

    #@	@+others
    #@+node:attribs
    multithreaded = 0
    flags = 1
    debug = False
    fcpHost = fcpHost
    fcpPort = fcpPort
    verbosity = defaultVerbosity
    allow_other = False
    kernel_cache = False
    config = os.path.join(os.path.expanduser("~"), ".freediskrc")
    
    # Files and directories already present in the filesytem.
    # Note - directories must end with "/"
    
    initialFiles = [
        "/",
        "/get/",
        "/put/",
        "/keys/",
        "/usr/",
        "/cmds/",
        ]
    
    chrFiles = [
        ]
    
    #@-node:attribs
    #@+node:__init__
    def __init__(self, mountpoint, *args, **kw):
        """
        Create a freenetfs
        
        Arguments:
            - mountpoint - the dir in the filesystem at which to mount the fs
            - other args get passed to fuse
        
        Keywords:
            - multithreaded - whether to run the fs multithreaded, default True
            - fcpHost - hostname of FCP service
            - fcpPort - port number of FCP service
            - verbosity - defaults to fcp.DETAIL
            - config - location of config file
            - debug - whether to run in debug mode, default False
        """
    
        self.log("FreenetBaseFS.__init__: args=%s kw=%s" % (args, kw))
    
        for k in ['multithreaded',
                  'fcpHost',
                  'fcpPort',
                  'verbosity',
                  'debug',
                  ]:
            if k in kw:
                v = kw.pop(k)
                try:
                    v = int(v)
                except:
                    pass
                    
                setattr(self, k, v)
    
        self.optlist = list(args)
        self.optdict = dict(kw)
    
        self.mountpoint = mountpoint
        
        #if not self.config:
        #    raise Exception("Missing 'config=filename.conf' argument")
    
        #self.loadConfig()
        self.setupFiles()
        self.setupFreedisks()
    
        # do stuff to set up your filesystem here, if you want
        #thread.start_new_thread(self.mythread, ())
    
        if 0:
            self.log("xmp.py:Xmp:mountpoint: %s" % repr(self.mountpoint))
            self.log("xmp.py:Xmp:unnamed mount options: %s" % self.optlist)
            self.log("xmp.py:Xmp:named mount options: %s" % self.optdict)
    
        try:
            self.node = None
            self.connectToNode()
        except:
            raise
            pass
    
    #@-node:__init__
    #@+node:command handlers
    # methods which handle filesystem commands
    
    #@+others
    #@+node:executeCommand
    def executeCommand(self, cmd):
        """
        Executes a single-line command that was submitted as
        a base64-encoded filename in /cmds/
        """
        self.log("executeCommand:cmd=%s" % repr(cmd))
    
        try:
            cmd, args = cmd.split(" ", 1)
            args = args.split("|")
        except:
            return "error\nInvalid command %s" % repr(cmd)
    
        method = getattr(self, "cmd_"+cmd, None)
        if method:
            return method(*args)
        else:
            return "error\nUnrecognised command %s" % repr(cmd)
    
    #@-node:executeCommand
    #@+node:cmd_hello
    def cmd_hello(self, *args):
        
        return "ok\nhello: args=%s" % repr(args)
    
    #@-node:cmd_hello
    #@+node:cmd_mount
    def cmd_mount(self, *args):
        """
        tries to mount a freedisk
        
        arguments:
            - diskname
            - uri (may be public or private)
            - password
        """
        #print "mount: args=%s" % repr(args)
    
        try:
            name, uri, passwd = args
        except:
            return "error\nmount: invalid arguments %s" % repr(args)
    
        try:
            self.addDisk(name, uri, passwd)
        except:
            return "error\nmount: failed to mount disk %s" % name
    
        return "ok\nmount: successfully mounted disk %s" % name
    
    #@-node:cmd_mount
    #@+node:cmd_umount
    def cmd_umount(self, *args):
        """
        tries to unmount a freedisk
        
        arguments:
            - diskname
        """
        #print "mount: args=%s" % repr(args)
    
        try:
            name = args[0]
        except:
            return "error\numount: invalid arguments %s" % repr(args)
    
        try:
            self.delDisk(name)
        except:
            traceback.print_exc()
            return "error\numount: failed to unmount freedisk '%s'" % name
        
        return "ok\numount: successfully unmounted freedisk %s" % name
    
    #@-node:cmd_umount
    #@+node:cmd_update
    def cmd_update(self, *args):
        """
        Does an update of a freedisk from freenet
        """
        #print "update: args=%s" % repr(args)
    
        try:
            name = args[0]
        except:
            return "error\nupdate: invalid arguments %s" % repr(args)
    
        try:
            self.updateDisk(name)
        except:
            traceback.print_exc()
            return "error\nupdate: failed to update freedisk '%s'" % name
        
        return "ok\nupdate: successfully updated freedisk '%s'" % name
    
    #@-node:cmd_update
    #@+node:cmd_commit
    def cmd_commit(self, *args):
        """
        Does an commit of a freedisk into freenet
        """
        try:
            name = args[0]
        except:
            return "error\ninvalid arguments %s" % repr(args)
    
        try:
            uri = self.commitDisk(name)
        except:
            traceback.print_exc()
            return "error\nfailed to commit freedisk '%s'" % name
        
        return "ok\n%s" % uri
    
    #@-node:cmd_commit
    #@-others
    
    #@-node:command handlers
    #@+node:fs primitives
    # primitives required for actual fs operations
    
    #@+others
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
    #@+node:fsync
    def fsync(self, path, isfsyncfile):
    
        self.log("fsync: path=%s, isfsyncfile=%s" % (path, isfsyncfile))
        return 0
    
    #@-node:fsync
    #@+node:getattr
    def getattr(self, path):
    
        rec = self.files.get(path, None)
        if not rec:
            # each of these code segments should assign a record to 'rec',
            # or raise an IOError
            
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
                    data=pubkey+"\n"+privkey+"\n",
                    perm=0o444,
                    )
                
                #@-node:<<generate keypair>>
                #@nl
            elif path.startswith("/get/"):
                #@            <<retrieve/cache key>>
                #@+node:<<retrieve/cache key>>
                # check the cache
                if _no_node:
                    print("FIXME: returning IOerror")
                    raise IOError(errno.ENOENT, path)
                
                # get a key
                uri = path.split("/", 2)[-1]
                try:
                    self.connectToNode()
                    mimetype, data = self.node.get(uri)
                    rec = self.addToCache(
                        path=path,
                        isreg=True,
                        perm=0o644,
                        data=data,
                        )
                
                except:
                    traceback.print_exc()
                    #print "ehhh?? path=%s" % path
                    raise IOError(errno.ENOENT, path)
                
                #@-node:<<retrieve/cache key>>
                #@nl
            elif path.startswith("/cmds/"):
                #@            <<base64 command>>
                #@+node:<<base64 command>>
                # a command has been encoded via base64
                
                cmdBase64 = path.split("/cmds/", 1)[-1]
                
                cmd = base64decode(cmdBase64)
                
                result = self.executeCommand(cmd)
                
                rec = self.addToCache(path=path, isreg=True, data=result, perm=0o644)
                
                #@-node:<<base64 command>>
                #@nl
            else:
                raise IOError(errno.ENOENT, path)
    
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
    
        ret = [(x,0) for x in files]
    
        self.log("getdir: path=%s\n  => %s" % (path, ret))
        return ret
    
    #@-node:getdir
    #@+node:link
    def link(self, path, path1):
    
        raise IOError(errno.EPERM, path)
    
        ret = os.link(path, path1)
        self.log("link: path=%s path1=%s\n  => %s" % (path, path1, ret))
        return ret
    
    #@-node:link
    #@+node:mkdir
    def mkdir(self, path, mode):
    
        self.log("mkdir: path=%s mode=%s" % (path, mode))
    
        # barf if directory exists
        if path in self.files:
            raise IOError(errno.EEXIST, path)
    
        # barf if happening outside /usr/
        if not path.startswith("/usr/"):
            raise IOError(errno.EACCES, path)
    
        parentPath = os.path.split(path)[0]
    
        if parentPath == '/usr':
            # creating a new freedisk
    
            # create the directory record
            rec = self.addToCache(path=path, isdir=True, perm=0o555)
    
            # create the pseudo-files within it
            for name in freediskSpecialFiles:
                subpath = os.path.join(path, name)
                rec = self.addToCache(path=subpath, isreg=True, perm=0o644)
                if name == '.status':
                    rec.data = "idle"
    
            # done here
            return 0
    
        elif path.startswith("/usr/"):
            # creating a dir within a freedisk
    
            # barf if no write permission in dir
            diskPath = "/".join(path.split("/")[:3])
            diskRec = self.files.get(diskPath, None)
            #if not diskRec:
            #    self.log("mkdir: diskPath=%s" % diskPath)
            #    raise IOError(errno.ENOENT, path)
            if diskRec and not diskRec.canwrite:
                self.log("mkdir: diskPath=%s" % diskPath)
                raise IOError(errno.EPERM, path)
    
            # ok to create
            self.addToCache(path=path, isdir=True, perm=0o755)
        
        return 0
        
    #@-node:mkdir
    #@+node:mknod
    def mknod(self, path, mode, dev):
        """ Python has no os.mknod, so we can only do some things """
    
        if path == "/":
            #return -EINVAL
            raise IOError(errno.EEXIST, path)
        
        parentPath = os.path.split(path)[0]
        if parentPath in ['/', '/usr']:
            #return -EINVAL
            raise IOError(errno.EPERM, path)
    
        # start key write, if needed
        if parentPath == "/put":
    
            # see if an existing file
            if path in self.files:
                raise IOError(errno.EEXIST, path)
    
            rec = self.addToCache(
                path=path, isreg=True, iswriting=True,
                perm=0o644)
            ret = 0
    
        elif path.startswith("/usr/"):
            # creating a file in a user dir
            
            # barf if no write permission in dir
            diskPath = "/".join(path.split("/")[:3])
            diskRec = self.files.get(diskPath, None)
            #if not diskRec:
            #    raise IOError(errno.ENOENT, path)
            if diskRec and not diskRec.canwrite:
                self.log("mknod: diskPath=%s" % diskPath)
                raise IOError(errno.EPERM, path)
    
            # create the record
            rec = self.addToCache(path=path, isreg=True, perm=0o644,
                                  iswriting=True, haschanged=True)
            ret = 0
    
            # fall back on host os
            #if S_ISREG(mode):
            #    file(path, "w").close()
            #    ret = 0
    
        else:
            #ret = -EINVAL
            raise IOError(errno.EPERM, path)
    
        self.log("mknod: path=%s mode=0%o dev=%s\n  => %s" % (
                    path, mode, dev, ret))
    
        return ret
    
    #@-node:mknod
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
            raise IOError(errno.ENOENT, path)
    
        for flag in [os.O_WRONLY, os.O_RDWR, os.O_APPEND]:
            if flags & flag:
                self.log("open: setting iswriting for %s" % path)
                rec.iswriting = True
                rec.haschanged = True
    
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
    #@+node:readlink
    def readlink(self, path):
    
        ret = os.readlink(path)
        self.log("readlink: path=%s\n  => %s" % (path, ret))
        return ret
    
    #@-node:readlink
    #@+node:release
    def release(self, path, flags):
    
        rec = self.files.get(path, None)
        if not rec:
            return
    
        filename = os.path.split(path)[1]
    
        # ditch any encoded command files
        if path.startswith("/cmds/"):
            #print "got file %s" % path
            rec = self.files.get(path, None)
            if rec:
                self.delFromCache(rec)
            else:
                print("eh? not in cache")
    
        # if writing, save the thing
        elif rec.iswriting:
            
            self.log("release: %s: iswriting=True" % path)
    
            # what uri?
            rec.iswriting = False
    
            print("Release: path=%s" % path)
    
            if path.startswith("/put/"):
                #@            <<insert to freenet>>
                #@+node:<<insert to freenet>>
                # insert directly to freenet as a key
                
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
                        print("FIXME: not inserting")
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
                            perm=0o444,
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
                
                #@-node:<<insert to freenet>>
                #@nl
    
            elif path.startswith("/usr/"):
                #@            <<write to freedisk>>
                #@+node:<<write to freedisk>>
                # releasing a file being written into a freedisk
                
                bits = path.split("/")
                
                self.log("release: bits=%s" % str(bits))
                
                if bits[0] == '' and bits[1] == 'usr':
                    diskName = bits[2]
                    fileName = bits[3]
                    
                    self.log("diskName=%s fileName=%s" % (diskName, fileName))
                    
                    if fileName == '.privatekey':
                        # written a private key, make the directory writeable
                        parentPath = os.path.split(path)[0]
                        parentRec = self.files[parentPath]
                        parentRec.canwrite = True
                        self.log("release: got privkey, mark dir %s read/write" % parentRec)
                
                    elif fileName == '.cmd':
                        # wrote a command
                
                        self.log("got release of .cmd")
                
                        cmd = rec.data.strip()
                        rec.data = ""
                        
                        self.log("release: cmd=%s" % cmd)
                
                        # execute according to command
                        if cmd == 'commit':
                            self.commitDisk(diskName)
                        elif cmd == 'update':
                            self.updateDisk(diskName)
                        elif cmd == 'merge':
                            self.mergeDisk(diskName)
                
                #@-node:<<write to freedisk>>
                #@nl
    
    
        self.log("release: path=%s flags=%s" % (path, flags))
        return 0
    #@-node:release
    #@+node:rename
    def rename(self, path, path1):
    
        rec = self.files.get(path, None)
        if not rec:
            raise IOError(errno.ENOENT, path)
    
        del self.files[path]
        self.files[path1] = rec
        rec.haschanged = True
        ret = 0
    
        self.log("rename: path=%s path1=%s\n  => %s" % (path, path1, ret))
        return ret
    
    #@-node:rename
    #@+node:rmdir
    def rmdir(self, path):
    
        self.log("rmdir: path=%s" % path)
    
        rec = self.files.get(path, None)
    
        # barf if no such directory
        if not rec:
            raise IOError(errno.ENOENT, path)
    
        # barf if not a directory
        if not rec.isdir:
            raise IOError(errno.ENOTDIR, path)
    
        # barf if not within freedisk mounts
        if not path.startswith("/usr/"):
            raise IOError(errno.EACCES, path)
    
        # seek the freedisk record
        bits = path.split("/")
        diskPath = "/".join(bits[:3])
        diskRec = self.files.get(diskPath, None)
    
        # barf if nonexistent
        if not diskRec:
            raise IOError(errno.ENOENT, path)
    
        # if a freedisk root, just delete
        if path == diskPath:
            # remove directory record
            self.delFromCache(rec)
    
            # and remove children
            for k in list(self.files.keys()):
                if k.startswith(path+"/"):
                    del self.files[k]
    
            return 0
    
        # now, it's a subdir within a freedisk
        
        # barf if non-empty
        if rec.children:
            raise IOError(errno.ENOTEMPTY, path)
        
        # now, at last, can remove
        self.delFromCache(rec)
        ret = 0
    
        self.log("rmdir:   => %s" % ret)
    
        return ret
    
    #@-node:rmdir
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
    #@+node:symlink
    def symlink(self, path, path1):
    
        raise IOError(errno.EPERM, path)
    
        ret = os.symlink(path, path1)
        self.log("symlink: path=%s path1=%s\n  => %s" % (path, path1, ret))
        return ret
    
    #@-node:symlink
    #@+node:truncate
    def truncate(self, path, size):
    
        self.log("truncate: path=%s size=%s" % (path, size))
    
        if not path.startswith("/usr/"):
            raise IOError(errno.EPERM, path)
    
        parentPath, filename = os.path.split(path)
    
        if os.path.split(parentPath)[0] != "/usr":
            raise IOError(errno.EPERM, path)
    
        rec = self.files.get(path, None)
        if not rec:
            raise IOError(errno.ENOENT, path)
    
        # barf at readonly files
        if filename == '.status':
            raise IOError(errno.EPERM, path)
    
        rec.data = ""
        rec.haschanged = True
    
        ret = 0
    
        self.log("truncate:    => %s" % ret)
    
        return ret
    
    #@-node:truncate
    #@+node:unlink
    def unlink(self, path):
    
        self.log("unlink: path=%s" % path)
    
        # remove existing file?
        if path.startswith("/get/") \
        or path.startswith("/put/") \
        or path.startswith("/keys/"):
            rec = self.files.get(path, None)
            if not rec:
                raise IOError(2, path)
            self.delFromCache(rec)
            return 0
    
        if path.startswith("/usr"):
            # remove a file within a freedisk
    
            # barf if nonexistent
            rec = self.files.get(path, None)
            if not rec:
                raise IOError(errno.ENOENT, path)
    
            # barf if removing dir
            if rec.isdir:
                raise IOError(errno.EISDIR, path)
    
            # barf if trying to remove a . control file
            bits = path.split("/")[2:]
            diskPath = "/".join(path.split("/")[:3])
            if len(bits) == 2 and bits[1] in freediskSpecialFiles:
                raise IOError(errno.EACCES, path)
    
            # barf if not on an existing freedisk
            diskRec = self.files.get(diskPath, None)
            if not diskRec:
                raise IOError(errno.ENOENT, path)
    
            # barf if freedisk not writeable
            if not diskRec.canwrite:
                raise IOError(errno.EACCES, path)
    
            # ok to delete
            self.delFromCache(rec)
    
            ret = 0
        else:
            raise IOError(errno.ENOENT, path)
    
        # fallback on host fs
        self.log("unlink:   => %s" % ret)
        return ret
    
    #@-node:unlink
    #@+node:utime
    def utime(self, path, times):
    
        ret = os.utime(path, times)
        self.log("utime: path=%s times=%s\n  => %s" % (path, times, ret))
        return ret
    
    #@-node:utime
    #@+node:write
    def write(self, path, buf, off):
    
        dataLen = len(buf)
    
        rec = self.files.get(path, None)
        if rec:
            # write to existing 'file'
            rec.seek(off)
            rec.write(buf)
            rec.hasdata = True
        else:
            f = open(path, "r+")
            f.seek(off)
            nwritten = f.write(buf)
            f.flush()
    
        self.log("write: path=%s buf=[%s bytes] off=%s" % (path, len(buf), off))
    
        #return nwritten
        return dataLen
    
    #@-node:write
    #@-others
    
    #@-node:fs primitives
    #@+node:freedisk methods
    # methods for freedisk operations
    
    #@+others
    #@+node:setupFreedisks
    def setupFreedisks(self):
        """
        Initialises the freedisks
        """
        self.freedisks = {}
    
    #@-node:setupFreedisks
    #@+node:addDisk
    def addDisk(self, name, uri, passwd):
        """
        Adds (mounts) a freedisk within freenetfs
        
        Arguments:
            - name - name of disk - will be mounted in as /usr/<name>
            - uri - a public or private SSK key URI. Parsing of the key will
              reveal whether it's public or private. If public, the freedisk
              will be mounted read-only. If private, the freedisk will be
              mounted read/write
            - passwd - the encryption password for the disk, or empty string
              if the disk is to be unencrypted
        """
        print("addDisk: name=%s uri=%s passwd=%s" % (name, uri, passwd))
    
        diskPath = "/usr/" + name
        rec = self.addToCache(path=diskPath, isdir=True, perm=0o755, canwrite=True)
        disk = Freedisk(rec)
        self.freedisks[name] = disk
    
        if uriIsPrivate(uri):
            privKey = uri
            pubKey = self.node.invertprivate(uri)
        else:
            privKey = None
            pubKey = uri
        
        disk.privKey = privKey
        disk.pubKey = pubKey
    
        #print "addDisk: done"
    
    #@-node:addDisk
    #@+node:delDisk
    def delDisk(self, name):
        """
        drops a freedisk mount
        
        Arguments:
            - name - the name of the disk
        """
        diskPath = "/usr/" + name
        rec = self.freedisks.pop(diskPath)
        self.delFromCache(rec)
    
    #@-node:delDisk
    #@+node:commitDisk
    def commitDisk(self, name):
        """
        synchronises a freedisk TO freenet
        
        Arguments:
            - name - the name of the disk
        """
        self.log("commitDisk: disk=%s" % name)
    
        startTime = time.time()
    
        # get the freedisk root's record, barf if nonexistent
        diskRec = self.freedisks.get(name, None)
        if not diskRec:
            self.log("commitDisk: no such disk '%s'" % name)
            return "No such disk '%s'" % name
    
        # and the file record and path
        rootRec = diskRec.root
        rootPath = rootRec.path
    
        # get private key, if any
        privKey = diskRec.privKey
        if not privKey:
            # no private key - disk was mounted readonly with only a pubkey
            raise IOError(errno.EIO, "Disk %s is read-only" % name)
        
        # and pubkey
        pubKey = diskRec.pubKey
    
        # process the private key to needed format
        privKey = privKey.split("freenet:")[-1]
        privKey = privKey.replace("SSK@", "USK@").split("/")[0] + "/" + name + "/0"
    
        self.log("commit: privKey=%s" % privKey)
    
        self.log("commitDisk: checking files in %s" % rootPath)
    
        # update status
        #statusFile.data = "committing\nAnalysing files\n"
    
        # get list of records of files within this freedisk
        fileRecs = []
        for f in list(self.files.keys()):
            # is file/dir within the freedisk?
            if f.startswith(rootPath+"/"):
                # yes, get its record
                fileRec = self.files[f]
    
                # is it a file, and not a special file?
                if fileRec.isfile \
                and (os.path.split(f)[1] not in freediskSpecialFiles):
                    # yes, grab it
                    fileRecs.append(fileRec)
    
        # now sort them by path
        fileRecs.sort(lambda r1, r2: cmp(r1.path, r2.path))
    
        # make sure we have a node to talk to
        self.connectToNode()
        node = self.node
    
        # determine CHKs for all these jobs
        for rec in fileRecs:
            rec.mimetype = guessMimetype(rec.path)
            rec.uri = node.put(
                "CHK@file",
                data=rec.data,
                chkonly=True,
                mimetype=rec.mimetype)
        
        # now insert all these files
        maxJobs = 5
        jobsWaiting = fileRecs[:]
        jobsRunning = []
        jobsDone = []
    
        # now, create the manifest XML file
        manifest = XMLFile(root="freedisk")
        root = manifest.root
        for rec in jobsWaiting:
            fileNode = root._addNode("file")
            fileNode.path = rec.path
            fileNode.uri = rec.uri
            try:
                fileNode.mimetype = rec.mimetype
            except:
                fileNode.mimetype = "text/plain"
            fileNode.hash = sha1(rec.data).hexdigest()
    
        # and create an index.html to make it freesite-compatible
        indexLines = [
            "<html><head><title>This is a freedisk</title></head><body>",
            "<h1>freedisk: %s" % name,
            "<table cellspacing=0 cellpadding=3 border=1>"
            "<tr>",
            "<td><b>Size</b></td>",
            "<td><b>Filename</b></td>",
            "<td><b>URI</b></td>",
            "</tr>",
            ]
        for rec in fileRecs:
            indexLines.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                rec.size, rec.path, rec.uri))
        indexLines.append("</table></body></html>\n")
        indexHtml = "\n".join(indexLines)
    
        # and add the manifest as a waiting job
        manifestJob = node.put(
            privKey,
            data=manifest.toxml(),
            mimetype="text/xml",
            **{"async": True}
            )
    
        #jobsRunning.append(manifestJob)
        #manifestUri = manifestJob.wait()
        #print "manifestUri=%s" % manifestUri
        #time.sleep(6)
    
        # the big insert/wait loop
        while jobsWaiting or jobsRunning:
            nWaiting = len(jobsWaiting)
            nRunning = len(jobsRunning)
            self.log("commit: %s waiting, %s running" % (nWaiting,nRunning))
    
            # launch jobs, if available, and if spare slots
            while len(jobsRunning) < maxJobs and jobsWaiting:
    
                rec = jobsWaiting.pop(0)
    
                # if record has data, insert it, otherwise take as done            
                if rec.hasdata:
                    uri = rec.uri
                    if not uri:
                        uri = "CHK@somefile" + os.path.splitext(rec.path)[1]
                    job = node.put(uri, data=rec.data, **{"async": True})
                    rec.job = job
                    jobsRunning.append(rec)
                else:
                    # record should already have the hash, uri, mimetype
                    jobsDone.append(rec)
    
            # check running jobs
            for rec in jobsRunning:
                if rec == manifestJob:
                    job = rec
                else:
                    job = rec.job
    
                if job.isComplete():
                    jobsRunning.remove(rec)
    
                    uri = job.wait()
    
                    if job != manifestJob:
                        rec.uri = uri
                        rec.job = None
                        jobsDone.append(rec)
    
            # breathe!!
            if jobsRunning:
                time.sleep(5)
            else:
                time.sleep(1)
    
        manifestUri = manifestJob.wait()
        self.log("commitDisk: done, manifestUri=%s" % manifestUri)
    
        #pubKeyFile.data = manifestJob.uri
    
        endTime = time.time()
        commitTime = endTime - startTime
    
        self.log("commitDisk: commit completed in %s seconds" % commitTime)
    
        return manifestUri
    
    #@-node:commitDisk
    #@+node:updateDisk
    def updateDisk(self, name):
        """
        synchronises a freedisk FROM freenet
        
        Arguments:
            - name - the name of the disk
        """
        self.log("updateDisk: disk=%s" % name)
    
        startTime = time.time()
    
        # get the freedisk root's record, barf if nonexistent
        diskRec = self.freedisks.get(name, None)
        if not diskRec:
            self.log("commitDisk: no such disk '%s'" % name)
            return "No such disk '%s'" % name
        
        rootRec = diskRec.root
    
        # and get the public key, sans 'freenet:'
        pubKey = rootRec.pubKey
        
        pubKey = pubKey.split("freenet:")[-1]
    
        # process further
        pubKey = privKey.replace("SSK@", "USK@").split("/")[0] + "/" + name + "/0"
    
        self.log("update: pubKey=%s" % pubKey)
    
        # fetch manifest
    
        # mark disk as readonly
            
        # for each entry in manifest
        #     if not localfile has changed
        #         replace the file record
    
    #@-node:updateDisk
    #@+node:getManifest
    def getManifest(self, name):
        """
        Retrieves the manifest of a given disk
        """
    #@-node:getManifest
    #@+node:putManifest
    def putManifest(self, name):
        """
        Inserts a freedisk manifest into freenet
        """
    #@-node:putManifest
    #@-others
    
    #@-node:freedisk methods
    #@+node:util methods
    # utility methods
    
    #@+others
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
                perm |= 0o666
                size = 1024
            else:
                # by default, it's a regular file
                isReg = True
    
            # create permissions field
            if isDir:
                perm |= 0o755
                size = 2
            else:
                perm |= 0o444
    
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
        
        #self.verbosity = fcp.DETAIL
    
        self.log("connectToNode: verbosity=%s" % self.verbosity)
    
        try:
            self.node = fcp.FCPNode(host=self.fcpHost,
                                    port=self.fcpPort,
                                    verbosity=self.verbosity)
        except:
            raise IOError(errno.EIO, "Failed to reach FCP service at %s:%s" % (
                            self.fcpHost, self.fcpPort))
    
        #self.log("pubkey=%s" % self.pubkey)
        #self.log("privkey=%s" % self.privkey)
        #self.log("cachedir=%s" % self.cachedir)
    
    #@-node:connectToNode
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
    #@+node:hashpath
    def hashpath(self, path):
        
        return sha1(path).hexdigest()
    
    #@-node:hashpath
    #@+node:addToCache
    def addToCache(self, rec=None, **kw):
        """
        Tries to 'cache' a given file/dir record, and
        adds it to parent dir
        """
        if rec == None:
            rec = FileRecord(self, **kw)
    
        path = rec.path
    
        # barf if file/dir already exists
        if path in self.files:
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
        if isinstance(rec, str):
            path = rec
            rec = self.files.get(path, None)
            if not rec:
                print("delFromCache: no such path %s" % path)
                return
        else:
            path = rec.path
    
        parentPath = os.path.split(path)[0]
        
        if path in self.files:
            rec = self.files[path]
            del self.files[path]
            for child in rec.children:
                self.delFromCache(child)
        
        parentRec = self.files.get(parentPath, None)
        if parentRec:
            parentRec.delChild(rec)
    
    #@-node:delFromCache
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
        print("statToDict: info=%s" % str(info))
    
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
    #@+node:log
    def log(self, msg):
        #if not quiet:
        #    print "freedisk:"+msg
        file("/tmp/freedisk.log", "a").write(msg+"\n")
    
    #@-node:log
    #@-others
    
    #@-node:util methods
    #@+node:deprecated methods
    # deprecated methods
    
    #@+others
    #@+node:__getDirStat
    def __getDirStat(self, path):
        """
        returns a stat tuple for given path
        """
        return FileRecord(mode=0o700, path=path, isdir=True)
    
    #@-node:__getDirStat
    #@+node:_loadConfig
    def _loadConfig(self):
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
        for line in [l.strip() for l in file(self.config).readlines()]:
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
        if "privkey" in opts:
    
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
                self.log("Creating cache directory %s" % self.cachedir)
                os.makedirs(self.cachedir)
                #raise hell
        except:
            raise Exception("config file %s: missing or invalid cache directory" \
                            % self.configfile)
    
    #@-node:_loadConfig
    #@-others
    
    #@-node:deprecated methods
    #@-others

#@-node:class FreenetBaseFS
#@+node:class Freedisk
class Freedisk:
    """
    Encapsulates a freedisk
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, rootrec):
        
        self.root = rootrec
    
    #@-node:__init__
    #@-others

#@-node:class Freedisk
#@+node:class FreenetFuseFS
class FreenetFuseFS(FreenetBaseFS):
    """
    Interfaces with FUSE
    """
    #@    @+others
    #@+node:attribs
    _attrs = ['getattr', 'readlink', 'getdir', 'mknod', 'mkdir',
          'unlink', 'rmdir', 'symlink', 'rename', 'link', 'chmod',
          'chown', 'truncate', 'utime', 'open', 'read', 'write', 'release',
          'statfs', 'fsync']
    
    #@-node:attribs
    #@+node:run
    def run(self):
    
        import _fuse
    
        d = {'mountpoint': self.mountpoint,
             'multithreaded': self.multithreaded,
             }
    
        #print "run: d=%s" % str(d)
    
        if self.debug:
            d['lopts'] = 'debug'
    
        k=[]
        for opt in ['allow_other', 'kernel_cache']:
            if getattr(self, opt):
                k.append(opt)
        if k:
            d['kopts'] = ",".join(k)
    
        for a in self._attrs:
            if hasattr(self,a):
                d[a] = ErrnoWrapper(getattr(self, a))
    
        #thread.start_new_thread(self.tickThread, ())
    
        _fuse.main(**d)
    
    #@-node:run
    #@+node:GetContent
    def GetContext(self):
        print("GetContext: called")
        return _fuse.FuseGetContext(self)
    
    #@-node:GetContent
    #@+node:Invalidate
    def Invalidate(self, path):
        print("Invalidate: called")
        return _fuse.FuseInvalidate(self, path)
    
    #@-node:Invalidate
    #@+node:tickThread
    def tickThread(self, *args, **kw):
        
        print("tickThread: starting")
        i = 0
        while True:
            print("tickThread: n=%s" % i)
            time.sleep(10)
            i += 1
    
    #@-node:tickThread
    #@-others
#@-node:class FreenetFuseFS
#@+node:class FileRecord
class FileRecord(list):
    """
    Encapsulates the info for a file, and can
    be returned by getattr
    """
    #@    @+others
    #@+node:attribs
    # default attribs, can be overwritten by constructor keywords
    haschanged = False
    hasdata = False
    canwrite = False
    iswriting = False
    uri = None
    
    #@-node:attribs
    #@+node:__init__
    def __init__(self, fs, statrec=None, **kw):
        """
        """
        # copy keywords cos we'll be popping them
        kw = dict(kw)
    
        # save fs ref
        self.fs = fs
    
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
        mode = kw.pop('mode', 0)
        if kw.pop('isdir', False):
            mode |= stat.S_IFDIR
        if kw.pop('ischr', False):
            mode |= stat.S_IFCHR
        if kw.pop('isblk', False):
            mode |= stat.S_IFBLK
        if kw.pop('isreg', False):
            mode |= stat.S_IFREG
        if kw.pop('isfifo', False):
            mode |= stat.S_IFIFO
        if kw.pop('islink', False):
            mode |= stat.S_IFLNK
        if kw.pop('issock', False):
            mode |= stat.S_IFSOCK
    
        # handle non-file-related keywords
        perm = kw.pop('perm', 0)
        mode |= perm
    
        # set path
        path = kw.pop('path')
        self.path = path
    
        # set up data stream
        if "data" in kw:
            self.stream = StringIO(kw.pop('data'))
            self.hasdata = True
        else:
            self.stream = StringIO()
        
        # find parent, if any
        if path == '/':
            self.parent = None
        else:
            parentPath = os.path.split(path)[0]
            parentRec = fs.files[parentPath]
            self.parent = parentRec
    
        # child files/dirs
        self.children = []
        
        # get inode number
        inode = pathToInode(path)
        
        #size = kw.get('size', 0)
        now = timeNow()
        atime = kw.pop('atime', now)
        mtime = kw.pop('mtime', now)
        ctime = kw.pop('ctime', now)
    
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
    
        # throw remaining keywords into instance's attribs
        self.__dict__.update(kw)
    
        # finally, parent constructor, now that we have a complete stat list
        list.__init__(self, statrec)
    
        if self.isdir:
            self.size = 2
    
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
    
        if attr in ['isreg', 'isfile']:
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
        elif attr in ['isreg', 'isfile']:
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
    
        #print "addChild: path=%s size=%s" % (self.path, self.size)
    
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
            print("eh? trying to remove %s from %s" % (rec.path, self.path))
    
        #print "delChild: path=%s size=%s" % (self.path, self.size)
    
    #@-node:delChild
    #@-others

#@-node:class FileRecord
#@+node:class FreediskMgr
class FreediskMgr:
    """
    Gateway for mirroring a local directory to/from freenet
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, **kw):
        """
        Creates a freediskmgr object
        
        Keywords:
            - name - mandatory - the name of the disk
            - fcpNode - mandatory - an FCPNode instance
            - root - mandatory - the root directory
            - publicKey - the freenet public key URI
            - privateKey - the freenet private key URI
        Notes:
            - exactly one of publicKey, privateKey keywords must be given
        """
    
    #@-node:__init__
    #@+node:update
    def update(self):
        """
        Update from freenet to local directory
        """
    
    #@-node:update
    #@+node:commit
    def commit(self):
        """
        commit from local directory into freenet
        """
    
    #@-node:commit
    #@-others

#@-node:class FreediskMgr
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
    inode = int(md5(path).hexdigest()[:7], 16)
    
    # and ensure it's unique
    while inode in inodes:
        inode += 1

    # register it
    inodes[path] = inode

    # done
    return inode
    
#@-node:pathToInode
#@+node:timeNow
def timeNow():
    return int(time.time()) & 0xffffffff

#@-node:timeNow
#@+node:usage
def usage(msg, ret=1):

    print("Usage: %s mountpoint -o args" % progname)

    sys.exit(ret)

#@-node:usage
#@+node:main
def main():

    kw = {}
    args = []

    if argc != 5:
        usage("Bad argument count")

    mountpoint = argv[2]

    for o in argv[4].split(","):
        try:
            k, v = o.split("=", 1)
            kw[k] = v
        except:
            args.append(o)

    kw['multithreaded'] = True
    #kw['multithreaded'] = False
    print("main: kw=%s" % str(kw))
    

    if os.fork() == 0:
        server = FreenetFuseFS(mountpoint, *args, **kw)
        server.run()


#@-node:main
#@+node:mainline
if __name__ == '__main__':

    main()
#@-node:mainline
#@-others

#@-node:@file freenetfs.py
#@-leo
