#!/usr/bin/env python2.4
#@+leo-ver=4
#@+node:@file refbot.py
#@@first
"""
An IRC bot for exchanging noderefs with peer freenet users
"""
#@+others
#@+node:imports
import base64
import StringIO
import sys, time, traceback, time
import socket, select
import threading
import os #not necassary but later on I am going to use a few features from this
import urllib2

import fcp
from minibot import log, MiniBot, PrivateChat

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
    minimumNodeBuild = 998;

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
        if(opts.has_key('fcp_host')):
            self.fcp_host = opts['fcp_host']
        else:
            self.fcp_host = "127.0.0.1";
            needToSave = True
        if(opts.has_key('fcp_port')):
            self.fcp_port = opts['fcp_port']
        else:
            self.fcp_port = 9481;
            needToSave = True
        if(opts.has_key('greetinterval')):
            self.greet_interval = opts['greetinterval']
        else:
            self.greet_interval = 1200
            needToSave = True
        if(opts.has_key('spaminterval')):
            self.spam_interval = opts['spaminterval']
        else:
            self.spam_interval = 3600
            needToSave = True
        if(opts.has_key('refsperrun')):
            self.number_of_refs_to_collect = opts['refsperrun']
        else:
            self.number_of_refs_to_collect = 10
            needToSave = True
        self.refs = opts['refs']
        if(opts.has_key('telnethost')):
            self.tmci_host = opts['telnethost']
            needToSave = True
        else:
            if(opts.has_key('tmci_host')):
                self.tmci_host = opts['tmci_host']
            else:
                self.tmci_host = "127.0.0.1";
                needToSave = True
        if(opts.has_key('telnetport')):
            self.tmci_port = opts['telnetport']
            needToSave = True
        else:
            if(opts.has_key('tmci_port')):
                self.tmci_port = opts['tmci_port']
            else:
                self.tmci_port = 2323;
                needToSave = True
        self.refurl = opts['refurl']
        
        # for internal use shadow of MiniBot configs
        self.irc_host = kw[ 'host' ]
        self.irc_port = kw[ 'port' ]
    
        if needToSave:
            self.save()

        try:
          f = fcp.FCPNode( host = self.fcp_host, port = self.fcp_port )
          f.shutdown()
        except Exception, msg:
          print "Failed to connect to node via FCP (%s:%d).  Check your fcp host and port settings on both the node and the bot config." % ( self.fcp_host, self.fcp_port );
          sys.exit( 1 );
        if( f.nodeBuild < self.minimumNodeBuild ):
          print "This version of the refbot requires your node be running build %d or higher.  Please upgrade your Freenet node and try again." % ( self.minimumNodeBuild );
          sys.exit( 1 );
    
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
        self.adderThreads = []
    
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
    
        opts['tmci_host'] = prompt("Node TMCI (telnet) hostname", "127.0.0.1")
    
        while 1:
            opts['tmci_port'] = prompt("Node TMCI (telnet) port", "2323")
            try:
                opts['tmci_port'] = int(opts['tmci_port'])
                break
            except:
                print "Invalid port '%s'" % opts['tmci_port']
    
        opts['fcp_host'] = prompt("Node FCP hostname", "127.0.0.1")
    
        while 1:
            opts['fcp_port'] = prompt("Node FCP port", "2323")
            try:
                opts['fcp_port'] = int(opts['fcp_port'])
                break
            except:
                print "Invalid port '%s'" % opts['fcp_port']
    
        opts['greetinterval'] = 1200
        opts['spaminterval'] = 3600
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
        f.write(fmt % ("tmci_host", repr(self.tmci_host)))
        f.write(fmt % ("tmci_port", repr(self.tmci_port)))
        f.write(fmt % ("fcp_host", repr(self.fcp_host)))
        f.write(fmt % ("fcp_port", repr(self.fcp_port)))
        f.write(fmt % ("refurl", repr(self.refurl)))
        f.write(fmt % ("password", repr(self.password)))
        f.write(fmt % ("greetinterval", repr(self.greet_interval)))
        f.write(fmt % ("spaminterval", repr(self.spam_interval)))
        f.write(fmt % ("refsperrun", repr(self.number_of_refs_to_collect)))
        f.write(fmt % ("refs", repr(self.refs)))
    
        f.close()
    
        log("Saved configuration to %s" % self.confpath)
    
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
        self.after(0.5, self.process_any_refs_added)
    
        log("****** on_ready")
    
    #@-node:on_ready
    #@+node:on_chanmsg
    def on_chanmsg(self, sender, target, msg):
        """
        Handles a message on the channel, not addressed to the bot
        """
        log("** chanmsg: %s => %s: %s" % (sender, target, repr(msg)))
    
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
        if(self.greet_interval > 0):
            self.after(self.greet_interval, self.greetChannel)
    
    #@-node:greetChannel
    #@+node:spamChannel
    def spamChannel(self):
        """
        Periodic plugs
        """
        self.action(
            self.channel,
            "is a Freenet NodeRef Swap-bot (www.freenet.org.nz/pyfcp/ + latest SVN refbot.py minibot.py and fcp/node.py)"
            )
        if(self.spam_interval > 0):
            self.after(self.spam_interval, self.spamChannel)
    
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
    def addref(self, url, replyfunc, sender_irc_nick):
    
        log("** adding ref: %s" % url)
        adderThread = AddRef(self.tmci_host, self.tmci_port, self.fcp_host, self.fcp_port, url, replyfunc, sender_irc_nick, self.irc_host)
        self.adderThreads.append(adderThread)
        adderThread.start()
    
    #@-node:addref
    #@+node:process_any_refs_added
    def process_any_refs_added(self):
        if(len(self.adderThreads) != 0):
            for adderThread in self.adderThreads:
                if(not adderThread.isAlive()):
                    adderThread.join()
                    log("adderThread has status: %s  url: %s  error_msg: %s" % (adderThread.status, adderThread.url, adderThread.error_msg))
                    self.adderThreads.remove(adderThread)
                    if(1 == adderThread.status):
                        self.refs.append(adderThread.url)
                        self.save()
                        self.nrefs += 1
                        log("** added ref: %s" % adderThread.url)
                        refs_to_go = self.number_of_refs_to_collect - self.nrefs
                        refs_to_go_str = ''
                        if refs_to_go > 0:
                            refs_plural_str = ''
                            if( refs_to_go > 1 ):
                                refs_plural_str = "s"
                            refs_to_go_str = " (%d ref%s to go)" % ( refs_to_go, refs_plural_str )
                        adderThread.replyfunc("added your ref.  Now please add mine <%s> to create a peer connection.%s" % (self.refurl, refs_to_go_str))
                        if self.nrefs >= self.number_of_refs_to_collect:
                            log("Got our %d refs, now terminating!" % ( self.number_of_refs_to_collect ))
                            self.after(3, self.thankChannelThenDie)
                    else:
                        error_str = "there was some unknown problem while trying to add your ref.  Try again and/or try again later."
                        if(0 == adderThread.status):
                            error_str = "there was a general error while trying to add your ref.  Try again and/or try again later."
                        elif(-1 == adderThread.status):
                            error_str = "the URL does not contain a valid ref.  Please correct the ref at the URL or the URL itself <%s> and try again." % (adderThread.url)
                        elif(-2 == adderThread.status):
                            error_str = "there was a problem fetching the given URL.  Please correct the URL <%s> and try again, or try again later if you suspect server troubles." % (adderThread.url)
                        elif(-3 == adderThread.status):
                            error_str = "there was a problem talking to the node.  Please try again later."
                        elif(-4 == adderThread.status):
                            error_str = "the node reports that it already has a peer with that identity.  Ref not re-added."
                        refs_to_go = self.number_of_refs_to_collect - self.nrefs
                        refs_to_go_str = ''
                        if refs_to_go > 0:
                            refs_plural_str = ''
                            if( refs_to_go > 1 ):
                                refs_plural_str = "s"
                            refs_to_go_str = " (%d ref%s to go)" % ( refs_to_go, refs_plural_str )
                        adderThread.replyfunc("%s%s" % (error_str, refs_to_go_str))
                    break
        self.after(0.5, self.process_any_refs_added)
    
    #@-node:process_any_refs_added
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
    #@+node:has_ref
    def has_ref(self, url):
        """
        Checks to see if we've already got the given ref
        """
        if url in self.refs:
            return True
        return False
    #@-node:has_ref
    #@+node:maybe_add_ref
    def maybe_add_ref(self, url, replyfunc, sender_irc_nick):
        """
        Checks, adds and replies to a ref add request
        """
        if( self.check_ref_url_and_complain(url, replyfunc)):
           self.addref(url, replyfunc, sender_irc_nick)
    #@-node:maybe_add_ref
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
            if(self.greet_interval > 0 and t > self.greet_interval):
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
    #@+node:events
    # event handling methods
    
    #@+others
    #@+node:on_unknownCommand
    def on_unknownCommand(self, replyfunc, cmd, msg):
        """
        Pick up possible URLs
        """
        if cmd.startswith("http://"):
            if(not self.bot.has_ref(cmd)):
                self.bot.maybe_add_ref(cmd.strip(), replyfunc, self.peernick)
            else:
                self.privmsg("error - already have your ref <%s>" % (cmd))
            return True
    
    #@-node:on_unknownCommand
    #@-others
    
    #@-node:events
    #@+node:actions
    # action methods
    
    #@+others
    #@-others
    
    #@-node:actions
    #@+node:command handlers
    # command handlers
    
    #@+others
    #@+node:cmd_hi
    def cmd_hi(self, replyfunc, args):
    
        log("cmd_hi: %s" % str(args))
    
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
        if(not self.bot.has_ref(url)):
            self.bot.maybe_add_ref(url.strip(), replyfunc, self.peernick)
        else:
            self.privmsg("error - already have your ref <%s>"% (url))
    
    #@-node:cmd_addref
    #@+node:cmd_getref
    def cmd_getref(self, replyfunc, args):
        
        replyfunc("My ref is at %s" % self.bot.refurl)
    
    #@-node:cmd_getref
    #@-others
    
    #@-node:command handlers
    #@-others

#@-node:class RefBotConversation
#@+node:class AddRef
class AddRef(threading.Thread):
    def __init__(self, tmci_host, tmci_port, fcp_host, fcp_port, url, replyfunc, sender_irc_nick, irc_host):
        threading.Thread.__init__(self)
        self.tmci_host = tmci_host
        self.tmci_port = tmci_port
        self.fcp_host = fcp_host
        self.fcp_port = fcp_port
        self.url = url
        self.replyfunc = replyfunc
        self.sender_irc_nick = sender_irc_nick
        self.irc_host = irc_host
        self.status = 0
        self.error_msg = None

    def run(self):
        try:
          openurl = urllib2.urlopen(self.url)
          refbuf = openurl.read(20*1024)  # read up to 20 KiB
          openurl.close()
          refmemfile = StringIO.StringIO(refbuf)
          reflines = refmemfile.readlines()
          refmemfile.close();
        except Exception, msg:
          self.status = -2
          self.error_msg = msg
          return  
        ref_fieldset = {};
        end_found = False
        for refline in reflines:
            refline = refline.strip();
            if("" == refline):
                continue;
            if("end" == refline.lower()):
                end_found = True
                break;
            reflinefields = refline.split("=", 1)
            if(2 != len(reflinefields)):
                continue;
            if(not ref_fieldset.has_key(reflinefields[ 0 ])):
                ref_fieldset[ reflinefields[ 0 ]] = reflinefields[ 1 ]
        if(not ref_fieldset.has_key("identity")):
            self.status = -1  # invalid ref found at URL
            self.error_msg = "No identity field in ref"
            return
        if(not ref_fieldset.has_key("myName")):
            self.status = -1  # invalid ref found at URL
            self.error_msg = "No myName field in ref"
            return

        try:
          f = fcp.FCPNode( host = self.fcp_host, port = self.fcp_port )
          returned_peer = f.modifypeer( NodeIdentifier = ref_fieldset[ "identity" ] )
          if( type( returned_peer ) == type( [] )):
            returned_peer = returned_peer[ 0 ];
          if( returned_peer[ "header" ] == "Peer" ):
              self.status = -4
              self.error_msg = "Node already has a peer with that identity"
              return
          sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          sock.connect((self.tmci_host, self.tmci_port))

          # wait for something to come in
          sock.recv(1)
          time.sleep(0.1)

          # wait till node stops sending
          while len(select.select([sock], [], [], 0.1)[0]) > 0:
              sock.recv(1024)

          sock.send("ADDPEER:\r\n")
          for refline in reflines:
              refline = refline.strip()
              sock.send("%s\r\n" % (refline))

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
        except Exception, msg:
          self.status = -3
          self.error_msg = msg
          return  

        try:
          note_text = "%s added via refbot.py from %s@%s at %s" % ( ref_fieldset[ "myName" ], self.sender_irc_nick, self.irc_host, time.strftime( "%Y%m%d-%H%M%S", time.localtime() ) )
          encoded_note_text = base64.encodestring( note_text ).replace( "\r", "" ).replace( "\n", "" );
          f.modifypeernote( NodeIdentifier = ref_fieldset[ "identity" ], PeerNoteType = fcp.node.PEER_NOTE_PRIVATE_DARKNET_COMMENT, NoteText = encoded_note_text )
        except Exception, msg:
          # We'll just not have added a private peer note if we get an exception here
          pass

        if(not ref_fieldset.has_key("physical.udp")):
            self.status = 2
            self.error_msg = "No physical.udp field in ref"
            return
        self.status = 1

#@-node:class AddRef
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
