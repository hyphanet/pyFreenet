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

obscenities = ["fuck", "cunt", "shit", "asshole", "fscking", "wank"]
reactToObscenities = False

svnLongRevision = "$Revision$"
svnRevision = svnLongRevision[ 11 : -2 ]

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

    svnLongRevision = "$Revision$"
    svnRevision = svnLongRevision[ 11 : -2 ]

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
        if(opts.has_key('ownerircnick')):
            kw['owner'] = opts['ownerircnick']
        else:
            kw['owner'] = opts['usernick']
            needToSave = True
        kw['nodenick'] = opts['usernick']
        kw['password'] = opts['password']
        if(opts.has_key('ircchannel')):
            kw['channel'] = opts['ircchannel']
        else:
            kw['channel'] = "#freenet-refs"
            needToSave = True
    
        # set up non-config keywords
        kw['nick'] = kw['nodenick'] + "_bot"
        kw['peerclass'] = RefBotConversation
        kw['realname'] = "%s's Freenet NodeRef Bot" % kw['nick']
    
        # get local attribs
        self.nodenick = opts['usernick']
        if(opts.has_key('ircchannel')):
            self.chan = opts['ircchannel']
        else:
            self.chan = "#freenet-refs"
            needToSave = True
        if(opts.has_key('refsperrun')):
            self.number_of_refs_to_collect = opts['refsperrun']
        else:
            self.number_of_refs_to_collect = 10
            needToSave = True
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
    
        opts['ownerircnick'] = prompt("Enter your usual freenode.net nick")
        opts['usernick'] = prompt("Enter your node's name", opts['ownerircnick'])
        print "** You need to choose a new password, since this bot will"
        print "** register this password with freenode 'nickserv', and"
        print "** on subsequent runs, will identify with this password"
        opts['password'] = prompt("Enter a new password")
        opts['refurl'] = prompt("URL of your noderef")
        opts['ircchannel'] = prompt("IRC channel to join", "#freenet-refs")
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
    
        opts['refsperrun'] = 10
        opts['refs'] = []
    
        return opts
    
    #@-node:setup
    #@+node:save
    def save(self):
    
        f = file(self.confpath, "w")
    
        fmt = "%s = %s\n"
        f.write(fmt % ("ownerircnick", repr(self.owner)))
        f.write(fmt % ("ircchannel", repr(self.chan)))
        f.write(fmt % ("usernick", repr(self.nodenick)))
        f.write(fmt % ("irchost", repr(self.host)))
        f.write(fmt % ("ircport", repr(self.port)))
        f.write(fmt % ("telnethost", repr(self.telnethost)))
        f.write(fmt % ("telnetport", repr(self.telnetport)))
        f.write(fmt % ("refurl", repr(self.refurl)))
        f.write(fmt % ("password", repr(self.password)))
        f.write(fmt % ("refsperrun", repr(self.number_of_refs_to_collect)))
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
    #@+node:on_chanmsg
    def on_chanmsg(self, sender, target, msg):
        """
        Handles a message on the channel, not addressed to the bot
        """
        print "** chanmsg: %s => %s: %s" % (sender, target, repr(msg))
    
        if reactToObscenities:
            m = msg.lower()
            for o in obscenities:
                if o in m:
                    self.action(self.channel, "blushes")
                    break
    
    #@-node:on_chanmsg
    #@-node:events
    #@+node:actions
    # action methods
    
    #@+others
    #@+node:greetChannel
    def greetChannel(self):
    
        refs_to_go = self.number_of_refs_to_collect - self.nrefs
        refs_plural_str = ''
        if( refs_to_go > 1 ):
            refs_plural_str = "s"
        self.privmsg(
            self.channel,
            "Hi, I'm %s's noderef swap bot. To swap a ref with me, /msg me or say %s: your_ref_url  (%d ref%s to go)" \
            % ( self.nodenick, self.nick, refs_to_go, refs_plural_str )
            )
    
        self.after(1200, self.greetChannel)
    
    #@-node:greetChannel
    #@+node:spamChannel
    def spamChannel(self):
        """
        Periodic plugs
        """
        self.action(
            self.channel,
            "is a Freenet NodeRef Swap-bot (www.freenet.org.nz/pyfcp/)"
            )
    
        self.after(3600, self.spamChannel)
    
    #@-node:spamChannel
    #@+node:thankChannel
    def thankChannelThenDie(self):
    
        refs_plural_str = ''
        if( self.number_of_refs_to_collect > 1 ):
            refs_plural_str = "s"
        self.privmsg(
            self.channel,
            "OK, I've got my %d noderef%s.  Thanks all." \
            % ( self.number_of_refs_to_collect, refs_plural_str )
            )
        self.privmsg(
            self.channel,
            "Bye"
            )
        self.after(4, self.die)
    
    #@-node:thankChannelThenDie
    #@+node:addref
    def addref(self, url):
    
        if url not in self.refs:
            print "** added ref: %s" % url
            thread.start_new_thread(addref, (self.telnethost, self.telnetport, url))
            self.refs.append(url)
            self.save()
    
            self.nrefs += 1
            if self.nrefs >= self.number_of_refs_to_collect:
                print "Got our %d refs, now terminating!" % ( self.number_of_refs_to_collect )
                self.after(3, self.thankChannelThenDie)
        else:
            print "** already got ref: %s" % url
    
    #@-node:addref
    #@+node:check_ref_url_and_complain
    def check_ref_url_and_complain(self, url, replyfunc):
    
        if( "http://code.bulix.org/" == url[ :22 ].lower() and "?raw" != url[ -4: ].lower() ):
            replyfunc("When sharing a code.bulix.org ref url, please include a \"?raw\" at the end (i.e. %s?raw).  Ref not added." % ( url ))
            return False
        if( "http://dark-code.bulix.org/" == url[ :27 ].lower() and "?raw" != url[ -4: ].lower() ):
            replyfunc("When sharing a dark-code.bulix.org ref url, please include a \"?raw\" at the end (i.e. %s?raw).  Ref not added." % ( url ))
            return False
        if( "http://pastebin.ca/" == url[ :19 ].lower() and "raw/" != url[ 19:23 ].lower() ):
            replyfunc("When sharing a pastebin.ca ref url, please use the \"Raw Content Download\" link.  Ref not added.")
            return False
        if( "http://rafb.net/paste/results/" == url[ :30 ].lower() and ".txt" != url[ -4: ].lower() ):
            replyfunc("When sharing a rafb.net ref url, please use the \"Download as Text\" link.  Ref not added.")
            return False
        if( "http://www.rafb.net/paste/results/" == url[ :34 ].lower() and ".txt" != url[ -4: ].lower() ):
            replyfunc("When sharing a www.rafb.net ref url, please use the \"Download as Text\" link.  Ref not added.")
            return False
        return True
    
    #@-node:check_ref_url_and_complain
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
            self.maybe_add_ref(cmd, replyfunc)
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
    #@+node:check_ref_url_and_complain
    def check_ref_url_and_complain(self, url, replyfunc):
        """
        Adds a ref to node, via telnet
        """
        return self.bot.check_ref_url_and_complain(url, replyfunc)
    #@-node:check_ref_url_and_complain
    #@+node:maybe_add_ref
    def maybe_add_ref(self, url, replyfunc):
        """
        Checks, adds and replies to a ref add request
        """
        if url not in self.bot.refs:
            if( self.check_ref_url_and_complain(url, replyfunc)):
                self.addref(url)
                refs_to_go = self.bot.number_of_refs_to_collect - self.bot.nrefs
                refs_to_go_str = ''
                if refs_to_go > 0:
                    refs_plural_str = ''
                    if( refs_to_go > 1 ):
                        refs_plural_str = "s"
                    refs_to_go_str = " (%d ref%s to go)" % ( refs_to_go, refs_plural_str )
                replyfunc("added your ref.  Now please add mine <%s> to create a peer connection.%s" % (self.bot.refurl, refs_to_go_str ))
        else:
            self.privmsg("error - already have your ref")
    #@-node:maybe_add_ref
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
            "I can be downloaded from http://www.freenet.org.nz/pyfcp/ as part of pyfcp (or from Freenet's SVN)",
            "My version numbers are refbot.py at r%s and minibot.py at r%s" % (FreenetNodeRefBot.svnRevision, MiniBot.svnRevision),
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
        self.maybe_add_ref(url, replyfunc)
    
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
