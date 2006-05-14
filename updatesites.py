#!/usr/bin/env python
"""
A utility to update freesites from within a cron environment
"""
import sys, os, time, commands
import sitemgr

# time we wait after starting fred, to allow the node to 'warm up'
# and make connections to its peers
startupTime = 180

# directory where we have freenet installed,
# change it as needed
freenetDir = "/home/david/freenet"

# derive path of freenet pid file, the (non)existence
# of which is the easiest test of whether the freenet
# node is running
freenetPidFile = os.path.join(freenetDir, "Freenet.pid")

logFile = os.path.join(freenetDir, "updatesites.log")
pidFile = os.path.join(freenetDir, "updatesites.pid")

# small wrapper which, if freenet isn't already running,
# starts it prior to inserting then stops it after
# inserting
def main(verbose=None):

    if verbose == None:
        verbose = ('-v' in sys.argv)

    if os.path.isfile(pidFile):
        print "updatesites.py already running: pid=%s" % file(pidFile).read()
        sys.exit(1)
    f = file(pidFile, "w")
    f.write(str(os.getpid()))
    f.close()

    try:
        print "--------------------------------------------"
        print "Start of site updating run"
        
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
            kw = {"verbosity" : sitemgr.fcp.DETAIL}
        else:
            kw = {"verbosity" : sitemgr.fcp.INFO}
    
        # get a site manager object, and perform the actual insertions
        s = sitemgr.SiteMgr(**kw)
        s.update()
        del s
        
        # kill freenet if it was dynamically started
        if startingFreenet:
            print "Waiting %s for inserts to finish..." % startupTime
            time.sleep(startupTime)
            print "Stopping node..."
            os.system("./run.sh stop")
            print "Node stopped"
    except:
        pass

    # can now drop our pidfile
    os.unlink(pidFile)

if __name__ == '__main__':
    main()

