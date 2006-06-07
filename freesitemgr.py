#!/usr/bin/env python
"""
A utility to update freesites from within a cron environment
"""
import sys, os, time, commands, traceback, getopt

import fcp.node
from fcp.sitemgr import SiteMgr

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
    confFileName = "freesites.ini"
else:
    confFileName = ".freesites"
confFile = os.path.join(homeDir, confFileName)

def editCreateConfig(sitemgr):
    """
    Creates an initial config file interactively
    """
    print "Setting up configuration file %s" % sitemgr.configFile

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
        print "Setup aborted"
        return
    fcpnode.shutdown()

    sitemgr.fcpHost = fcpHost
    sitemgr.fcpPort = fcpPort

    # confirm and save
    if getyesno("Save configuration", True):
        sitemgr.saveConfig()

    print "Configuration saved to %s" % sitemgr.configFile

def addSite(sitemgr):
    """
    Interactively adds a new site to config
    """
    print "Add new site"

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
        elif not os.path.isfile(os.path.join(sitedir, "index.html")):
            print "'%s' has no index.html, try again" % sitedir
            continue
        break
    
    # good to go - add the site
    sitemgr.addSite(sitename, sitedir)

    print "Added new freesite: '%s' => %s" % (sitename, sitedir)

def removeSite(sitemgr, sitename):
    """
    tries to remove site from config
    """
    if not sitemgr.hasSite(sitename):
        print "No such freesite '%s'" % sitename
        return

    if getyesno("Are you sure you wish to delete freesite '%s'", False):
        sitemgr.removeSite(sitename)
        print "Removed freesite '%s'" % sitename
    else:
        print "Freesite deletion aborted"

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
def help():
    """
    dump help info and exit
    """
    print "%s: a console-based freesite insertion utility" % progname
    
    print "Usage: %s [options] <command> <args>" % progname
    print "Options:"
    print "  -h, --help"
    print "          - display this help message"
    print "  -f, --file=filename"
    print "          - use a different config file (default is %s)" % confFile
    print "  -v, --verbose"
    print "          - run verbosely"
    print "  -q, --quiet"
    print "          - run quietly"
    print "  -l, --logfile=filename"
    print "          - location of logfile (default %s)" % logFile
    print "  -s, --single-files"
    print "          - insert one file at a time as CHKs, then insert"
    print "            a manifest which redirects to these, useful"
    print "            for debugging. Also, you MUST use this mode if"
    print "            inserting a freesite from across a LAN (ie, if"
    print "            the FCP service is on a different machine to"
    print "            the machine running freesitemgr"
    print "  -a, --all-at-once"
    print "          - companion option to '-s' which, if set, inserts all"
    print "            files simultaneously; very demanding on memory and"
    print "            CPU, not recommended for larger sites"
    print
    print "Available Commands:"
    print "  setup          - create/edit freesite config file interactively"
    print "  add            - add new freesite called <name> using directory <dir>"
    print "  list [<name>]  - display a summary of all freesites, or a"
    print "                   detailed report of one site if <name> given"
    print "  remove <name>  - remove given freesite"
    print "  update         - reinsert any freesites which have changed since"
    print "                   they were last inserted"

def usage(ret=-1, msg=None):
    if msg != None:
        print msg
    print "Usage: %s [options] <command> [<arguments>]" % progname
    print "Do '%s -h' for help" % progname

    sys.exit(ret)

def main():

    # default job options
    opts = {
            "configfile" : confFile,
            "verbosity" : fcp.node.INFO,
            "logfile" : logFile,
            "filebyfile" : False,
            "allatonce" : False,
            }

    # process command line switches
    try:
        cmdopts, args = getopt.getopt(
            sys.argv[1:],
            "?hvf:l:sa",
            ["help", "verbose", "file=", "logfile=",
             "single-files", "all-at-once",
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
            opts['verbosity'] = fcp.node.DETAIL
            opts['Verbosity'] = 1023
        
        if o in ("-q", "--quiet"):
            opts['verbosity'] = fcp.node.SILENT
        
        if o in ("-f", "--file"):
            opts['configfile'] = a
        
        if o in ("-l", "--logfile"):
            opts['logfile'] = a
        
        if o in ("-s", "--single-files"):
            opts['filebyfile'] = True

        if o in ("-a", "--all-at-once"):
            opts['allatonce'] = True

    # process command
    if len(args) < 1:
        usage(msg="No command given")

    cmd = args.pop(0)

    if cmd not in ['setup','add','remove','list','update']:    
        usage(msg="Unrecognised command '%s'" % cmd)

    # we now have a likely valid command, so now we need a sitemgr
    sitemgr = SiteMgr(**opts)

    if cmd == 'setup':
        editCreateConfig(sitemgr)

    elif cmd == 'add':
        addSite(sitemgr)

    elif cmd == 'remove':
        if not args:
            print "Remove site: no freesites selected"
            return
        for sitename in args:
            removeSite(sitemgr, sitename)
        pass
        print "Removed freesites: " + " ".join(args)
        return

    elif cmd == 'list':
        if not args:
            # summary list
            print " ".join(sitemgr.getSiteNames())
        else:
            for sitename in args:
                if not sitemgr.hasSite(sitename):
                    print "No such site '%s'" % sitename
                else:
                    info = sitemgr.getSiteInfo(sitename)
                    print "%s:" % sitename
                    print "    dir: %s" % info['dir']
                    print "    uri: %s" % info['uri']
                    print "    privkey: %s" % info['privatekey']
                    print "    version: %s" % info['version']
                    
            pass
        return

    elif cmd == 'update':
        sitemgr.update()
        pass

# small wrapper which, if freenet isn't already running,
# starts it prior to inserting then stops it after
# inserting
def main_old(verbose=None):

    os.chdir(freenetDir)

    if verbose == None:
        verbose = ('-v' in sys.argv)

    if os.path.isfile(pidFile):
        print "updatesites.py already running: pid=%s" % file(pidFile).read()
        sys.exit(1)
    f = file(pidFile, "w")
    f.write(str(os.getpid()))
    f.close()

    #logfile = file(logFile, "w")
    logfile = sys.stdout

    logfile.write("----------------------\n")
    logfile.write(time.asctime() + "\n")

    try:
        print "--------------------------------------------"
        print "Start of site updating run"
        print "Status being logged to file %s" % logFile
        
        # start freenet and let it warm up, if it's not already running
        if not os.path.isfile(freenetPidFile):
            startingFreenet = True
            os.chdir(freenetDir)
            print "Starting freenet..."
            print os.system("%s/start.sh &" % freenetDir)
            print "Letting node settle for %s seconds..." % startupTime
            time.sleep(startupTime)
        else:
            print "Freenet node is already running!"
            startingFreenet = False
    
        # add verbosity argument if needed    
        if verbose:
            kw = {"verbosity" : fcp.DETAIL}
            kw['Verbosity'] = 65535
        else:
            kw = {"verbosity" : fcp.INFO}
    
        # get a site manager object, and perform the actual insertions
        print "Creating SiteMgr object"
        s = fcp.sitemgr.SiteMgr(logfile=logfile, **kw)
        print "Starting updates"
        try:
            s.update()
        except:
            traceback.print_exc()
        print "Updates done"
        del s
        
        # kill freenet if it was dynamically started
        if startingFreenet:
            print "Waiting %s for inserts to finish..." % startupTime
            time.sleep(startupTime)
            print "Stopping node..."
            os.system("./run.sh stop")
            print "Node stopped"
        else:
            print "Not killing freenet - it was already running"
    except:
        traceback.print_exc()
        pass

    # can now drop our pidfile
    os.unlink(pidFile)

if __name__ == '__main__':
    main()

