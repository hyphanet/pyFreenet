#!/usr/bin/env python
#@+leo-ver=4
#@+node:@file refbot.py
#@@first
"""
An IRC bot for exchanging noderefs with peer freenet users
"""
#@+others
#@+node:imports
import sys, time, traceback, time
import socket, select
import thread, threading
import os #not necassary but later on I am going to use a few features from this

from minibot import MiniBot, PrivateChat

#@-node:imports
#@+node:globals
progname = sys.argv[0]
args = sys.argv[1:]
nargs = len(args)

# The server we want to connect to
#HOST = 'mesa.az.us.undernet.org'
defaultHost = 'irc.freenode.net'

# The connection port which is usually 6667
defaultPort = 6667

# The bot's nickname
#defaultNick = 'aum_bot'

ident = 'FreenetRefBot'

# The default channel for the bot
#chan = '#freenet-bottest'
chan = '#freenet-refs'

# Here we store all the messages from server
readbuffer = ''

#@-node:globals
#@+node:exceptions
class NotOwner(Exception):
    """
    peer is telling us to do something only owners can tell us to
    """
#@-node:exceptions
#@+node:class FreenetNodeRefBot
class FreenetNodeRefBot(MiniBot):
    """
    A simple IRC bot
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, cfgFile=None):
        """
        Takes one optional argument - alternative pathname
        """
        # determine a config file path
        if not cfgFile:
            cfgFile = os.path.join(os.path.expanduser("~"), ".freenet_ref_bot")
        confpath = self.confpath = cfgFile
    
        # load, or create, a config
        if os.path.isfile(confpath):
            opts = self.load()
            needToSave = False
        else:
            opts = self.setup()
            needToSave = True
    
        # now, gotta map from config file to constructor keyword
        kw = {}
    
        # set up keywords from config
        kw['host'] = opts['irchost']
        kw['port'] = opts['ircport']
        kw['owner'] = opts['usernick']
        kw['password'] = opts['password']
    
        # set up non-config keywords
        kw['nick'] = opts['usernick'] + "_bot"
        kw['channel'] = chan
        kw['peerclass'] = RefBotConversation
        kw['realname'] = "%s's Freenet NodeRef Bot" % kw['nick']
        kw['nick'] = kw['owner'] + "_bot"
    
        # get local attribs
        self.refs = opts['refs']
        self.telnethost = opts['telnethost']
        self.telnetport = opts['telnetport']
        self.refurl = opts['refurl']
    
        # finally construct the parent
        MiniBot.__init__(self, **kw)
    
        if needToSave:
            self.save()
    
        self.timeLastChanGreeting = time.time()
        self.haveSentDownloadLink = False
    
        self.nrefs = 0
    
        self.lastSendTime = time.time()
        self.sendlock = threading.Lock()
    
        #self.usersInChan = []
    
    #@-node:__init__
    #@+node:setup
    def setup(self):
        """
        """
        def prompt(msg, dflt=None):
            if dflt:
                return raw_input(msg + " [%s]: " % dflt) or dflt
            else:
                while 1:
                    resp = raw_input(msg + ": ")
                    if resp:
                        return resp
    
        opts = {}
    
        opts['usernick'] = prompt("Enter your usual freenode.net nick")
        print "** You need to choose a new password, since this bot will"
        print "** register this password with freenode 'nickserv', and"
        print "** on subsequent runs, will identify with this password"
        opts['password'] = prompt("Enter a new password")
        opts['refurl'] = prompt("URL of your noderef")
        opts['irchost'] = prompt("Hostname of IRC server", "irc.freenode.net")
    
        while 1:
            opts['ircport'] = prompt("IRC Server Port", "6667")
            try:
                opts['ircport'] = int(opts['ircport'])
                break
            except:
                print "Invalid port '%s'" % opts['ircport']
    
        opts['telnethost'] = prompt("Node Telnet hostname", "127.0.0.1")
    
        while 1:
            opts['telnetport'] = prompt("Node Telnet port", "2323")
            try:
                opts['telnetport'] = int(opts['telnetport'])
                break
            except:
                print "Invalid port '%s'" % opts['telnetport']
    
        opts['refs'] = []
    
        return opts
    
    #@-node:setup
    #@+node:save
    def save(self):
    
        f = file(self.confpath, "w")
    
        fmt = "%s = %s\n"
        f.write(fmt % ("usernick", repr(self.nick)))
        f.write(fmt % ("irchost", repr(self.host)))
        f.write(fmt % ("ircport", repr(self.port)))
        f.write(fmt % ("telnethost", repr(self.telnethost)))
        f.write(fmt % ("telnetport", repr(self.telnetport)))
        f.write(fmt % ("refurl", repr(self.refurl)))
        f.write(fmt % ("password", repr(self.password)))
        f.write(fmt % ("refs", repr(self.refs)))
    
        f.close()
    
        print "Saved configuration to %s" % self.confpath
    
    #@-node:save
    #@+node:load
    def load(self):
    
        opts = {}
        exec file(self.confpath).read() in opts
        return opts
    
    #@-node:load
    #@+node:events
    # handle events
    #@+node:on_ready
    def on_ready(self):
        """
        Invoked when bot is fully signed in, on channel and ready to play
        """
        if self._restarted:
            self.action(self.channel, "restarted because the server was ignoring it")
        else:
            self.greetChannel()
    
        self.after(10, self.spamChannel)
    
        print "****** on_ready"
    
    #@-node:on_ready
    #@-node:events
    #@+node:actions
    # action methods
    
    #@+others
    #@+node:greetChannel
    def greetChannel(self):
    
        self.privmsg(chan, "Hi, I'm %s's noderef swap bot" % self.owner)
        self.privmsg(self.channel, 
                     "To swap a ref with me, type '%s: <your-ref-url>'" % self.nick)
    
        self.after(1200, self.greetChannel)
    
    #@-node:greetChannel
    #@+node:spamChannel
    def spamChannel(self):
        """
        Periodic plugs
        """
        self.action(
            self.channel,
            "is a Freenet NodeRef Swap-bot (www.freenet.org.nz/pyfcp)"
            )
    
        self.after(3600, self.spamChannel)
    
    #@-node:spamChannel
    #@+node:addref
    def addref(self, url):
    
        if url not in self.refs:
            print "** added ref: %s" % url
            thread.start_new_thread(addref, (self.telnethost, self.telnetport, url))
            self.refs.append(url)
            self.save()
    
            self.nrefs += 1
            if self.nrefs >= 10:
                print "Got our 10 refs, now terminating!"
                self.die()
        else:
            print "** already got ref: %s" % url
    
    #@-node:addref
    #@-others
    
    #@-node:actions
    #@+node:low level
    # low level methods
    
    #@+others
    #@+node:thrd
    def thrd(self):
    
        while 1:
            time.sleep(10)
            self.sendline("PING")
    
            now = time.time()
            t = now - self.timeLastChanGreeting
            if t > 900:
                self.greetChannel()
    
    #@-node:thrd
    #@-others
    
    #@-node:low level
    #@-others

#@-node:class FreenetNodeRefBot
#@+node:class RefBotConversation
class RefBotConversation(PrivateChat):
    """
    Encapsulates a private chat with a peer
    """
    #@    @+others
    #@+node:__init__
    def __init__(self, bot, peernick):
        """
        """
        self.bot = bot
        self.peernick = peernick
    
    #@-node:__init__
    #@+node:events
    # event handling methods
    
    #@+others
    #@+node:on_unknownCommand
    def on_unknownCommand(self, replyfunc, cmd, msg):
        """
        Pick up possible URLs
        """
        if cmd.startswith("http://"):
            if cmd not in self.bot.refs:
                self.addref(cmd)
                replyfunc(self.bot.refurl)
            else:
                self.privmsg("error already have your ref")
            return True
    
    #@-node:on_unknownCommand
    #@-others
    
    #@-node:events
    #@+node:actions
    # action methods
    
    #@+others
    #@+node:addref
    def addref(self, url):
        """
        Adds a ref to node, via telnet
        """
        return self.bot.addref(url)
    #@-node:addref
    #@-others
    
    #@-node:actions
    #@+node:command handlers
    # command handlers
    
    #@+others
    #@+node:cmd_hi
    def cmd_hi(self, replyfunc, args):
    
        print "cmd_hi: %s" % str(args)
    
        self.action("waits for a bit")
    
        self.privmsg("Hi - type 'help' for help")
    
    #@-node:cmd_hi
    #@+node:cmd_error
    def cmd_error(self, replyfunc, args):
        pass
    
    #@-node:cmd_error
    #@+node:cmd_help
    def cmd_help(self, replyfunc, args):
    
        self.privmsg(
            "I am a bot for exchanging freenet noderefs",
            "Available commands:",
            "  addref <URL> - add ref at <URL> to my node",
            "  getref      - print out my own ref so you can add me",
            "  die         - terminate me (owner only)",
            "  help        - display this help",
            "** (end of help listing) **"
            )
    
    #@-node:cmd_help
    #@+node:cmd_addref
    def cmd_addref(self, replyfunc, args):
    
        if len(args) != 1:
            self.privmsg(
                "Invalid argument count",
                "Syntax: addref <url>"
                )
            return
        
        url = args[0]
        self.addref(url)
        
        replyfunc("added, my ref is at %s" % self.bot.refurl)
    
    #@-node:cmd_addref
    #@+node:cmd_getref
    def cmd_getref(self, replyfunc, args):
        
        replyfunc("My ref is at %s" % self.bot.refurl)
    
    #@-node:cmd_getref
    #@-others
    
    #@-node:command handlers
    #@-others

#@-node:class RefBotConversation
#@+node:addref
def addref(host, port, url):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # wait for something to come in
    sock.recv(1)
    time.sleep(0.1)

    # wait till node stops sending
    while len(select.select([sock], [], [], 0.1)[0]) > 0:
        sock.recv(1024)

    sock.send("ADDPEER:%s\n" % url)

    # wait for something to come in
    sock.recv(1)
    time.sleep(0.1)

    # wait till node stops sending
    while len(select.select([sock], [], [], 0.1)[0]) > 0:
        buf = sock.recv(1024)
        sys.stdout.write(buf)
        sys.stdout.flush()
    print

    sock.close()

    return 

#@-node:addref
#@+node:main
def main():

    if nargs > 0:
        cfgFile = args[0]
    else:
        cfgFile = None
    bot = FreenetNodeRefBot(cfgFile)
    bot.run()

#@-node:main
#@+node:mainline
if __name__ == '__main__':
    main()

#@-node:mainline
#@-others
#@-node:@file refbot.py
#@-leo
