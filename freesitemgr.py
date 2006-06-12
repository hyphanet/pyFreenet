#!/usr/bin/env python
#@+leo-ver=4
#@+node:@file freesitemgr.py
#@@first
#@+others
#@+node:freesitemgr-script
"""
A utility to update freesites from within a cron environment
"""
#@+others
#@+node:imports
import sys, os, time, commands, traceback, getopt

import fcp.node
from fcp.sitemgr import SiteMgr, fixUri

#@-node:imports
#@+node:globals
progname = sys.argv[0]

# time we wait after starting fred, to allow the node to 'warm up'
# and make connections to its peers
startupTime = 180

# directory where we have freenet installed,
# change it as needed
#freenetDir = "/home/david/freenet"

homeDir = os.path.expanduser("~")

# derive path of freenet pid file, the (non)existence
# of which is the easiest test of whether the freenet
# node is running
#freenetPidFile = os.path.join(freenetDir, "Freenet.pid")

logFile = os.path.join(homeDir, "updatesites.log")
pidFile = os.path.join(homeDir, "updatesites.pid")

if sys.platform.startswith("win"):
    confDirName = "freesitemgr"
else:
    confDirName = ".freesitemgr"
confDir = os.path.join(homeDir, confDirName)

#@-node:globals
#@+node:editCreateConfig
def editCreateConfig(sitemgr):
    """
    Creates an initial config file interactively
    """
    print "Setting up configuration file %s" % sitemgr.conffile

    # get fcp hostname
    fcpHost = raw_input("FCP Hostname [%s] (* for all): " % sitemgr.fcpHost).strip()
    if not fcpHost:
        fcpHost = sitemgr.fcpHost
    if fcpHost == '*':
        fcpHost = ""
    
    # get fcp port
    while 1:
        fcpPort = raw_input("FCP Port [%s]: " % sitemgr.fcpPort).strip()
        if not fcpPort:
            fcpPort = sitemgr.fcpPort
        try:
            fcpPort = int(fcpPort)
        except:
            continue
        break

    print "Trying FCP port at %s:%s" % (fcpHost, fcpPort)
    try:
        fcpnode = fcp.FCPNode(host=fcpHost, port=fcpPort)
    except Exception, e:
        print "Failed to connect to FCP Port: %s" % e
        print "Please ensure your node is running, with its FCP port"
        print "reachable at %s:%s, and try this command again" % (fcpHost, fcpPort)
        print "Setup aborted"
        return
    fcpnode.shutdown()

    sitemgr.fcpHost = fcpHost
    sitemgr.fcpPort = fcpPort

    # confirm and save
    if getyesno("Save configuration", True):
        sitemgr.save()

    print "Configuration saved to %s" % sitemgr.conffile

#@-node:editCreateConfig
#@+node:addSite
def addSite(sitemgr):
    """
    Interactively adds a new site to config
    """
    print "Add new site"
    
    if not sitemgr.node:
        print "Cannot add site - no contact with node on %s:%s" % (
            sitemgr.fcpHost, sitemgr.fcpPort)
        print "Please ensure your freenet node is running, or run"
        print "'%s setup' to edit your FCP access address" % progname

    while 1:
        sitename = raw_input("Name of freesite, or empty line to cancel: ").strip()
        if not sitename:
            print "Add site aborted"
            return
        elif sitemgr.hasSite(sitename):
            print "Freesite '%s' already exists" % sitename
            continue
        break

    while 1:
        sitedir = raw_input("Directory where freesite's files reside: ").strip()
        if not sitedir:
            print "Add site aborted"
            return
        sitedir = os.path.abspath(sitedir)
        if not os.path.isdir(sitedir):
            print "'%s' is not a directory, try again" % sitedir
            continue
        #elif not os.path.isfile(os.path.join(sitedir, "index.html")):
        #    print "'%s' has no index.html, try again" % sitedir
        #    continue
        break

    while 1:
        uriPriv = raw_input("Site private URI (if any - press ENTER for new\n: ").strip()
        if not uriPriv:
            uriPub, uriPriv = sitemgr.node.genkey()
        else:
            try:
                uriPub = sitemgr.node.invertprivate(uriPriv)
            except:
                traceback.print_exc()
                print "Invalid private URI:\n  %s" % uriPriv
                continue
        break
        uriPub = fixUri(uriPub, sitename)
        uriPriv = fixUri(uriPriv, sitename)
    
    # good to go - add the site
    sitemgr.addSite(name=sitename, dir=sitedir, uriPub=uriPub, uriPriv=uriPriv)

    print "Added new freesite: '%s' => %s" % (sitename, sitedir)

#@-node:addSite
#@+node:removeSite
def removeSite(sitemgr, sitename):
    """
    tries to remove site from config
    """
    if not sitemgr.hasSite(sitename):
        print "No such freesite '%s'" % sitename
        return

    if getyesno("Are you sure you wish to delete freesite '%s'" % sitename, False):
        sitemgr.removeSite(sitename)
        print "Removed freesite '%s'" % sitename
    else:
        print "Freesite deletion aborted"

#@-node:removeSite
#@+node:getYesNo
def getyesno(ques, default=False):
    """
    prompt for yes/no answer, with default
    """
    if default:
        prmt = "[Y/n]"
    else:
        prmt = "[y/N]"
        
    resp = raw_input(ques + " " + prmt + " ").strip().lower()
    
    if not resp:
        return default
    elif resp[0] in ['y', 't']:
        return True
    else:
        return False
#@-node:getYesNo
#@+node:help
def help():
    """
    dump help info and exit
    """
    print "%s: a console-based USK freesite insertion utility" % progname
    
    print "Usage: %s [options] <command> <args>" % progname
    print "Options:"
    print "  -h, --help"
    print "          - display this help message"
    print "  -c, --config-dir=path"
    print "          - use different config directory (default is %s)" % confDir
    print "  -v, --verbose"
    print "          - run verbosely, set this twice for even more noise"
    print "  -q, --quiet"
    print "          - run quietly"
    print "  -l, --logfile=filename"
    print "          - location of logfile (default %s)" % logFile
    print "  -m, --max-concurrent"
    print "          - default 10, takes effect if -s and -a are set"
    print "            limits the number of simultaneous file inserts,"
    print "            to avoid unduly thrashing the node"
    print "            setting this option also sets -s and -a"
    print "  -r, --priority"
    print "     Set the priority (0 highest, 6 lowest, default 4)"
    print "     of 'forever', so the insert will resume if the node crashes"
    print
    print "Available Commands:"
    print "  setup          - create/edit freesite config file interactively"
    print "  add            - add new freesite called <name> using directory <dir>"
    print "  list [<name>]  - display a summary of all freesites, or a"
    print "                   detailed report of one site if <name> given"
    print "  remove <name>  - remove given freesite"
    print "  update         - reinsert any freesites which have changed since"
    print "                   they were last inserted"

#@-node:help
#@+node:usage
def usage(ret=-1, msg=None):
    if msg != None:
        print msg
    print "Usage: %s [options] <command> [<arguments>]" % progname
    print "Do '%s -h' for help" % progname

    sys.exit(ret)

#@-node:usage
#@+node:noNodeError
def noNodeError(sitemgr, msg):
    print msg + ": cannot connect to node FCP port"
    print "To use this command, you must have a freenet node running"
    print "Please ensure your node FCP port is reachable at %s:%s" % (
        sitemgr.fcpHost, sitemgr.fcpPort)
    print "or run '%s setup' to configure a different FCP port" % progname
    sys.exit(1)

#@-node:noNodeError
#@+node:main
def main():

    # default job options
    opts = {
            "verbosity" : fcp.node.ERROR,
            "Verbosity" : 0,
            #"logfile" : logFile,
            'priority' : 3,
            }

    # process command line switches
    try:
        cmdopts, args = getopt.getopt(
            sys.argv[1:],
            "?hvc:l:m:r:",
            ["help", "verbose", "config-dir=", "logfile=",
             "max-concurrent=",
             "priority",
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
            sys.exit(0)

        if o in ("-v", "--verbosity"):
            opts['verbosity'] += 1
            opts['Verbosity'] = 1023
        
        if o in ("-q", "--quiet"):
            opts['verbosity'] = fcp.node.SILENT
        
        if o in ("-c", "--config-dir"):
            opts['configdir'] = a
        
        if o in ("-l", "--logfile"):
            opts['logfile'] = a
        
        if o in ("-m", "--max-concurrent"):
            opts['maxconcurrent'] = int(a)

        if o in ("-r", "--priority"):
            try:
                pri = int(a)
                if pri < 0 or pri > 6:
                    raise hell
            except:
                usage("Invalid priority '%s'" % pri)
            opts['priority'] = int(a)

    # process command
    if len(args) < 1:
        usage(msg="No command given")

    cmd = args.pop(0)

    if cmd not in [
            'setup','config','init',
            'add',
            'remove',
            'list',
            'update'
            ]:    
        usage(msg="Unrecognised command '%s'" % cmd)

    # we now have a likely valid command, so now we need a sitemgr
    sitemgr = SiteMgr(**opts)

    if cmd in ['setup', 'init', 'config']:
        editCreateConfig(sitemgr)

    elif cmd == 'add':
        if not sitemgr.node:
            noNodeError(sitemgr, "Cannot add site")
        addSite(sitemgr)

    elif cmd == 'remove':
        if not args:
            print "Remove site: no freesites selected"
            return
        for sitename in args:
            removeSite(sitemgr, sitename)
        pass
        print "Removed freesites: " + " ".join(args)

    elif cmd == 'list':
        if not args:
            # summary list
            print " ".join(sitemgr.getSiteNames())
        else:
            for sitename in args:
                if not sitemgr.hasSite(sitename):
                    print "No such site '%s'" % sitename
                else:
                    site = sitemgr.getSite(sitename)
                    print "%s:" % sitename
                    print "    dir: %s" % site.dir
                    print "    uri: %s" % site.uriPub
                    print "    privkey: %s" % site.uriPriv
                    #print "    version: %s" % info['version']
                    
            pass
        return

    elif cmd == 'update':
        if not sitemgr.node:
            noNodeError(sitemgr, "Cannot update freesites")
        try:
            then = time.time()
            sitemgr.insert()
            now = time.time()
            #print "Site updates completed in %s seconds" % int(now - then)
        except KeyboardInterrupt:
            print "freesitemgr: site inserts cancelled by user"

    try:
        sitemgr.node.shutdown()
    except:
        pass



#@-node:main
#@+node:mainline
if __name__ == '__main__':
    main()

#@-node:mainline
#@-others
#@-node:freesitemgr-script
#@-others
#@-node:@file freesitemgr.py
#@-leo
