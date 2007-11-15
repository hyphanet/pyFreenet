#!/usr/bin/env python
#@+leo-ver=4
#@+node:@file minibot.py
#@@first
"""
An IRC bot for exchanging noderefs with peer freenet users
"""
#@+others
#@+node:imports
import os #not necessary but later on I am going to use a few features from this
import sched
import select
import socket
import string
import sys
import thread
import threading
import time
import traceback

has_platform_module = False;
try:
  import platform;
  has_platform_module = True;
except:
  pass

#@-node:imports
#@+node:globals
progname = sys.argv[0]
args = sys.argv[1:]
nargs = len(args)
logfilepath = None
logfile = None

# bot transmit queue priority levels
TXQUEUE_PRIO_PREMIUM = 1
TXQUEUE_PRIO_EXPRESS = 2
TXQUEUE_PRIO_STANDARD = 3
TXQUEUE_PRIO_BULK = 4

#@-node:globals
#@+node:exceptions
class NotOwner(Exception):
    """
    peer is telling us to do something only owners can tell us to
    """

class NotPrivateMessage(Exception):
    """
    peer is telling us to do something that we'll only do when it's sent in a private message
    """

class TimeToQuit(Exception):
    """
    Terminates the bot gracefully
    """

class DieImmediately(Exception):
    """
    Terminates the bot ungracefully
    """

class DoneSayingGoodbye(Exception):
    """
    Nothing more to say before leaving IRC
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
        global logfilepath, logfile
        
        self.host = kw['host']
        self.port = kw.get('port', 6667)
        self.channel = kw['channel']
        self.nick = kw['nick']
        self.owner = kw.get('owner', None)
        self.ident = kw.get('ident', 'FreenetRefBot')
        self.password = kw['password']
        self.peerclass = kw.get('peerclass', PrivateChat)
        logfilepath = kw.get('logfilepath', None)
        logfile = None
        
        realname = kw.get('realname', None)
        if not realname:
            if self.owner:
                realname = "%s's IRC MiniBot" % self.owner
            else:
                realname = "%s the MiniBot" % self.nick
        self.realname = realname
    
        self.hasIdentified = False
        self._running = False
        self.peers = {}
        self.lastSendTime = time.time()
    
        self.usersInChan = []
    
        self.rxbuf = []
        self.txqueues = {}
        self.txqueues[ TXQUEUE_PRIO_PREMIUM ] = []
        self.txqueues[ TXQUEUE_PRIO_EXPRESS ] = []
        self.txqueues[ TXQUEUE_PRIO_STANDARD ] = []
        self.txqueues[ TXQUEUE_PRIO_BULK ] = []
        self.txqueuepriorities = self.txqueues.keys()
        self.txqueuepriorities.sort()
        self.txtimes = []
        self.restartCount = 0
        self.restartDelay = 45
        self.sock = None
        self.stopReason = None
    
    #@-node:__init__
    #@+node:run
    def run(self):
    
        self._keepRunning = True
    
        while True:
            log("Starting main run() while loop...")
    
            self.sched = sched.scheduler(time.time, time.sleep)
            self._running = True
    
            # this flag gets set if the bot restarts due to the server
            # sending it off into la-la land. setting this to True
            # suppresses call to self.greetChannel
            self._restarted = False
    
            self.sock = None
            self.connect()
    
            try:
                self._using_scheduler = True
                self.sched.run()
    
            except DieImmediately:
                self._keepRunning = False
                my_exit( 0 )
    
            except DoneSayingGoodbye:
                self._keepRunning = False
                my_exit( 0 )
    
            except KeyboardInterrupt:
                self._keepRunning = False
                log("Terminated by user")
                self.stopReason = "Terminated by user"
                
            except TimeToQuit:
                self._keepRunning = False
                log("Quitting")
                self.stopReason = "Quitting"
    
            except MemoryError:
                log_traceback()
                log("Got MemoryError exception; Terminating.")
                self._keepRunning = False
                self.stopReason = "MemoryError"
    
            except NotReceiving:
                self._using_scheduler = False
                self.sock.close()
                self.sock = None
                self.hasIdentified = False
                log("** ERROR: server is ignoring us, restarting in 3 seconds...")
                time.sleep(3)
                self._restarted = True
                continue
    
            except:
                log("?? ERROR: Uncaught Exception:")
                log_traceback()
                self._using_scheduler = False
                #
                #
                # **FIXME** Try to get a handle on what's causing these problems without broadcasting them to the whole channel
                #
                try:
                    exc_type, exc_value = sys.exc_info()[ :2 ]
                    traceback_list = traceback.extract_tb( sys.exc_info()[ 2 ] )
                    reported_traceback = ''
                    for traceback_item in traceback_list:
                        traceback_line = traceback_item[ 1 ]
                        traceback_file = traceback_item[ 0 ]
                        traceback_file_fields = traceback_file.split( "/" )
                        traceback_file = traceback_file_fields[ -1 ]
                        traceback_file_fields = traceback_file.split( "\\" )
                        traceback_file = traceback_file_fields[ -1 ]
                        reported_traceback += "%d:%s|" % ( traceback_line, traceback_file )
                    if( '|' == reported_traceback[ -1 ] ):
                        reported_traceback = reported_traceback[ : -1 ]
                    error_msg = "Exception: type=[%s]  value=[%s]  traceback=[%s]  revisions=[%s]" % ( exc_type, exc_value, reported_traceback, self.getRevisionsString() )
                except:
                    error_msg = "Exception while generating the exception message"
                    log("?? ERROR: Exception while generating the exception message:")
                    log_traceback()
                if( "Zothar" in self.usersInChan ):
                    self.privmsg(
                        "Zothar",
                        "Uncaught exception in main run() loop of minibot.py: %s" % ( error_msg )
                        )
                elif( "Zothar_Work" in self.usersInChan ):
                    self.privmsg(
                        "Zothar_Work",
                        "Uncaught exception in main run() loop of minibot.py: %s" % ( error_msg )
                        )
                elif( "Zothar70d_bot" in self.usersInChan ):
                    self.privmsg(
                        "Zothar_Work",
                        "Uncaught exception in main run() loop of minibot.py: %s" % ( error_msg )
                        )
                self.part_and_quit( "Uncaught Exception" )
                self.sock.close()
                self.sock = None
                self.hasIdentified = False
                self.restartCount += 1
                if( self.restartCount > 7 ):
                    log("** ERROR: bot crashed and won't be restarted as it apparently needs user attention if it crashes this many times; please consider filing a bug report at https://bugs.freenetproject.org/ if it seems appropriate.")
                    self._keepRunning = False
                    break
                log("** ERROR: bot crashed, restarting in %d seconds..." % (self.restartDelay))
                time.sleep(self.restartDelay)  # a repeatedly crashing bot can be very annoying to other IRCers on the channel
                self.restartDelay = self.restartDelay * 2  # Exponential "backoff"
                continue
    
            if not self._keepRunning:
                self._using_scheduler = False
                if( None != self.sock ):
                    if( None != self.stopReason ):
                        self.part_and_quit( self.stopReason );
                    else:
                        self.part_and_quit( "*Poof*" )
                    self.sock.close()
                    self.sock = None
                break
                
        my_exit( 0 );
    
    #@-node:run
    #@+node:connect
    def connect(self):
    
        # Create the socket
        log("Create socket...")
    
        sock = self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock = self.sock = socket.socket()
    
        #send = sock.send
        send = self.sendline
    
        # Connect to server
        connected = False
        port = self.port
        try:
            ip_addresses = socket.gethostbyname_ex(self.host)[2]
        except:
            log("Nameservice trouble looking up %s  Couldn't get a connection" % ( self.host ))
            return
        # Doesn't work well this way as the first connection attempt needs to be cleared cleanly before trying the next and I'm missing something ATM
        #try:
        #    sock.settimeout(15)
        #except:
        #    # Ignore on pre-2.3 hopefully
        #    log("Setting default socket timeout failed; running in Python pre-2.3?")
        #    log_traceback()
        for ip in ip_addresses:
            log("Connect to %s:%s" % (ip, port))
            try:
                sock.connect((ip, port))
                connected = True
                log("Connected to %s:%s" % (ip,port))
                break
            except:
                #sock.close()
                #log_traceback()
                log("Failed to connect to %s:%s" % (ip, port))
    
        if not connected:
            log("Couldn't get a connection")
            self.sock = None
            return
    
        self._lastRxTime = time.time()
    
        # Send the nick to server
        log("Send nick...")
        send('NICK '+ self.nick)
    
        # Identify to server
        log("Sending USER...")
        send('USER ' + self.ident + ' ' + self.host + ' bla :' + self.realname)
    
        # plant initial tasks
        self.after(0, self._receiver)
        self.after(1, self._sender)
        self.after(5, self._watchdog)
        self.after(42, self._pinger)
    
    #@-node:connect
    #@+node:handlers
    # handler methods
    
    #@+others
    #@+node:on_chanmsg
    def on_chanmsg(self, sender, target, msg):
        """
        Handles a message on the channel, not addressed to the bot
        """
        log("** chanmsg: %s => %s: %s" % (sender, target, repr(msg)))
    
    #@-node:on_chanmsg
    #@+node:on_error
    def on_error(self, sender, error_type, msg):
    
        log("** error: %s -> :%s: %s" % (sender, error_type, msg))
        if( "Closing Link" == error_type ):
            raise DoneSayingGoodbye
        log("?? unhandled error from server: type=%s msg=%s" % ( error_type, msg ))
    
    #@-node:on_error
    #@+node:on_join
    def on_join(self, sender, target):
        """
        When another user (or us) have joined
        """
        if sender == self.nick:
            return
        if(target[ 0 ] == ':'):
            target = target[ 1: ]
        log("** join: %s -> %s" % ( sender, target ))
        if( sender not in self.usersInChan ):
            self.usersInChan.append(sender)
        #log("** users: %s" % ( self.usersInChan ));
        self.post_on_join(sender, target)
        
    #@-node:on_join
    #@+node:on_kick
    def on_kick(self, sender, channel, target, msg):
        """
        When a user has been kicked from a channel
        """
        log("** kick: %s kicked %s from %s with %s" % ( sender, target, channel, msg ))
    
        if sender == self.nick:
            return
        if target == self.nick:
            # If we got kicked, it's probably for a good reason, so die ungracefully and let the owner deal with it
            log("NOTICE")
            log("NOTICE")
            log("NOTICE")
            log("NOTICE: The bot was kicked from the channel by %s with the following reason: %s" % ( sender, msg ))
            log("NOTICE: The bot may be misbehaving, so you'll want to address the reason for the kick before restarting the bot.")
            log("NOTICE")
            log("NOTICE")
            log("NOTICE")
            raise DieImmediately
        if target in self.peers:
            del self.peers[target]
        if( target in self.usersInChan ):
            self.usersInChan.remove(target)
        #log("** users: %s" % ( self.usersInChan ));
        self.post_on_kick(sender, channel, target, msg)
    
    #@-node:on_kick
    #@+node:on_mode
    def on_mode(self, mode):
        
        log("** mode: %s" % mode)
    
    #@-node:on_mode
    #@+node:on_nick
    def on_nick(self, sender, target):
        """
        When another user (or us) have changed nicks
        """
        if(target[ 0 ] == ':'):
            target = target[ 1: ]
        log("** nick: %s -> %s" % ( sender, target ))
        target = self.stripNickSpecialChars(target)
        if( sender in self.usersInChan ):
            self.usersInChan.remove(sender)
        if( target not in self.usersInChan ):
            self.usersInChan.append(target)
        #log("** users: %s" % ( self.usersInChan ));
        self.post_on_nick(sender, target)
    
    #@-node:on_nick
    #@+node:on_notice
    def on_notice(self, sender, msg):
    
        log("** notice: %s: %s" % (sender, msg))
        if "Please wait " in msg and " seconds before using REGISTER again" in msg:
            waitsecondsbuf = msg.replace( "Please wait ", "" ).replace( " seconds before using REGISTER again", "" )
            try:
              waitseconds = int( waitsecondsbuf )
            except:
              log("?? ERROR: Failed to parse '%s' as an integer.  Perhaps minibot.py needs an update for an IRC server behavior change." % ( waitsecondsbuf ))
              my_exit( 1 );
            log("Just registered password, waiting %d seconds..." % ( waitseconds ))
            self.after(waitseconds + 1, self.registerPassword)
            return
    
        elif "If this is your nickname, type /msg NickServ" in msg:
            self.after(1, self.identifyPassword)
    
        elif "The nickname " in msg and "is not registered" in msg:
            self.registerPassword()
    
        elif "Password accepted - you are now recognized" in msg:
            log("Password accepted")
            if(not self.hasIdentified):
              self.hasIdentified = True
              self.joinChannel()
    
        elif "Your nickname is now registered" in msg:
            log("Password registered")
            if(not self.hasIdentified):
              self.hasIdentified = True
              self.joinChannel()
    
    #@-node:on_notice
    #@+node:on_part
    def on_part(self, sender, target, msg):
        """
        When another user (or us) have left a channel
        """
        log("** leave: %s <- %s with %s" % ( sender, target, msg ))
    
        if sender in self.peers:
            del self.peers[sender]
        if( sender in self.usersInChan ):
            self.usersInChan.remove(sender)
        #log("** users: %s" % ( self.usersInChan ));
        self.post_on_part(sender, target, msg)
    
    #@-node:on_part
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
    #@+node:on_quit
    def on_quit(self, sender, msg):
        """
        When another user (or us) have quit a server
        """
        log("** quit: %s with %s" % ( sender, msg ))
    
        if sender in self.peers:
            del self.peers[sender]
        if( sender in self.usersInChan ):
            self.usersInChan.remove(sender)
        #log("** users: %s" % ( self.usersInChan ));
        self.post_on_quit(sender, msg)
    
    #@-node:on_quit
    #@+node:on_raw_rx
    def on_raw_rx(self, line):
        """
        Called when a raw line comes in from server
        """
        if line.startswith("NOTICE "):
            msg = line.split(" ", 1)[-1].strip()
            self.on_notice("$server", msg)
            return
    
        if line.startswith("ERROR "):
            errorlinefields = line.split(":", 2)
            error_type = errorlinefields[ 1 ]
            msg = errorlinefields[ 2 ][ 1: ]
            self.on_error("$server", error_type, msg)
            return
    
        parts = line.split(" ", 3)
        if( len( parts ) == 0 ):
            log("?? no parts could be split from: %s" % ( line ));
            return;
        sender = parts[0]
    
        sender = sender[1:]
        if sender.endswith(".freenode.net") or sender == self.host:
            sender = "$server$"
        else:
            sender = self.stripNickSpecialChars(sender.split("!")[0])
    
        if( len( parts ) == 1 ):
            log("?? only 1 part could be split from: %s" % ( line ));
            return;
        typ = parts[1]
    
        if( len( parts ) == 2 ):
            log("?? only 2 parts could be split from: %s" % ( line ));
            return;
        target = parts[2].strip()
        if len(parts) > 3:
            msg = parts[3][1:].rstrip()
        else:
            msg = ''
    
        if sender == '$server$':
            self.on_server_msg(typ, msg, line)
            return
    
        if typ == 'JOIN':
            self.on_join(sender, target)
        elif typ == 'KICK':
            channel = target
            target, msg = parts[3].split(" :", 1)
            self.on_kick(sender, channel, target, msg)
        elif typ == 'MODE':
            self.on_mode(msg)
        elif typ == 'NICK':
            self.on_nick(sender, target)
        elif typ == "NOTICE":
            self.on_notice(sender, msg)
        elif typ == 'PART':
            self.on_part(sender, target, msg)
        elif typ == 'PRIVMSG':
            if sender == 'freenode-connect':
                return
            if target.lower() == self.nick.lower():
                self.on_privmsg(sender, msg)
            else:
                if msg.lower().startswith(self.nick.lower()+":"):
                    text = msg.split(":", 1)[-1].strip()
                    self.on_pubmsg(sender, text)
                elif msg.lower().startswith(self.nick.lower()+">"):
                    text = msg.split(">", 1)[-1].strip()
                    self.on_pubmsg(sender, text)
                elif msg.lower().startswith(self.nick.lower()+"]"):
                    text = msg.split("]", 1)[-1].strip()
                    self.on_pubmsg(sender, text)
                elif msg.lower().startswith(self.nick.lower()+" "):
                    text = msg.split(" ", 1)[-1].strip()
                    self.on_pubmsg(sender, text)
                else:
                    self.on_chanmsg(sender, target, msg)
        elif typ == 'QUIT':
            if len(parts) > 2:
                quit_msg = string.join(parts[2:], " ")[1:].rstrip()
            else:
                quit_msg = ''
            self.on_quit(sender, quit_msg)
        else:
            log("?? sender=%s typ=%s target=%s msg=%s line=[%s]" % (
                repr(sender), repr(typ), repr(target), repr(msg), repr(line)))
        # NOTE: Should only return as it's been factored out of the above ifs
    
    #@-node:on_raw_rx
    #@+node:on_ready
    def on_ready(self):
        """
        Invoked when bot is fully signed in, on channel and ready to play
        """
        self.greetChannel()
    
    #@-node:on_ready
    #@+node:on_server_msg
    def on_server_msg(self, typ, msg, line):
        """
        Handles messages from server
        """
        svrmsglinefields = line.split(" ", 3)
        svrmsg_type = svrmsglinefields[ 1 ]
        svrmsg_text = svrmsglinefields[ 3 ]
        if typ == 'PONG':
            pass
        elif typ in [ '004', '005' ]:
            log("** server: %s %s" % (repr(svrmsg_type), svrmsg_text))
        elif typ in [ '001', '002', '003', '250', '251', '255', '265', '266', '372', '375', '376' ]:
            log("** server: %s %s" % (repr(typ), msg))
        elif typ in [ '252', '254' ]:
            textfields = svrmsg_text.split(":", 1)
            svrmsg_int = textfields[ 0 ][ : -1 ]
            svrmsg_text = textfields[ 1 ]
            log("** server: %s %s %s" % (repr(svrmsg_type), repr(svrmsg_int), svrmsg_text))
        elif typ in [ '366', '401', '403', '433', '442' ]:
            textfields = svrmsg_text.split(":", 1)
            svrmsg_nick_channel = textfields[ 0 ][ : -1 ]
            svrmsg_text = textfields[ 1 ]
            log("** server: %s %s %s" % (repr(svrmsg_type), repr(svrmsg_nick_channel), svrmsg_text))
            if( '401' == typ and "nickserv" == svrmsg_nick_channel):
                self.die()
        elif typ not in [ '353', '409' ]:
            log("** server: %s %s\n**** line=[%s]" % (repr(typ), msg, line))
        if "End of /MOTD" in msg:
            if(not self.hasIdentified):
                self.after(5, self.identifyPassword)
            return
    
        elif "End of /NAMES list" in msg:
            self.on_ready()
            return
    
        elif typ == '353':
            msgparts = msg.split()
            if msgparts[0] == self.channel and msgparts[1] == (":"+self.nick):
                for user in msgparts[2:]:
                    self.usersInChan.append(self.stripNickSpecialChars(user))
                log("** users in %s: %s" % (self.channel, self.usersInChan))
                return
    
    #@-node:on_server_msg
    #@+node:post_on_join
    def post_on_join(self, sender, target):
        """
        When another user (or us) have joined (post processing by inheriting class)
        """
        pass
        
    #@-node:post_on_join
    #@+node:post_on_kick
    def post_on_kick(self, sender, channel, target, msg):
        """
        When a user has been kicked from a channel (post processing by inheriting class)
        """
        pass
    
    #@-node:post_on_kick
    #@+node:post_on_nick
    def post_on_nick(self, sender, target):
        """
        When another user (or us) have changed nicks (post processing by inheriting class)
        """
        pass
    
    #@-node:post_on_nick
    #@+node:post_on_part
    def post_on_part(self, sender, target, msg):
        """
        When another user (or us) have left a channel (post processing by inheriting class)
        """
        pass
    
    #@-node:post_on_part
    #@+node:post_on_quit
    def post_on_quit(self, sender, msg):
        """
        When another user (or us) have quit a server (post processing by inheriting class)
        """
        pass
    
    #@-node:post_on_quit
    #@-others
    
    #@-node:handlers
    #@+node:actions
    # action methods
    
    #@+others
    #@+node:greetChannel
    def greetChannel(self):
    
        self.privmsg(self.channel, "Hi, I'm %s" % self.realname)
    
    #@-node:greetChannel
    #@+node:joinChannel
    def joinChannel(self):
    
        log("** joining channel %s" % self.channel)
        self.sendline('JOIN ' + self.channel) #Join a channel
    
    #@-node:joinChannel
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
    #@+node:part_and_quit
    def part_and_quit(self, reason):
        """
        Parts the channel informatively and quits from the IRC server
        """
        self.pre_part_and_quit( reason )
        self.sendline( 'PART ' + self.channel + ' :' + reason )
        self.sendline( 'QUIT :' + reason )
        try:
            while( 0 < self.getsendqueuesize() ):
                self._receiver();
                self._sender();
                time.sleep( 0.25 )
            startTime = time.time();
            while( 15 > ( time.time() - startTime )):
                self._receiver();
                time.sleep( 0.25 )
        except DoneSayingGoodbye:
            pass
        except NotReceiving:
            pass
        except socket.error, msg:
            log( "** ERROR: socket error: %s" % ( msg ))
        except TimeToQuit:
            pass
        except:
            log( "** ERROR: caught unhandled exception while saying goodbye:" )
            log_traceback()
        time.sleep( 1 )
        
    #@-node:part_and_quit
    #@+node:pre_part_and_quit
    def pre_part_and_quit(self, reason):
        """
        Called before doing anything in part_and_quit() (pre processing by inheriting class)
        """
        pass
        
    #@-node:pre_part_and_quit
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
    
    #@-node:registerPassword
    #@+node:identifyPassword
    def identifyPassword(self):
        """
        sends an 'identify <password>' command to nickserv
        """
        # **FIXME** Need to store knowledge of whether we've successfully registered and if not, call registerPassword from here instead of identifying (cleaner code/faster first time startup)
        if(self.hasIdentified):
            return;    # Don't need to identify if we have already
        self.privmsg("nickserv", "identify %s" % self.password)
    
    #@-node:identifyPassword
    #@+node:after
    def after(self, delay, func, *args, **kw):
        """
        Schedule a function or method 'func' to be executed
        'secs' seconds from now, with arguments
        """
        if self._running:
            pri = kw.get('priority', 3)
            return self.sched.enter(delay, pri, func, args)
        return None
    
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
    #@+node:sendline
    def sendline(self, msg, target = None, priority = TXQUEUE_PRIO_STANDARD):
    
        # **FIXME** Implement storage of target in queue for later additional efficiencies
        self.txqueues[ priority ].append(msg)
    
    #@-node:sendline
    #@+node:getRevisionsString
    def getRevisionsString(self):
        """
        Return a string of the relevant file revisions (should be overridden inheriting class)
        """
        return "minibot.py:%s" % ( MiniBot.svnRevision )
        
    #@-node:getRevisionsString
    #@+node:getsendqueuesize
    def getsendqueuesize(self):

        total_count = 0;
        for priority in self.txqueuepriorities:
            total_count += len( self.txqueues[ priority ] )
        return total_count
    
    #@-node:getsendqueuesize
    #@+node:_sender
    def _sender(self):
    
        if self._using_scheduler:
            fast_send_time = 0.5
            slow_send_time = 2.5
            check_time_range = 30
            slow_send_time_threshold = 6
            next_send_time = fast_send_time
            self.txtimes.append(time.time())
            while((time.time() - self.txtimes[ 0 ]) > check_time_range):
                self.txtimes = self.txtimes[ 1: ]
            recent_sent = len(self.txtimes)
            if(recent_sent >= slow_send_time_threshold):
                next_send_time = slow_send_time
            self.after(next_send_time, self._sender)
    
        for priority in self.txqueuepriorities:
            if( 0 >= len( self.txqueues[ priority ] )):
                continue;
            msg = self.txqueues[ priority ].pop(0)
    
            if 0 or not msg.startswith( "PING" ):
                log("** SEND: %s" % msg)
    
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
    
        if self._using_scheduler:
            self.after(0.1, self._receiver)
    
    #@-node:_receiver
    #@+node:_pinger
    def _pinger(self):
        
        self.sendline("PING %s %s" % ( self.nick, self.host  ))
        self.after(42, self._pinger)
    
    #@-node:_pinger
    #@+node:_watchdog
    def _watchdog(self):
        
        #log("** watchdog: WOOF!")
    
        if time.time() - self._lastRxTime > 60:
            log("** watchdog: server is ignoring us, fire a restart...")
            raise NotReceiving
    
        self.after(10, self._watchdog)
    
    #@-node:_watchdog
    #@-others
    
    #@-node:low level
    #@-others
    #@+node:utils
    # util methods
    
    #@+others
    #@+node:stripNickSpecialChars
    def stripNickSpecialChars(self, nickString):
    
        while( nickString[ 0 ] in [ '@' ] ):
            nickString = nickString[ 1: ]
        return nickString
    
    #@-node:stripNickSpecialChars
    #@-others
    
    #@-node:utils
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
        self.rxtimes = []
        self.last_ignore_start = None
        self.last_help = None
    
    #@-node:__init__
    #@+node:events
    # event handling methods
    
    #@+others
    #@+node:on_pubmsg
    def on_pubmsg(self, msg):
    
        self.on_msg(self.pubmsg, msg, False)
    #@-node:on_pubmsg
    #@+node:on_privmsg
    def on_privmsg(self, msg):
    
        self.on_msg(self.privmsg, msg, True)
    
    #@-node:on_privmsg
    #@+node:on_msgf
    def on_msg(self, replyfunc, msg, is_from_privmsg):
    
        check_time_range = 10
        ignore_time = 15
        min_help_time = 60
        received_too_fast_threshold = 4  # ignores starting at this
        self.rxtimes.append(time.time())
        while((time.time() - self.rxtimes[ 0 ]) > check_time_range):
            self.rxtimes = self.rxtimes[ 1: ]
        recent_received = len(self.rxtimes)
        if(recent_received >= received_too_fast_threshold):
            if(self.last_ignore_start == None or (time.time() - self.last_ignore_start) > ignore_time):
                self.last_ignore_start = time.time()
                self.privmsg("error It looks to me like you're talking too fast.  I'll ignore you until you've stopped \"babbling\" for awhile.")
            log("** on_anymsg: IGNORING BABBLER: %s: %s" % (self.peernick, msg))
            return
        log("** on_anymsg: %s: %s" % (self.peernick, msg))
    
        parts = msg.split()
        if(len(parts) < 1):
            parts = [ '', '' ]
        elif(len(parts) < 2):
            parts.append('')
        cmd = parts[0]
        args = parts[1:]
        
        if(cmd == "help"):
            if(self.last_help == None):
                self.last_help = time.time()
            elif((time.time() - self.last_help) < min_help_time):
                self.last_help = time.time()
                self.privmsg("error I've already sent you my help information recently.")
                log("** cmd: IGNORING HELPLESS: %s" % (cmd))
                return
    
        #log("** cmd=%s" % repr(cmd))
    
        try:
            meth = getattr(self, "cmd_" + cmd)
        except:
            meth = None
    
        if meth:
            try:
                meth(replyfunc, is_from_privmsg, args)
            except NotOwner:
                pass
            except NotPrivateMessage:
                pass
        else:
            if not self.on_unknownCommand(replyfunc, is_from_privmsg, cmd, msg):
                self.privmsg(
                    "error Unrecognised command '%s' - type 'help' for help" % cmd)
    
    #@-node:on_msg
    #@+node:on_unknownCommand
    def on_unknownCommand(self, replyfunc, is_from_privmsg, cmd, msg):
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
    #@+node:notice
    def notice(self, *lines):
        """
        Send a notice to peer
        """
        self.bot.notice(self.peernick, *lines)
    
    #@-node:notice
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
    #@+node:cmd_die
    def cmd_die(self, replyfunc, is_from_privmsg, args):
    
        #log("** die: %s %s" % (self.peernick, args))
    
        self.barfIfNotOwner()
        if(not is_from_privmsg):
            self.privmsg("Sorry, but that command will only be honored in a /msg")
            raise NotPrivateMessage()
        self.notice("Goodbye, master")
        self.bot.die()
    
    #@-node:cmd_die
    #@+node:cmd_error
    def cmd_error(self, replyfunc, is_from_privmsg, args):
    
        pass
    
    #@-node:cmd_error
    #@+node:cmd_help
    def cmd_help(self, replyfunc, is_from_privmsg, args):
    
        self.privmsg(
            "I am a bot",
            "Available commands:",
            "  help        - display this help",
            "** (end of help listing) **"
            )
    
    #@-node:cmd_help
    #@+node:cmd_hi
    def cmd_hi(self, replyfunc, is_from_privmsg, args):
    
        log("cmd_hi: %s" % str(args))
    
        self.privmsg("Hi - type 'help' for help")
    
    #@-node:cmd_hi
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
#@+node:log
def log(msg):
    global logfilepath, logfile
    
    formatted_msg = "%s: %s\n" % (time.strftime("%Y%m%d-%H%M%S"), msg)
    sys.stdout.write(formatted_msg)
    sys.stdout.flush()
    if( None == logfile and None != logfilepath ):
        logfile = file( logfilepath, "w+" )
    if( None != logfile ):
        logfile.write(formatted_msg)

#@-node:log
#@+node:log_traceback
def log_traceback():
    traceback_items = traceback.format_exception( sys.exc_info()[ 0 ], sys.exc_info()[ 1 ], sys.exc_info()[ 2 ] )
    for traceback_item in traceback_items:
        while( traceback_item.endswith("\n") ):
            traceback_item = traceback_item[ : -1 ]
        traceback_item_lines = traceback_item.split("\n")
        for traceback_item_line in traceback_item_lines:
            log(traceback_item_line)

#@-node:log_traceback
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
#@+node:my_exit
def my_exit( exit_status ):
    global logfilepath, logfile
    
    log("Closing program with an exit status of %s" % ( exit_status ))
    if( None != logfile ):
        logfile.close()
    if( not has_platform_module or ( has_platform_module and "Windows" == platform.system())):
        raw_input( "Hit Enter or Return to continue..." );
    sys.exit( exit_status );

#@+node:my_exit
#@+node:mainline
if __name__ == '__main__':
    main()

#@-node:mainline
#@-others
#@-node:@file minibot.py
#@-leo
