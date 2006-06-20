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
class FreenetNodeRefBot:
    """
    A simple IRC bot
    """
    #@    @+others
    #@+node:__init__
    def __init__(self):
    
        confpath = self.confpath = os.path.join(os.path.expanduser("~"), ".freenet_ref_bot")
    
        if os.path.isfile(confpath):
            self.load()
        else:
            self.setup()
    
        self.botnick = self.usernick + "_bot"
        self.realname = "%s's Freenet NodeRef Bot" % self.usernick
        self.peers = {}
    
        self.lastSendTime = time.time()
        self.timeLastChanGreeting = time.time()
        self.sendlock = threading.Lock()
    
        self.nrefs = 0
    
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
    
        opts = self.opts = {}
    
        self.usernick = prompt("Enter your freenode.net nick")
        self.password = prompt("Enter a new password")
        self.refurl = prompt("URL of your noderef")
        self.irchost = prompt("Hostname of IRC server", "irc.freenode.net")
        self.ircport = prompt("Port of IRC server", 6667)
        self.telnethost = prompt("Node Telnet hostname", "127.0.0.1")
        while 1:
            self.telnetport = prompt("Node Telnet port", "2323")
            try:
                self.telnetport = int(self.telnetport)
                break
            except:
                print "Invalid port '%s'" % self.telnetport
    
        self.refs = []
    
        self.save()
    
    #@-node:setup
    #@+node:save
    def save(self):
    
        f = file(self.confpath, "w")
        
        for attr in (
            "usernick", "irchost", "ircport",
            "telnethost", "telnetport",
            "refurl", "password",
            "refs",
            ):
            f.write("%s = %s\n" % (attr, repr(getattr(self, attr))))
    
        f.close()
    
        print "Saved configuration to %s" % self.confpath
    
    #@-node:save
    #@+node:load
    def load(self):
    
        opts = {}
        exec file(self.confpath).read() in opts
        self.__dict__.update(opts)
    
    #@-node:load
    #@+node:run
    def run(self):
    
        self.lock = threading.Lock()
    
        # Create the socket
        self.log("Create socket...")
        #sock = self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = self.sock = socket.socket()
        send = self.sendline
    
        # Connect to server
        connected = False
        port = self.ircport
        ip_addresses = socket.gethostbyname_ex(self.irchost)[2]
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
    
        # get a file from it
        # print "Get file obj..."
        # f = s.makefile()
    
        # Send the nick to server
        self.log("Send nick...")
        send('NICK '+ self.botnick)
    
        # Identify to server
        self.log("Sending USER...")
        send('USER ' + ident + ' ' + self.irchost + ' bla :' + self.realname)
    
        self.log("Entering loop...")
    
        thread.start_new_thread(self.thrd, ())
    
        #send('JOIN ' + chan) #Join a channel
    
        #self.privmsg("nickserv", "identify %s" % self.password)
    
        try:
            self.loop()
        except KeyboardInterrupt:
            print "Terminated by user"
        self.sock.close()
    #@-node:run
    #@+node:loop
    def loop(self):
    
        self.running = 1
        while self.running:
    
            # recieve server messages
            line = self.recvline()
    
            if line.startswith("NOTICE "):
                msg = msg = line.split(" ", 1)[-1].strip()
                self.on_notice("$server", msg)
                continue
    
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
                continue
    
            if typ == "NOTICE":
                self.on_notice(sender, msg)
                continue
    
            if typ == 'JOIN':
                self.on_join(sender)
                continue
    
            if typ == 'PRIVMSG':
                if sender == 'freenode-connect':
                    continue
                if target == self.botnick:
                    self.on_privmsg(sender, msg)
                else:
                    if msg.startswith(self.botnick+":"):
                        text = msg.split(":", 1)[-1].strip()
                        self.on_pubmsg(sender, text)
                    else:
                        self.on_chanmsg(sender, target, msg)
                continue
            
            if typ == 'QUIT':
                self.on_quit(sender)
    
            if typ == 'MODE':
                self.on_mode(msg)
                continue
    
            print "?? sender=%s typ=%s target=%s msg=%s" % (
                repr(sender), repr(typ), repr(target), repr(msg))
    
            continue
    
            # DEPRECATED!!!
    
            if line.find('PRIVMSG') != -1:
                # Call a parsing function
                self.parsemsg(line)
                line = line.rstrip() #remove trailing 'rn'
                line = line.split()
                if(line[0] == 'PING'): #If server pings then pong
                    send('PONG ' + line[1] + '\n')
    
    #@-node:loop
    #@+node:handlers
    # handler methods
    
    #@+others
    #@+node:on_server_msg
    def on_server_msg(self, typ, msg):
        """
        Handles messages from server
        """
        if "End of /MOTD" in msg:
            print "** joining channel %s" % chan
            self.sendline('JOIN ' + chan) #Join a channel
    
        elif "End of /NAMES list" in msg:
            self.identifyPassword()
    
        elif 0:
            if typ != '409':
                print "** server: %s %s" % (repr(typ), msg)
    
    #@-node:on_server_msg
    #@+node:on_notice
    def on_notice(self, sender, msg):
    
        if "Please wait 30 seconds before using REGISTER again" in msg:
            print "Just registered password, waiting 30 seconds..."
            time.sleep(31)
            self.registerPassword()
            print "Registered password!"
    
        elif "If this is your nickname, type /msg NickServ" in msg:
            self.identifyPassword()
    
        elif "The nickname " in msg and "is not registered" in msg:
            self.registerPassword()
    
        elif "Password accepted - you are now recognized" in msg:
            self.log("Password accepted")
            self.greetChannel()
        
        elif 0:
            print "** notice: %s: %s" % (sender, msg)
    
    #@-node:on_notice
    #@+node:on_chanmsg
    def on_chanmsg(self, sender, target, msg):
        """
        Handles a message on the channel, not addressed to the bot
        """
        #print "** chanmsg: %s => %s: %s" % (sender, target, msg)
    
    #@-node:on_chanmsg
    #@+node:on_pubmsg
    def on_pubmsg(self, sender, msg):
        """
        Handles a message to us from peer
        """
        if not self.peers.has_key(sender):
            peer = self.peers[sender] = PrivateChat(self, sender)
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
        if not self.peers.has_key(sender):
            peer = self.peers[sender] = PrivateChat(self, sender)
        else:
            peer = self.peers[sender]
        
        peer.on_privmsg(msg)
        return
    
    #@-node:on_privmsg
    #@+node:on_join
    def on_join(self, sender):
        """
        When another user (or us) have joined
        """
        print "** join: %s" % sender
        
        if sender.endswith("_bot"):
            # send our ref to the bot
            self.privmsg(sender, self.refurl)
    
    #@-node:on_join
    #@+node:on_part
    def on_part(self, sender):
        print "** part: %s" % sender
    
        if sender in self.peers:
            del self.peers[sender]
    
    #@-node:on_part
    #@+node:on_quit
    def on_quit(self, sender):
        print "** quit: %s" % sender
    
        if sender in self.peers:
            del self.peers[sender]
    
    #@-node:on_quit
    #@+node:on_mode
    def on_mode(self, mode):
        
        print "** mode: %s" % mode
    
    #@-node:on_mode
    #@-others
    
    #@-node:handlers
    #@+node:actions
    # action methods
    
    #@+others
    #@+node:greetChannel
    def greetChannel(self):
    
        self.privmsg(
            chan,
            "Hi, I'm %s's noderef swap bot, please privmsg me if you want to swap a ref" \
                % self.usernick
            )
    
        self.timeLastChanGreeting = time.time()
    
    #@-node:greetChannel
    #@+node:notice
    def notice(self, target, msg):
        self.sendline("NOTICE " + target + " :" + msg)
    
    #@-node:notice
    #@+node:chanmsg
    def chanmsg(self, *lines):
        """
        Sends a public msg to channel
        """
        for line in lines:
            self.sendline(":%s PRIVMSG %s :%s" % (self.botnick, chan, line))
    
    #@-node:chanmsg
    #@+node:pubmsg
    def pubmsg(self, peernick, *lines):
        """
        Sends a msg to peer
        """
        for line in lines:
            self.sendline(":%s PRIVMSG %s :%s: %s" % (
                self.botnick, chan, peernick, line))
    
    #@-node:pubmsg
    #@+node:privmsg
    def privmsg(self, target, *lines):
    
        for msg in lines:
            self.sendline(":%s PRIVMSG %s :%s" % (self.botnick, target, msg))
    
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
    #@+node:die
    def die(self):
    
        self.running = 0
    
    #@-node:die
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
    #@+node:log
    def log(self, msg):
        print "** log: %s" % msg
    
    #@-node:log
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
    #@+node:sendline
    def sendline(self, msg):
    
        self.sendlock.acquire()
        
        print "** SEND: %s" % msg
    
        try:
            now = time.time()
            t = now - self.lastSendTime
            if t < 0.5:
                time.sleep(0.5 - t)
            self.sock.send(msg + "\n")
            self.lastSendTime = time.time()
        finally:
            self.sendlock.release()
    
    
    
    
    #@-node:sendline
    #@+node:send
    def send(self, msg):
        #print "SENDING: %s" % msg.strip()
        self.lock.acquire()
        self.sock.send(msg)
        self.lock.release()
    
    #@-node:send
    #@+node:recvline
    def recvline(self):
        """
        receives a single line from server
        """
        sock = self.sock
        chars = []
        while True:
            c = sock.recv(1)
            if c == '\n':
                break
            chars.append(c)
        line = "".join(chars)
        #if 1 or not line.split().endswith("freenode.net"):
        if 0 and ":No origin specified" not in line:
            print "RECVLINE: %s" % line
        return line
    
    #@-node:recvline
    #@-others
    
    #@-node:low level
    #@+node:DEPRECATED
    #@+node:recv
    def recv(self, n):
        buf = self.sock.recv(n)
        print "RECEIVED: %s" % buf.rstrip()
        return buf
    
    #@-node:recv
    #@+node:syscmd
    def syscmd(self, commandline, channel):
    
        cmd = commandline.replace('sys ','')
        cmd = cmd.rstrip()
        os.system(cmd + ' >temp.txt')
        a = open('temp.txt')
        ot = a.read()
        ot.replace('\n', '|')
        a.close()
        self.send('PRIVMSG ' + channel + ' :' + ot + '\n')
        return 0
    
    #@-node:syscmd
    #@+node:parsemsg
    def parsemsg(self, msgtxt):
        print "parsemsg: msg=%s" % msgtxt.rstrip()
    
        # Parse the message into useful data
        complete = msgtxt[1:].split(':', 1)
        info = complete[0].split(' ')
        msgpart = complete[1]
        sender = info[0].split('!')
    
        msg = {}
        msg['fromnick'] = sender[0]
        msg['fromaddr'] = sender[1]
        msg['text'] = msgpart.rstrip()
        msg['dest'] = info[2]
    
        #print "   info=%s" % repr(info)
        #print "   msgpart=%s" % repr(msgpart)
        #print "   sender=%s" % repr(sender)
        print msg
        
        if msgpart[0] == '`' and sender[0] == self.usernick:
            # Treat all messages starting with '`' as command
            cmd = msgpart[1:].split(' ')
            if cmd[0] == 'op':
                s.send('MODE ' + info[2] + ' +o ' + cmd[1] + '\n')
            if cmd[0] == 'deop':
                s.send('MODE ' + info[2] + ' -o ' + cmd[1] + '\n')
            if cmd[0] == 'voice':
                s.send('MODE ' + info[2] + ' +v ' + cmd[1] + '\n')
            if cmd[0] == 'devoice':
                s.send('MODE ' + info[2] + ' -v ' + cmd[1] + '\n')
            if cmd[0] == 'sys':
                syscmd(msgpart[1:], info[2])
        
        if msgpart[0] == '-' and sender[0] == self.usernick:
            # Treat msgs with - as explicit command to send to server
            cmd = msgpart[1:]
            s.send(cmd + '\n')
            print 'cmd=' + cmd
    
    #@-node:parsemsg
    #@-node:DEPRECATED
    #@-others
#@-node:class FreenetNodeRefBot
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
    
        self.on_anymsg(self.pubmsg, msg)
    #@-node:on_pubmsg
    #@+node:on_privmsg
    def on_privmsg(self, msg):
    
        self.on_anymsg(self.privmsg, msg)
    
    #@-node:on_privmsg
    #@+node:on_anymsg
    def on_anymsg(self, replyfunc, msg):
    
        print "** on_anymsg: %s: %s" % (self.peernick, msg)
    
        parts = msg.split()
        cmd = parts[0]
        args = parts[1:]
        print "cmd=%s" % repr(cmd)
    
        if cmd.startswith("http://"):
            if cmd not in self.bot.refs:
                self.addref(cmd)
                replyfunc(self.bot.refurl)
            else:
                replyfunc("error already have your ref")
            return
    
    
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
            self.privmsg("Unrecognised command '%s' - please type 'help' for help" % cmd)
    
    #@-node:on_anymsg
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
        
        if self.bot.usernick != self.peernick:
            self.privmsg("Sorry, but only my owner can tell me to do that")
            raise NotOwner()
    
    #@-node:barfIfNotOwner
    #@-others
    
    #@-node:utils
    #@-others

#@-node:class PrivateChat
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

    bot = FreenetNodeRefBot()
    bot.run()

#@-node:main
#@+node:mainline
if __name__ == '__main__':
    main()

#@-node:mainline
#@-others
#@-node:@file refbot.py
#@-leo
