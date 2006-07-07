#!/usr/bin/env python
#@+leo-ver=4
#@+node:@file minibot.py
#@@first
"""
An IRC bot for exchanging noderefs with peer freenet users
"""
#@+others
#@+node:imports
import sys, time, traceback, time, sched
import socket, select
import string
import thread, threading
import os #not necassary but later on I am going to use a few features from this

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

class TimeToQuit(Exception):
    """
    Terminates the bot
    """

class NotReceiving(Exception):
    """
    raised when server puts the bot into la-la land
    """

#@-node:exceptions
#@+node:class MiniBot
class MiniBot:
    """
    A simple IRC bot
    """

    svnLongRevision = "$Revision$"
    svnRevision = svnLongRevision[ 11 : -2 ]

    #@    @+others
    #@+node:__init__
    def __init__(self, **kw):
        """
        Creates a MiniBot instance
        
        Arguments:
            - no arguments
            
        Keywords:
            - host - hostname of irc connection - mandatory
            - port - port for IRC connection - default 6667
            - channel - channel to join - mandatory
            - nick - nick to join as - mandatory
            - realname - realname to use
            - ident - ident to use - default MiniBot
            - owner - nick of owner - defaults to None (no owner)
            - password - chanserv password, for registering and
              identifying on servers that use it (eg freenode)
            - peerclass - class to be used for encapsulating conversations
              with peer users - default PeerConversation
        """
        self.host = kw['host']
        self.port = kw.get('port', 6667)
        self.channel = kw['channel']
        self.nick = kw['nick']
        self.owner = kw.get('owner', None)
        self.ident = kw.get('ident', 'FreenetRefBot')
        self.password = kw['password']
        self.peerclass = kw.get('peerclass', PrivateChat)
        
        realname = kw.get('realname', None)
        if not realname:
            if self.owner:
                realname = "%s's IRC MiniBot"
            else:
                realname = "%s the MiniBot" % self.nick
        self.realname = realname
    
        self.running = 1
        self.peers = {}
        self.lastSendTime = time.time()
        self.sendlock = threading.Lock()
    
        self.usersInChan = []
    
        self.rxbuf = []
        self.txqueue = []
    
    #@-node:__init__
    #@+node:run
    def run(self):
    
        self._keepRunning = True
    
        while True:
    
            self.sched = sched.scheduler(time.time, time.sleep)
            self._running = True
    
            # this flag gets set if the bot restarts due to the server
            # sending it off into la-la land. setting this to True
            # suppresses call to self.greetChannel
            self._restarted = False
    
            self.connect()
    
            try:
                self.sched.run()
    
            except KeyboardInterrupt:
                print "Terminated by user"
                self._keepRunning = False
    
            except TimeToQuit:
                self._keepRunning = False
    
            except NotReceiving:
                self.sock.close()
                print "** ERROR: server is ignoring us, restarting in 3 seconds..."
                time.sleep(3)
                self._restarted = True
                continue
    
            except:
                traceback.print_exc()
                self.sock.close()
                print "** ERROR: bot crashed, restarting in 45 seconds..."
                time.sleep(45)  # a repeatedly crashing bot can be very annoying
                continue
    
            if not self._keepRunning:
                self.sock.close()
                break
    
    #@-node:run
    #@+node:connect
    def connect(self):
    
        # Create the socket
        self.log("Create socket...")
    
        sock = self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock = self.sock = socket.socket()
    
        #send = sock.send
        send = self.sendline
    
        # Connect to server
        connected = False
        port = self.port
        ip_addresses = socket.gethostbyname_ex(self.host)[2]
        for ip in ip_addresses:
            self.log("Connect to %s:%s" % (ip, port))
            try:
                sock.connect((ip, port))
                connected = True
                self.log("Connected to %s:%s" % (ip,port))
                break
            except:
                #traceback.print_exc()
                print "Failed to connect to %s:%s" % (ip, port)
    
        if not connected:
            self.log("Couldn't get a connection")
            return
    
        self._lastRxTime = time.time()
    
        # Send the nick to server
        self.log("Send nick...")
        send('NICK '+ self.nick + "\n")
    
        # Identify to server
        self.log("Sending USER...")
        send('USER ' + self.ident + ' ' + self.host + ' bla :' + self.realname + "\n")
    
        # plant initial tasks
        self.after(0, self._receiver)
        self.after(1, self._sender)
        self.after(5, self._watchdog)
        #self.after(1, self._pinger)
    
    #@-node:connect
    #@+node:handlers
    # handler methods
    
    #@+others
    #@+node:on_server_msg
    def on_server_msg(self, typ, msg):
        """
        Handles messages from server
        """
        if "End of /MOTD" in msg:
            print "** joining channel %s" % self.channel
            self.sendline('JOIN ' + self.channel) #Join a channel
            return
    
        elif "End of /NAMES list" in msg:
            #self.identifyPassword()  # Don't identify twice (at least on freenode) 
            return
    
        elif typ == '353':
            msgparts = msg.split()
            if msgparts[0] == self.channel and msgparts[1] == (":"+self.nick):
                self.usersInChan.extend(msgparts[2:])
                print "** users in %s: %s" % (self.channel, self.usersInChan)
                return
            
        elif 1:
            if typ != '409':
                print "** server: %s %s" % (repr(typ), msg)
    
    #@-node:on_server_msg
    #@+node:on_notice
    def on_notice(self, sender, msg):
    
        if "Please wait 30 seconds before using REGISTER again" in msg:
            print "Just registered password, waiting 30 seconds..."
            self.after(31, self.registerPassword)
            return
    
        elif "If this is your nickname, type /msg NickServ" in msg:
            self.identifyPassword()
    
        elif "The nickname " in msg and "is not registered" in msg:
            self.registerPassword()
    
        elif "Password accepted - you are now recognized" in msg:
            self.log("Password accepted")
            self.on_ready()
            self.after(1, self._pinger)
    
        elif 1:
            print "** notice: %s: %s" % (sender, msg)
    
    #@-node:on_notice
    #@+node:on_ready
    def on_ready(self):
        """
        Invoked when bot is fully signed in, on channel and ready to play
        """
        self.greetChannel()
    
    #@-node:on_ready
    #@+node:on_chanmsg
    def on_chanmsg(self, sender, target, msg):
        """
        Handles a message on the channel, not addressed to the bot
        """
        print "** chanmsg: %s => %s: %s" % (sender, target, repr(msg))
    
    #@-node:on_chanmsg
    #@+node:on_pubmsg
    def on_pubmsg(self, sender, msg):
        """
        Handles a message to us from peer
        """
        if sender == self.nick:
            return
    
        if not self.peers.has_key(sender):
            peer = self.peers[sender] = self.peerclass(self, sender)
        else:
            peer = self.peers[sender]
        
        peer.on_pubmsg(msg)
        return
    
    #@-node:on_pubmsg
    #@+node:on_privmsg
    def on_privmsg(self, sender, msg):
        """
        Handles a privmsg from another user
        """
        if sender == self.nick:
            return
    
        if not self.peers.has_key(sender):
            peer = self.peers[sender] = self.peerclass(self, sender)
        else:
            peer = self.peers[sender]
        
        peer.on_privmsg(msg)
        return
    
    #@-node:on_privmsg
    #@+node:on_join
    def on_join(self, sender, target):
        """
        When another user (or us) have joined
        """
        if sender == self.nick:
            return
        if(target[ 0 ] == ':'):
            target = target[ 1: ]
        print "** join: %s -> %s" % ( sender, target )
        
    #@-node:on_join
    #@+node:on_nick
    def on_nick(self, sender, target):
        """
        When another user (or us) have joined
        """
        if(target[ 0 ] == ':'):
            target = target[ 1: ]
        print "** nick: %s -> %s" % ( sender, target )
    
    
    #@-node:on_nick
    #@+node:on_part
    def on_part(self, sender, target, msg):
        print "** leave: %s <- %s with %s" % ( sender, target, msg )
    
        if sender in self.peers:
            del self.peers[sender]
    
    #@-node:on_part
    #@+node:on_quit
    def on_quit(self, sender, msg):
        print "** quit: %s with %s" % ( sender, msg )
    
        if sender in self.peers:
            del self.peers[sender]
    
    #@-node:on_quit
    #@+node:on_mode
    def on_mode(self, mode):
        
        print "** mode: %s" % mode
    
    #@-node:on_mode
    #@+node:on_raw_rx
    def on_raw_rx(self, line):
        """
        Called when a raw line comes in from server
        """
        if line.startswith("NOTICE "):
            msg = msg = line.split(" ", 1)[-1].strip()
            self.on_notice("$server", msg)
            return
    
        parts = line.split(" ", 3)
        sender = parts[0]
    
        sender = sender[1:]
        if sender.endswith(".freenode.net"):
            sender = "$server$"
        else:
            sender = sender.split("!")[0]
    
        typ = parts[1]
    
        target = parts[2].strip()
        if len(parts) > 3:
            msg = parts[3][1:].rstrip()
        else:
            msg = ''
    
        if sender == '$server$':
            self.on_server_msg(typ, msg)
            return
    
        if typ == "NOTICE":
            self.on_notice(sender, msg)
        elif typ == 'JOIN':
            self.on_join(sender, target)
        elif typ == 'NICK':
            self.on_nick(sender, target)
        elif typ == 'PART':
            self.on_part(sender, target, msg)
        elif typ == 'PRIVMSG':
            if sender == 'freenode-connect':
                return
            if target == self.nick:
                self.on_privmsg(sender, msg)
            else:
                if msg.startswith(self.nick+":"):
                    text = msg.split(":", 1)[-1].strip()
                    self.on_pubmsg(sender, text)
                else:
                    self.on_chanmsg(sender, target, msg)
        elif typ == 'QUIT':
            if len(parts) > 2:
                quit_msg = string.join(parts[2:], " ")[1:].rstrip()
            else:
                quit_msg = ''
            self.on_quit(sender, quit_msg)
        elif typ == 'MODE':
            self.on_mode(msg)
        else:
            print "?? sender=%s typ=%s target=%s msg=%s" % (
                repr(sender), repr(typ), repr(target), repr(msg))
        # NOTE: Should only return as it's been factored out of the above ifs
    
    #@-node:on_raw_rx
    #@-others
    
    #@-node:handlers
    #@+node:actions
    # action methods
    
    #@+others
    #@+node:greetChannel
    def greetChannel(self):
    
        self.privmsg(self.channel, "Hi, I'm %s" % self.realname)
    
    #@-node:greetChannel
    #@+node:notice
    def notice(self, target, msg):
    
        self.sendline("NOTICE " + target + " :" + msg)
    
    #@-node:notice
    #@+node:action
    def action(self, target, *lines):
    
        for line in lines:
            self.ctcp("ACTION", target, line)
    
    #@-node:action
    #@+node:ctcp
    def ctcp(self, typ, target, msg=''):
            """
            Send a CTCP command
            """
            if msg:
                msg = " " + msg
            self.privmsg(target, "\001%s%s\001" % (typ, msg))
    
    #@-node:ctcp
    #@+node:chanmsg
    def chanmsg(self, *lines):
        """
        Sends a public msg to channel
        """
        for line in lines:
            self.sendline(":%s PRIVMSG %s :%s" % (self.nick, self.channel, line))
    
    #@-node:chanmsg
    #@+node:pubmsg
    def pubmsg(self, peernick, *lines):
        """
        Sends a msg to peer
        """
        for line in lines:
            self.sendline(":%s PRIVMSG %s :%s: %s" % (
                self.nick, self.channel, peernick, line))
    
    #@-node:pubmsg
    #@+node:privmsg
    def privmsg(self, target, *lines):
    
        for msg in lines:
            self.sendline(":%s PRIVMSG %s :%s" % (
                            self.nick, target, msg))
    
    #@-node:privmsg
    #@+node:registerPassword
    def registerPassword(self):
        """
        sends a 'register <password>' command to nickserv
        """
        self.privmsg("nickserv", "register %s" % self.password)
        pass
    
    #@-node:registerPassword
    #@+node:identifyPassword
    def identifyPassword(self):
        """
        sends an 'identify <password>' command to nickserv
        """
        self.privmsg("nickserv", "identify %s" % self.password)
        pass
    
    #@-node:identifyPassword
    #@+node:after
    def after(self, delay, func, *args, **kw):
        """
        Schedule a function or method 'func' to be executed
        'secs' seconds from now, with arguments
        """
        if self._running:
            pri = kw.get('priority', 3)
            self.sched.enter(delay, pri, func, args)
    
    #@-node:after
    #@+node:die
    def die(self):
    
        raise TimeToQuit
    
    #@-node:die
    #@-others
    
    #@-node:actions
    #@+node:low level
    # low level methods
    
    #@+others
    #@+node:log
    def log(self, msg):
        print "** log: %s" % msg
    
    #@-node:log
    #@+node:sendline
    def sendline(self, msg):
    
        self.txqueue.append(msg)
    
    #@-node:sendline
    #@+node:_sender
    def _sender(self):
    
        self.after(0.5, self._sender)
    
        if self.txqueue:
            msg = self.txqueue.pop(0)
    
            if 0 or msg != 'PING':
                print "** SEND: %s" % msg
    
            self.sock.send(msg + "\n")
    
    
    #@-node:_sender
    #@+node:_receiver
    def _receiver(self):
        """
        receives a single line from server
        """
        sock = self.sock
        while len(select.select([self.sock], [], [], 0.01)[0]) > 0:
            c = sock.recv(1)
            if c == '\n':
                self._lastRxTime = time.time()
                line = "".join(self.rxbuf)
                self.rxbuf = []
                self.on_raw_rx(line)
            else:
                self.rxbuf.append(c)
    
        self.after(0.1, self._receiver)
    
    #@-node:_receiver
    #@+node:_pinger
    def _pinger(self):
        
        self.sendline("PING")
        self.after(5, self._pinger)
    
    #@-node:_pinger
    #@+node:_watchdog
    def _watchdog(self):
        
        #print "** watchdog: WOOF!"
    
        if time.time() - self._lastRxTime > 60:
            print "** watchdog: server is ignoring us, fire a restart..."
            raise NotReceiving
    
        self.after(10, self._watchdog)
    
    #@-node:_watchdog
    #@-others
    
    #@-node:low level
    #@-others

#@-node:class MiniBot
#@+node:class PrivateChat
class PrivateChat:
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
    #@+node:on_pubmsg
    def on_pubmsg(self, msg):
    
        self.on_msg(self.pubmsg, msg)
    #@-node:on_pubmsg
    #@+node:on_privmsg
    def on_privmsg(self, msg):
    
        self.on_msg(self.privmsg, msg)
    
    #@-node:on_privmsg
    #@+node:on_msg
    def on_msg(self, replyfunc, msg):
    
        print "** on_anymsg: %s: %s" % (self.peernick, msg)
    
        parts = msg.split()
        cmd = parts[0]
        args = parts[1:]
    
        print "** cmd=%s" % repr(cmd)
    
        try:
            meth = getattr(self, "cmd_" + cmd)
        except:
            meth = None
    
        if meth:
            try:
                meth(replyfunc, args)
            except NotOwner:
                pass
        else:
            if not self.on_unknownCommand(replyfunc, cmd, msg):
                self.privmsg(
                    "error Unrecognised command '%s' - type 'help' for help" % cmd)
    
    #@-node:on_msg
    #@+node:on_unknownCommand
    def on_unknownCommand(self, replyfunc, cmd, msg):
        """
        Handler for messages that don't match an existing
        command handler method
        
        Override if you want
        
        Return True if message was handled, or False to cause a
        'type help' reply
        """
        self.action("does not understand '%s'" % msg)
    
    #@-node:on_unknownCommand
    #@-others
    
    #@-node:events
    #@+node:actions
    # action methods
    
    #@+others
    #@+node:pubmsg
    def pubmsg(self, *lines):
        """
        Send a msg to peer
        """
        self.bot.pubmsg(self.peernick, *lines)
    
    #@-node:pubmsg
    #@+node:privmsg
    def privmsg(self, *lines):
        """
        Send a privmsg to peer
        """
        self.bot.privmsg(self.peernick, *lines)
    
    #@-node:privmsg
    #@+node:action
    def action(self, *lines):
    
        self.bot.action(self.peernick, *lines)
    
    #@-node:action
    #@+node:after
    def after(self, delay, func, *args, **kw):
        """
        Schedule a function or method 'func' to be executed
        'secs' seconds from now, with arguments
        """
        self.bot.after(delay, func, *args, **kw)
    
    #@-node:after
    #@-others
    
    #@-node:actions
    #@+node:command handlers
    # command handlers
    
    #@+others
    #@+node:cmd_hi
    def cmd_hi(self, replyfunc, args):
    
        print "cmd_hi: %s" % str(args)
    
        self.privmsg("Hi - type 'help' for help")
    
    #@-node:cmd_hi
    #@+node:cmd_error
    def cmd_error(self, replyfunc, args):
    
        pass
    
    #@-node:cmd_error
    #@+node:cmd_help
    def cmd_help(self, replyfunc, args):
    
        self.privmsg(
            "I am a bot",
            "Available commands:",
            "  help        - display this help",
            "** (end of help listing) **"
            )
    
    #@-node:cmd_help
    #@+node:cmd_die
    def cmd_die(self, replyfunc, args):
    
        #print "** die: %s %s" % (self.peernick, args)
    
        self.barfIfNotOwner()
        self.privmsg("Goodbye, master")
        self.bot.die()
    
    #@-node:cmd_die
    #@-others
    
    #@-node:command handlers
    #@+node:utils
    # util methods
    
    #@+others
    #@+node:barfIfNotOwner
    def barfIfNotOwner(self):
        
        if self.bot.owner != self.peernick:
            self.privmsg("Sorry, but only my owner can tell me to do that")
            raise NotOwner()
    
    #@-node:barfIfNotOwner
    #@-others
    
    #@-node:utils
    #@-others

#@-node:class PrivateChat
#@+node:main
def main():

    bot = MiniBot(
            host="irc.freenode.net",
            nick="mytestbot",
            channel="#freenet-bottest",
            password="fooble",
            )
    bot.run()

#@-node:main
#@+node:mainline
if __name__ == '__main__':
    main()

#@-node:mainline
#@-others
#@-node:@file minibot.py
#@-leo
