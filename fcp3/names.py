#@+leo-ver=4
#@+node:@file names.py
"""
Perform namesite operations
"""

#@+others
#@+node:imports
import sys, os, getopt, traceback, mimetypes, time

from . import node

#@-node:imports
#@+node:globals
progname = sys.argv[0]

#@-node:globals
#@+node:class NamesMgr
class NamesMgr:
    """
    """
    #@    @+others
    #@+node:synonyms
    synonyms = {"addservice" : "newservice",
                "listservice" : "listservices",
                }
        
    #@-node:synonyms
    #@+node:__init__
    def __init__(self, node):
        """
        Create a command interface for names service
        """
        self.node = node
    
    #@-node:__init__
    #@+node:execute
    def execute(self, cmd, *args):
        """
        executes command with args
        """
        cmd = self.synonyms.get(cmd, cmd)
    
        method = getattr(self, "cmd_"+cmd, None)
        if not method:
            usage("unrecognised command '%s'" % cmd)
        return method(*args)
    
    
    #@-node:execute
    #@+node:cmd_help
    def cmd_help(self, *args):
        
        help()
        sys.exit(0)
    
    #@-node:cmd_help
    #@+node:cmd_newservice
    def cmd_newservice(self, *args):
        """
        Creates a new local name service
        """
        #print "cmd_newservice %s" % repr(args)
    
        nargs = len(args)
    
        if nargs not in [1, 2]:
            usage("newservice: bad argument count")
        
        name = args[0]
        if len(args) == 2:
            priv = args[1]
            pub = self.node.invertkey(priv)
        else:
            pub, priv = self.node.genkey()
    
        pub = self.node.namesiteProcessUri(pub)
        priv = self.node.namesiteProcessUri(priv)
    
        self.node.namesiteAddLocal(name, priv)
    
        print(pub)
    
    #@-node:cmd_newservice
    #@+node:cmd_delservice
    def cmd_delservice(self, *args):
        """
        delservice <name>
        
        Remove local service <name> and deletes its records
        """
        #print "cmd_delservice %s" % repr(args)
    
        nargs = len(args)
    
        if nargs != 1:
            usage("delservice: bad argument count")
        
        name = args[0]
    
        self.node.namesiteDelLocal(name)
    
    #@-node:cmd_delservice
    #@+node:cmd_listservices
    def cmd_listservices(self):
        """
        Print a list of services as 'name uri' lines
        """
        for rec in self.node.namesiteLocals:
            print("%s %s" % (rec['name'], rec['puburi']))
    
    #@-node:cmd_listservices
    #@+node:cmd_dumpservice
    def cmd_dumpservice(self, *args):
        """
        Dumps out all records for given service
        """
        nargs = len(args)
        
        if nargs != 1:
            usage("dumpservice: bad argument count")
        
        name = args[0]
        
        for rec in self.node.namesiteLocals:
            if rec['name'] == name:
                for k,v in list(rec['cache'].items()):
                    print("%s %s" % (k, v))
    
    #@-node:cmd_dumpservice
    #@+node:cmd_addpeer
    def cmd_addpeer(self, *args):
        """
        addpeer <name> <uri>
    
        Adds a peer name service
        """
        #print "cmd_addpeer %s" % repr(args)
    
        nargs = len(args)
        
        if nargs != 2:
            usage("addpeer: bad argument count")
        
        name, uri = args
        
        self.node.namesiteAddPeer(name, uri)
    
    #@-node:cmd_addpeer
    #@+node:cmd_delpeer
    def cmd_delpeer(self, *args):
        """
        delpeer <name>
    
        Remove peer name service <name>
        """
        #print "cmd_delpeer %s" % repr(args)
    
        nargs = len(args)
        
        if nargs != 1:
            usage("delpeer: bad argument count")
        
        name = args[0]
        
        self.node.namesiteRemovePeer(name)
    
    #@-node:cmd_delpeer
    #@+node:cmd_listpeers
    def cmd_listpeers(self):
        """
        Prints a list of peers and their URIs
        """
        for rec in self.node.namesitePeers:
            print("%s %s" % (rec['name'], rec['puburi']))
    
    #@-node:cmd_listpeers
    #@+node:cmd_addrecord
    def cmd_addrecord(self, *args):
        """
        addrecord <service> <sitename> <uri>
    
        Add to local service <service> a record mapping <sitename> to <uri>
        """
        #print "cmd_addrecord %s" % repr(args)
    
        nargs = len(args)
        if nargs != 3:
            usage("addrecord: bad argument count")
        
        localname, domain, uri = args
    
        self.node.namesiteAddRecord(localname, domain, uri)
    
    #@-node:cmd_addrecord
    #@+node:cmd_delrecord
    def cmd_delrecord(self, *args):
        """
        delrecord <service> <sitename>
    
        Remove from local service <service> the record for name <sitename>
        """
        #print "cmd_delrecord %s" % repr(args)
    
        nargs = len(args)
        if nargs != 2:
            usage("delrecord: bad argument count")
        
        service, sitename = args
    
        self.node.namesiteDelRecord(service, sitename)
    
    #@-node:cmd_delrecord
    #@+node:cmd_reinsertservice
    def cmd_reinsertservice(self, *args):
        """
        Forces a reinsert of all records for given service
        """
        nargs = len(args)
        
        if nargs != 1:
            usage("dumpservice: bad argument count")
        
        name = args[0]
        
        for r in self.node.namesiteLocals:
            if r['name'] == name:
                rec = r
                break
        if not rec:
            return
        
        for domain,uri in list(rec['cache'].items()):
            # reinsert each record
    
            # determine the insert uri
            localPrivUri = rec['privuri'] + "/" + domain + "/0"
    
            # and stick it in, via global queue
            id = "namesite|%s|%s|%s" % (name, domain, int(time.time()))
            # Data sent over FCP should be byte encoded.
            encodedUri = uri.encode('utf-8')
            self.node.put(
                localPrivUri,
                id=id,
                data=encodedUri,
                persistence="forever",
                Global=True,
                priority=0,
                **{"async": True}
                )
    
        self.node.refreshPersistentRequests()
    
    #@-node:cmd_reinsertservice
    #@+node:cmd_verifyservice
    def cmd_verifyservice(self, *args):
        """
        Tries to retrieve all the records of a given service
        """
        nargs = len(args)
        
        if nargs != 1:
            usage("dumpservice: bad argument count")
        
        name = args[0]
    
        rec = None    
        for r in self.node.namesiteLocals:
            if r['name'] == name:
                rec = r
                break
        if not rec:
            usage("No local service called '%s'" % name)
    
        ntotal = 0
        nsuccessful = 0
        nfailed = 0
        nincorrect = 0
    
        for domain,uri in list(rec['cache'].items()):
    
            ntotal += 1
    
            # retrieve each record
    
            # determine the insert uri
            localPubUri = rec['puburi'] + "/" + domain + "/0"
            
            print(("Trying to retrieve record %s..." % domain), end=' ')
    
            try:
                mimetype, data = recUri = self.node.get(localPubUri, priority=0)
                if data == uri:
                    print("  successful!")
                    nsuccessful += 1
                else:
                    print("  incorrect! :(")
                    nincorrect += 1
            except:
                print("  failed to fetch")
                nfailed += 1
    
        print("Result: total=%s successful=%s failed=%s" % (
            ntotal, nsuccessful, nfailed+nincorrect))
    
    #@-node:cmd_verifyservice
    #@+node:cmd_lookup
    def cmd_lookup(self, *args):
        """
        lookup <name>
    
        look up <name>, and print its target uri
        """
        #print "cmd_lookup %s" % repr(args)
    
        if len(args) != 1:
            usage("Syntax: lookup <domainname>")
    
        domain = args[0]
        
        uri = self.node.namesiteLookup(domain)
        if uri:
            print(uri)
        else:
            return 1
    
    #@-node:cmd_lookup
    #@-others

#@-node:class NamesMgr
#@+node:usage
def usage(msg=None, ret=1):
    """
    Prints usage message then exits
    """
    if msg:
        sys.stderr.write(msg+"\n")
    sys.stderr.write("Usage: %s [options]\n" % progname)
    sys.stderr.write("Type '%s -h' for help\n" % progname)
    sys.exit(ret)

#@-node:usage
#@+node:help
def help():
    """
    print help options, then exit
    """
    print("%s: operate on pyFreenet 'namesites'"  % progname)
    print()
    print("Usage: %s [options]" % progname)
    print()
    print("Options:")
    print("  -h, -?, --help")
    print("     Print this help message")
    print("  -v, --verbose")
    print("     Print verbose progress messages to stderr")
    print("  -H, --fcpHost=<hostname>")
    print("     Connect to FCP service at host <hostname>")
    print("  -P, --fcpPort=<portnum>")
    print("     Connect to FCP service at port <portnum>")
    print("  -V, --version")
    print("     Print version number and exit")
    print()
    print("Commands:")
    print("  newservice <name> [<privuri>]")
    print("     create a new local service")
    print("  delservice <name>")
    print("     remove local service <name> and delete its records")
    print("  listservices")
    print("     print details for local services as '<name> <uri>' lines,")
    print("     so that peers can 'addpeer' one or more of these")
    print("  dumpservice <name>")
    print("     print a list of records in local name service <name>, as a")
    print("     set of lines in the form '<name> <targetURI>'")
    print("  reinsertservice <name>")
    print("     reinsert all records of local service <name> - USE ONLY IF DESPERATE")
    print("  verifyservice <name>")
    print("     retrieves all records of local service <name> to check")
    print("     retrievability and accuracy")
    print("  addpeer <name> <uri>")
    print("     Adds a peer name service")
    print("  delpeer <name>")
    print("     Remove peer name service <name>")
    print("  listpeers")
    print("     Print a list of registered peer namesites, as '<name> <uri>' lines")
    print("  addrecord <service> <sitename> <uri>")
    print("     Add to local service <service> a record mapping <sitename> to <uri>")
    print("  delrecord <service> <sitename>")
    print("    Remove from local service <service> the record for name <name>")
    print("  lookup <name>")
    print("     look up <name>, and print its target uri")
    print()
    print("Environment:")
    print("  Instead of specifying -H and/or -P, you can define the environment")
    print("  variables FCP_HOST and/or FCP_PORT respectively")

    sys.exit(0)

#@-node:help
#@+node:main
def main():
    """
    Front end for fcpget utility
    """
    # default job options
    verbosity = node.ERROR
    verbose = False
    fcpHost = node.defaultFCPHost
    fcpPort = node.defaultFCPPort
    mimetype = None
    cfgfile = None

    opts = {
            "Verbosity" : 0,
            }

    # process command line switches
    try:
        cmdopts, args = getopt.getopt(
            sys.argv[1:],
            "?hvH:P:Vc:",
            ["help", "verbose", "fcpHost=", "fcpPort=", "version",
             "config-file=",
             ]
            )
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    output = None
    verbose = False
    #print cmdopts
    for o, a in cmdopts:

        if o in ("-?", "-h", "--help"):
            help()

        if o in ("-V", "--version"):
            print("This is %s, version %s" % (progname, node.fcpVersion))
            sys.exit(0)

        if o in ("-c", "--config-file"):
            cfgfile = a

        if o in ("-v", "--verbosity"):
            verbosity = node.DETAIL
            opts['Verbosity'] = 1023
            verbose = True

        if o in ("-H", "--fcpHost"):
            fcpHost = a
        
        if o in ("-P", "--fcpPort"):
            try:
                fcpPort = int(a)
            except:
                usage("Invalid fcpPort argument %s" % repr(a))

    # try to create the node
    try:
        n = node.FCPNode(host=fcpHost, port=fcpPort, verbosity=verbosity,
                         logfile=sys.stderr,
                         namesitefile=cfgfile)
    except:
        if verbose:
            traceback.print_exc(file=sys.stderr)
        usage("Failed to connect to FCP service at %s:%s" % (fcpHost, fcpPort))

    if len(args) < 1:
        usage("No command specified")

    mgr = NamesMgr(n)
    res = mgr.execute(*args)

    n.shutdown()
    if res:
        sys.exit(1)
    else:
        sys.exit(0)

#@-node:main
#@-others

#@-node:@file names.py
#@-leo
