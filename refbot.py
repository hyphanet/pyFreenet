#!/usr/bin/env python
#@+leo-ver=4
#@+node:@file refbot.py
#@@first
"""
An IRC bot for exchanging noderefs with peer freenet users
"""
#@+others
#@+node:imports
import StringIO
import base64
import math
import os
import os.path
import random
import select
import socket
import string
import struct
import sys
import threading
import time
import traceback
import urllib2
import urlparse

import fcp
from minibot import log, log_traceback, MiniBot, PrivateChat, my_exit

have_plugin_module = False;
try:
  import botplugin;
  have_plugin_module = True;
except Exception, msg:
  pass;

#@-node:imports
#@+node:globals
progname = sys.argv[0]
args = sys.argv[1:]
nargs = len(args)

ident = 'FreenetRefBot'

announcerTokenHolderPickDelay = 300
current_config_version = 5

obscenities = ["fuck", "cunt", "shit", "asshole", "fscking", "wank"]
reactToObscenities = False

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

    bogon_filename = "bogon-bn-agg.txt";  # Get updates from http://www.cymru.com/Documents/bogon-bn-agg.txt
    bogons = {};
    bot_filepath = sys.argv[ 0 ];
    if( os.path.islink( bot_filepath )):
        bot_filepath = os.path.realpath( bot_filepath );
    bot_install_directory = os.path.dirname( bot_filepath );
    if( '' == bot_install_directory ):
      bot_install_directory = '.';
    if( '/' != bot_install_directory[ -1 ] ):
        bot_install_directory += '/';
    minimumFCPNodeRevision = 15720;
    minimumMiniBotRevision = 15715;
    minimumNodeBuild = 1073;
    svnLongRevision = "$Revision$"
    svnRevision = svnLongRevision[ 11 : -2 ]
    versions_filename = "updater_versions.dat";

    #@    @+others
    #@+node:__init__
    def __init__(self, cfgFile=None):
        """
        Takes one optional argument - alternative pathname
        """

        self.bots = {}
        self.botAnnouncePool = []
        self.botDarknetIdentities = {}
        self.botOpennetIdentities = {}
        self.botTimeWhenStarted = time.time();
        self.seenChannelUsers = []
            
        # check that we've got a revision capable fcp/node.py (must be before using it)
        try:
            fcpnodepy_revision = fcp.FCPNode.svnRevision;
        except:
            log("***");
            log("*** This version of the refbot requires a newer version of fcp/node.py.  Please run updater.py and try again.");
            log("***");
            my_exit( 1 );
        # check that we've got a revision capable minibot.py (must be before using it)
        try:
            minibotpy_revision = MiniBot.svnRevision;
        except:
            log("***");
            log("*** This version of the refbot requires a newer version of minibot.py.  Please run updater.py and try again.");
            log("***");
            my_exit( 1 );
        
        log("Starting refbot with the following file versions: refbot.py: r%s  minibot.py: r%s  fcp/node.py: r%s" % (FreenetNodeRefBot.svnRevision, MiniBot.svnRevision, fcp.FCPNode.svnRevision))
        
        # check refbot release age
        log("Checking refbot release age....")
        if( not os.path.exists( FreenetNodeRefBot.bot_install_directory + FreenetNodeRefBot.versions_filename )):
            FreenetNodeRefBot.versions_file = file( FreenetNodeRefBot.bot_install_directory + FreenetNodeRefBot.versions_filename, "w+" );
            FreenetNodeRefBot.versions_file.write( "\n" );
            FreenetNodeRefBot.versions_file.close();
        else:
            last_version_file_mod_time = os.path.getmtime( FreenetNodeRefBot.bot_install_directory + FreenetNodeRefBot.versions_filename );
            now = time.time();
            last_version_file_age = now - last_version_file_mod_time;
            minute_seconds = 60;
            hour_seconds = 60 * minute_seconds;
            day_seconds = 24 * hour_seconds;
            week_seconds = 7 * day_seconds;
            #if( last_version_file_age > ( 1 * week_seconds )):
            #    log("***");
            #    log("*** This release of the refbot is more than one week old.  Please run updater.py and then try starting refbot.py again.");
            #    log("***");
            #    my_exit( 1 );
            if( last_version_file_age > ( 6 * hour_seconds )):
                log("***");
                log("*** This release of the refbot (under testing) is more than six hours old.  Please run updater.py and then start refbot.py again.");
                log("***");
                my_exit( 1 );

        # check that we've got a bogon IPs file
        if( not os.path.exists( FreenetNodeRefBot.bot_install_directory + FreenetNodeRefBot.bogon_filename )):
            log("***");
            log("*** The bogon IPs file \"%s\" is missing.  Please run updater.py and try again." % ( FreenetNodeRefBot.bot_install_directory + FreenetNodeRefBot.bogon_filename ));
            log("***");
            my_exit( 1 );
            
        # check that we've got an up-to-date fcp/node.py
        if( self.minimumFCPNodeRevision > int( fcp.FCPNode.svnRevision )):
            log("***");
            log("*** This version of the refbot requires at least revision %s of fcp/node.py.  Please run updater.py and try again." % ( self.minimumFCPNodeRevision ));
            log("***");
            my_exit( 1 );
            
        # check that we've got an up-to-date minibot.py
        if( self.minimumMiniBotRevision > int( MiniBot.svnRevision )):
            log("***");
            log("*** This version of the refbot requires at least revision %s of minibot.py.  Please run updater.py and try again." % ( self.minimumMiniBotRevision ));
            log("***");
            my_exit( 1 );
        
        # determine a config file path
        if not cfgFile:
            cfgFile = os.path.join(os.path.expanduser("~"), ".freenet_ref_bot")
        confpath = self.confpath = cfgFile
    
        # load, or create, a config
        if os.path.isfile(confpath):
            try:
                opts = self.load()
            except Exception, msg:
                log("***");
                log("*** ERROR loading configuration file:  %s" % ( msg ));
                log("*** ERROR: Failed to load configuration file.  Perhaps it is corrupted?");
                log("***");
                my_exit( 1 );
            needToSave = False
            if( len( opts['usernick'] ) > 12 ):
              print "The node's name used by the bot cannot be any longer than 12 characters because the bot's IRC nickname cannot be any longer than 16 characters and the bot IRC nickname will be this value with '_bot' added to the end.  Try again."
              self.setup_usernick( opts )
              needToSave = True
            elif( opts['usernick'][ -4: ].lower() == "_bot" ):
              print "The node's name used by the bot should not end in \"_bot\" because the bot IRC nickname will use the this node's name with '_bot' added to the end.  Try again."
              self.setup_usernick( opts )
              needToSave = True
            elif( ' ' in opts['usernick'] ):
              print "The node's name used by the bot should not contain spaces because the bot IRC nickname cannot contain spaces.  Try again."
              self.setup_usernick( opts )
              needToSave = True
            elif( '.' in opts['usernick'] ):
              print "The node's name used by the bot should not contain periods because the bot IRC nickname cannot contain periods.  Try again."
              self.setup_usernick( opts )
              needToSave = True
        else:
            opts = self.setup()
            needToSave = True

        if(not opts.has_key('config_version')):
            opts['config_version'] = 0
            needToSave = True
        try:
            self.config_version = int( opts['config_version'] )
        except:
            self.config_version = 0
            needToSave = True

        self.max_cpeers = 30
        self.max_tpeers = 50
        self.cpeers = None
        self.tpeers = None
    
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
        self.botircnick = self.nodenick + "_bot"
        self.refs = opts['refs']
        if(self.config_version < 1 and (not opts.has_key('bot2bot') or (opts.has_key('bot2bot') and opts['bot2bot'] == 'y'))):
            self.setup_bot2bot( opts )
        if(opts.has_key('bot2bot')):
            if( opts['bot2bot'] == 'y' ):
                self.bot2bot_configured = True
            else:
                self.bot2bot_configured = False
        else:
            self.bot2bot_configured = True
            needToSave = True
        # Not implemented yet - **FIXME**
        # **FIXME** Needs config_version check and old config_version upgrading
        #if(opts.has_key('bot2bot_announces')):
        #    if( opts['bot2bot_announce'] == 'y' ):
        #        self.bot2bot_announces_configured = True
        #    else:
        #        self.bot2bot_announces_configured = False
        #else:
        #    self.bot2bot_announces_configured = False
        #    needToSave = True
        if(self.config_version < 1 and (not opts.has_key('bot2bot_trades') or (opts.has_key('bot2bot_trades') and opts['bot2bot_trades'] == 'n'))):
            self.setup_bot2bot_trades( opts )
        if(opts.has_key('bot2bot_trades')):
            if( opts['bot2bot_trades'] == 'y' ):
                self.bot2bot_trades_configured = True
            else:
                self.bot2bot_trades_configured = False
        else:
            self.bot2bot_trades_configured = True
            needToSave = True
        if(self.config_version < 2 and (not opts.has_key('bot2bot_trades_only') or (opts.has_key('bot2bot_trades_only') and opts['bot2bot_trades_only'] == 'n'))):
            self.setup_bot2bot_trades_only( opts )
        if(opts.has_key('bot2bot_trades_only')):
            if( opts['bot2bot_trades_only'] == 'y' ):
                self.bot2bot_trades_only_configured = True
            else:
                self.bot2bot_trades_only_configured = False
        else:
            self.bot2bot_trades_only_configured = False
            needToSave = True
        if(not self.bot2bot_configured and self.bot2bot_trades_only_configured):
            log("***");
            log("*** bot2bot communication is disabled, but trading with other bots only is enabled.  This does not make sense.  Quitting.");
            log("***");
            my_exit( 1 );
        if(not self.bot2bot_trades_configured and self.bot2bot_trades_only_configured):
            log("***");
            log("*** bot2bot ref trading is disabled, but trading with other bots only is enabled.  This does not make sense.  Quitting.");
            log("***");
            my_exit( 1 );
        if(self.config_version < 3 and (not opts.has_key('privmsg_only') or (opts.has_key('privmsg_only') and opts['privmsg_only'] == 'y'))):
            self.setup_privmsg_only( opts )
        self.refurl = opts['refurl']
        if(self.config_version < 5 and not opts.has_key('darknet_trades')):
            self.setup_darknet_trades( opts )
            needToSave = True
        if(opts.has_key('darknet_trades')):
            if( opts['darknet_trades'] == 'y' ):
                self.darknet_trades_configured = True
            else:
                self.darknet_trades_configured = False
        else:
            opts['darknet_trades'] = 'y';
            self.darknet_trades_configured = True
            needToSave = True
        if(self.config_version < 5 and not opts.has_key('opennet_trades')):
            self.setup_opennet_trades( opts )
            needToSave = True
        if(opts.has_key('opennet_trades')):
            if( opts['opennet_trades'] == 'y' ):
                self.opennet_trades_configured = True
            else:
                self.opennet_trades_configured = False
        else:
            opts['opennet_trades'] = 'y';
            self.opennet_trades_configured = True
            needToSave = True
        if(self.config_version < 4 and not opts.has_key('opennet_refurl')):
            self.setup_opennet_refurl( opts )
            needToSave = True
        self.opennet_refurl = opts['opennet_refurl']
        if('' == self.refurl and not self.bot2bot_trades_only_configured and self.darknet_trades_configured):
            log("***");
            log("*** configured to trade with humans using a darknet noderef url, but we don't know a darknet noderef url.  This does not make sense.  Quitting.");
            log("***");
            my_exit( 1 );
        if('' == self.opennet_refurl and not self.bot2bot_trades_only_configured and not self.darknet_trades_configured):
            log("***");
            log("*** configured to trade with humans using a opennet noderef url, but we don't know a opennet noderef url.  This does not make sense.  Quitting.");
            log("***");
            my_exit( 1 );
        while(not self.darknet_trades_configured and not self.opennet_trades_configured):
            log("***");
            log("*** configured to trade neither darknet refs nor opennet refs.  The bot is useless without trading at least one of the two.");
            log("***");
            self.setup_darknet_trades( opts )
            if( opts['darknet_trades'] == 'y' ):
                self.darknet_trades_configured = True
            else:
                self.darknet_trades_configured = False
            self.setup_opennet_trades( opts )
            if( opts['opennet_trades'] == 'y' ):
                self.opennet_trades_configured = True
            else:
                self.opennet_trades_configured = False
            self.setup_refurl( opts )
            self.refurl = opts['refurl']
            self.setup_opennet_refurl( opts )
            self.opennet_refurl = opts['opennet_refurl']
        if(opts.has_key('privmsg_only')):
            if( opts['privmsg_only'] == 'y' ):
                self.privmsg_only_configured = True
            else:
                self.privmsg_only_configured = False
        else:
            self.privmsg_only_configured = True
            needToSave = True
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
            try:
                self.greet_interval = int( opts['greetinterval'] )
            except:
                print "Seems you've a bogus value for greetinterval in your config file.  Bailing."
                my_exit( 1 );
        else:
            self.greet_interval = 1800
            needToSave = True
        if(opts.has_key('spaminterval')):
            try:
                self.spam_interval = int( opts['spaminterval'] )
            except:
                print "Seems you've a bogus value for spaminterval in your config file.  Bailing."
                my_exit( 1 );
        else:
            self.spam_interval = 7200
            needToSave = True
        if(opts.has_key('refsperrun')):
            try:
                self.number_of_refs_to_collect_configured = int( opts['refsperrun'] )
            except:
                print "Seems you've a bogus value for refsperrun in your config file.  Bailing."
                my_exit( 1 );
        else:
            self.number_of_refs_to_collect_configured = 10
            needToSave = True
        self.number_of_refs_to_collect = self.number_of_refs_to_collect_configured
        if(self.number_of_refs_to_collect <= 0):
            print "refsperrun is at or below zero.  Nothing to do.  Quitting."
            my_exit( 1 );
        if(self.number_of_refs_to_collect > 20):
            self.number_of_refs_to_collect = 20
            needToSave = True
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
        if(opts.has_key('fcploglevel')):
            try:
                self.fcp_log_level = int( opts['fcploglevel'] )
            except:
                print "Seems you've a bogus value for fcploglevel in your config file.  Bailing."
                my_exit( 1 );
            if( 0 > self.fcp_log_level or 7 < self.fcp_log_level ):
                print "Seems you've a bogus value for fcploglevel in your config file.  The value should be between 0 and 7 inclusive to match the logger verbosity levels defined in fcp/node.py.  Bailing."
                my_exit( 1 );
        else:
            self.fcp_log_level = 3
            needToSave = True
        if(opts.has_key('fcploglevel_peerupdate')):
            try:
                self.peer_update_fcp_log_level = int( opts['fcploglevel_peerupdate'] )
            except:
                print "Seems you've a bogus value for fcploglevel_peerupdate in your config file.  Bailing."
                my_exit( 1 );
            if( 0 > self.peer_update_fcp_log_level or 7 < self.peer_update_fcp_log_level ):
                print "Seems you've a bogus value for fcploglevel_peerupdate in your config file.  The value should be between 0 and 7 inclusive to match the logger verbosity levels defined in fcp/node.py.  Bailing."
                my_exit( 1 );
        else:
            self.peer_update_fcp_log_level = 3
            needToSave = True
        if(opts.has_key('logfilepath')):
            self.log_file_path = opts['logfilepath']
            if( "None" == self.log_file_path ):
                self.log_file_path = None
        else:
            self.log_file_path = None
            needToSave = True
        kw['logfilepath'] = self.log_file_path
        
        # for internal use shadow of MiniBot configs
        self.irc_host = kw[ 'host' ]
        self.irc_port = kw[ 'port' ]
        
        self.bot2bot_enabled = self.bot2bot_configured;
        #self.bot2bot_announces_enabled = self.bot2bot_announces_configured;  # **FIXME** hardcoded ATM
        self.bot2bot_announces_enabled = True;                                # **FIXME** hardcoded ATM
        self.bot2bot_trades_enabled = self.bot2bot_trades_configured;
        self.bot2bot_trades_only_enabled = self.bot2bot_trades_only_configured;
        self.darknet_trades_enabled = self.darknet_trades_configured;
        self.opennet_trades_enabled = self.opennet_trades_configured;
        self.bot2bot_darknet_trades_enabled = self.darknet_trades_enabled;
        self.bot2bot_opennet_trades_enabled = self.opennet_trades_enabled;
        self.privmsg_only_enabled = self.privmsg_only_configured;
        if( not self.bot2bot_enabled ):
            self.bot2bot_announces_enabled = False;
            self.bot2bot_trades_enabled = False;
        if( not self.bot2bot_trades_enabled ):
            self.bot2bot_darknet_trades_enabled = False;
            self.bot2bot_opennet_trades_enabled = False;
            self.bot2bot_trades_only_enabled = False;
        if( self.bot2bot_trades_only_enabled ):
            self.bot2bot_announces_enabled = False;
          
        if( self.bot2bot_announces_enabled ):
            self.botAnnouncePool.append( self.botircnick );
            self.seenChannelUsers.append( self.botircnick );
    
        # finally construct the parent
        MiniBot.__init__(self, **kw)
    
        if( self.config_version < current_config_version ):
            self.config_version = current_config_version
            needToSave = True
        if needToSave:
            self.save()

        self.nodeDarknetIdentity = None;
        self.nodeDarknetRef = {};
        log("Verifying connectivity with node....  (If this hangs, there are problems talking to the node's FCP service)")
        f = None;
        try:
          f = fcp.FCPNode( host = self.fcp_host, port = self.fcp_port, logfunc = log, verbosity = self.fcp_log_level )
        except Exception, msg:
          try:
            f.shutdown()
          except UnboundLocalError, msg:
            pass
          log("***");
          log("*** ERROR: Failed to connect to node via FCP (%s:%d).  Check your fcp host and port settings on both the node and the bot config." % ( self.fcp_host, self.fcp_port ));
          log("***");
          my_exit( 1 )
        log("Successfully connected to the node's FCP service....")
        log("Verifying node build version....")
        if( f.nodeBuild < self.minimumNodeBuild ):
          f.shutdown()
          log("***");
          log("*** ERROR: This version of the refbot requires your node be running build %d or higher.  Please upgrade your Freenet node and try again." % ( self.minimumNodeBuild ))
          log("***");
          my_exit( 1 )
        log("Getting node's darknet ref....")
        try:
          node_darknet_ref = f.refstats();
          if( type( node_darknet_ref ) == type( [] )):
            node_darknet_ref = node_darknet_ref[ 0 ];
          self.nodeDarknetIdentity = node_darknet_ref[ "identity" ];
        except Exception, msg:
          f.shutdown()
          log("***");
          log("*** ERROR: Failed to get the node's darknet identity via FCP.  This is an odd error this refbot developer is not sure of a reason for.");
          log("***");
          my_exit( 1 )
        del node_darknet_ref[ "header" ];
        self.nodeDarknetRef = node_darknet_ref;
        self.hasOpennet = False;
        self.nodeOpennetIdentity = None;
        self.nodeOpennetRef = {};
        log("Checking if node has opennet enabled....")
        try:
          nodeconfig = f.getconfig( WithCurrent = True );
          if( type( nodeconfig ) == type( [] )):
            nodeconfig = nodeconfig[ 0 ];
          if( nodeconfig.has_key( "current.node.opennet.enabled" ) and "true" == nodeconfig[ "current.node.opennet.enabled" ].lower() ):
            self.hasOpennet = True;
        except Exception, msg:
          f.shutdown()
          log("***");
          log("*** ERROR: Failed to get the node's opennet enabled status via FCP.  This is an odd error this refbot developer is not sure of a reason for.");
          log("***");
          my_exit( 1 )
        if( not self.hasOpennet and self.opennet_trades_enabled ):
            log("***");
            log("*** configured to trade opennet refs, but opennet is not enabled on the node.  Quitting.");
            log("***");
            my_exit( 1 );
        if( self.hasOpennet ):
          log("Getting node's opennet ref....")
          try:
            node_opennet_ref = f.refstats( GiveOpennetRef = True );
            if( type( node_opennet_ref ) == type( [] )):
              node_opennet_ref = node_opennet_ref[ 0 ];
            self.nodeOpennetIdentity = node_opennet_ref[ "identity" ];
          except Exception, msg:
            f.shutdown()
            log("***");
            log("*** ERROR: Failed to get the node's opennet identity via FCP even though opennet is enabled.  This is an odd error this refbot developer is not sure of a reason for.");
            log("***");
            my_exit( 1 )
          del node_opennet_ref[ "header" ];
          self.nodeOpennetRef = node_opennet_ref;

        if( 0 >= len( FreenetNodeRefBot.bogons.keys())):
            readBogonFile( FreenetNodeRefBot.bot_install_directory + FreenetNodeRefBot.bogon_filename, self.addBogonCIDRNet );
            #log("DEBUG: bogons: %s" % ( FreenetNodeRefBot.bogons ));

        # Testing advertised darknet ref URL
        needToSave = False;
        #log("DEBUG: self.darknet_trades_enabled: %s" % ( self.darknet_trades_enabled ));
        while( 'y' != opts['bot2bot_trades_only'] and self.darknet_trades_enabled ):
            ( url_scheme, url_netloc, url_path, url_parms, url_query, url_fragid ) = urlparse.urlparse( opts['refurl'] );
            url_host = url_netloc;
            if( -1 != url_host.find( ":" )):
              url_host_fields = url_host.split( ":" );
              url_host = url_host_fields[ 0 ];
            url_ip = socket.gethostbyname( url_host );
            #log("DEBUG: url_ip: %s" % ( url_ip ));
            if( self.findBogonCIDRNet( url_ip )):
                log("***");
                log("*** ERROR: The bot advertised darknet ref URL points to an RFC1918 private IP address or an unassigned bogon IP address and cannot be used on the Internet.");
                log("***");
                self.setup_refurl( opts );
                needToSave = True;
                continue;
            log("Getting the bot advertised darknet ref from URL...");
            try:
                openurl = urllib2.urlopen(opts['refurl'])
                refbuf = openurl.read(20*1024)  # read up to 20 KiB
                openurl.close()
                refmemfile = StringIO.StringIO(refbuf)
                reflines = refmemfile.readlines()
                refmemfile.close();
            except Exception, msg:
                log("***");
                log("*** ERROR: Failed to get the bot advertised darknet ref from URL.");
                log("***");
                self.setup_refurl( opts );
                needToSave = True;
                continue;
            log("Checking syntax of advertised darknet ref...");
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
            ref_has_syntax_problem = False;
            if(not end_found):
                log("***");
                log("*** ERROR: Advertised ref does not contain an \"End\" line.");
                log("***");
                ref_has_syntax_problem = True;
            if( ref_fieldset.has_key( "testnet" ) and "true" == ref_fieldset[ "testnet" ].lower() ):
                log("***");
                log("*** ERROR: The bot advertised darknet ref is really an testnet ref.  The bot does not currently support testnet ref trading.");
                log("***");
                self.setup_refurl( opts );
                needToSave = True;
                continue;
            if( ref_fieldset.has_key( "opennet" ) and "true" == ref_fieldset[ "opennet" ].lower() ):
                log("***");
                log("*** ERROR: The bot advertised darknet ref is really an opennet ref; perhaps you've got your ref URLs mixed up?");
                log("***");
                self.setup_refurl( opts );
                needToSave = True;
                continue;
            required_ref_fields = [ "dsaGroup.g", "dsaGroup.p", "dsaGroup.q", "dsaPubKey.y", "identity", "location", "myName", "sig" ];
            for require_ref_field in required_ref_fields:
                if(not ref_fieldset.has_key(require_ref_field)):
                    log("***");
                    log("*** ERROR: No %s field in ref" % ( require_ref_field ));
                    log("***");
                    ref_has_syntax_problem = True;
            if(ref_has_syntax_problem):
                self.setup_refurl( opts );
                needToSave = True;
                continue;
            if( ref_fieldset[ "identity" ] != self.nodeDarknetIdentity ):
                log("***");
                log("*** ERROR: The bot advertised darknet ref's identity does not match the node's darknet identity; perhaps your FCP host/port setting is wrong?");
                log("***");
                self.setup_refurl( opts );
                needToSave = True;
                continue;
            if( ref_fieldset[ "identity" ] == self.nodeOpennetIdentity ):
                log("***");
                log("*** ERROR: The bot advertised darknet ref's identity matches the node's opennet identity; perhaps you've got your ref URLs mixed up?");
                log("***");
                self.setup_refurl( opts );
                needToSave = True;
                continue;
            log("Test adding advertised darknet ref...");
            try:
                addpeer_result = f.addpeer( kwdict = ref_fieldset )
            except fcp.node.FCPException, msg:
                if( 21 == msg.info[ 'Code' ] ):
                    log("***");
                    log("*** ERROR: The node had trouble parsing the bot advertised darknet ref");
                    log("***");
                    self.setup_refurl( opts );
                    needToSave = True;
                    continue;
                elif( 27 == msg.info[ 'Code' ] ):
                    log("***");
                    log("*** ERROR: The node could not verify the signature of the bot advertised darknet ref");
                    log("***");
                    self.setup_refurl( opts );
                    needToSave = True;
                    continue;
                elif( 28 == msg.info[ 'Code' ] ):
                    log("The bot advertised darknet ref appears to be good");
                    break;
                elif( 29 == msg.info[ 'Code' ] ):
                    log("***");
                    log("*** ERROR: The node has a peer with the bot advertised darknet ref; perhaps your FCP host/port setting is wrong?");
                    log("***");
                    f.shutdown()
                    my_exit( 1 )
                log("***");
                log("*** ERROR: The node had trouble test-adding the bot advertised darknet ref and gave us an unexpected error; perhaps you need to run updater.py");
                log("***");
                f.shutdown()
                my_exit( 1 )
            except Exception, msg:
                log("***");
                log("*** ERROR: caught generic exception test-adding darknet ref as peer: %s" % ( msg ));
                log("***");
                f.shutdown()
                my_exit( 1 )
            try:
                f.removepeer(ref_fieldset[ "identity" ] );
            except Exception, msg:
                pass;
            break;

        # Testing advertised opennet ref URL
        #log("DEBUG: self.opennet_trades_enabled: %s" % ( self.opennet_trades_enabled ));
        while( 'y' != opts['bot2bot_trades_only'] and self.opennet_trades_enabled ):
            ( url_scheme, url_netloc, url_path, url_parms, url_query, url_fragid ) = urlparse.urlparse( opts['opennet_refurl'] );
            url_host = url_netloc;
            if( -1 != url_host.find( ":" )):
              url_host_fields = url_host.split( ":" );
              url_host = url_host_fields[ 0 ];
            url_ip = socket.gethostbyname( url_host );
            #log("DEBUG: url_ip: %s" % ( url_ip ));
            if( self.findBogonCIDRNet( url_ip )):
                log("***");
                log("*** ERROR: The bot advertised opennet ref URL points to an RFC1918 private IP address or an unassigned bogon IP address and cannot be used on the Internet.");
                log("***");
                self.setup_opennet_refurl( opts );
                needToSave = True;
                continue;
            log("Getting the bot advertised opennet ref from URL...");
            try:
                openurl = urllib2.urlopen(opts['opennet_refurl'])
                refbuf = openurl.read(20*1024)  # read up to 20 KiB
                openurl.close()
                refmemfile = StringIO.StringIO(refbuf)
                reflines = refmemfile.readlines()
                refmemfile.close();
            except Exception, msg:
                log("***");
                log("*** ERROR: Failed to get the bot advertised opennet ref from URL.");
                log("***");
                self.setup_opennet_refurl( opts );
                needToSave = True;
                continue;
            log("Checking syntax of advertised opennet ref...");
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
            ref_has_syntax_problem = False;
            if(not end_found):
                log("***");
                log("*** ERROR: Advertised ref does not contain an \"End\" line.");
                log("***");
                ref_has_syntax_problem = True;
            if( ref_fieldset.has_key( "testnet" ) and "true" == ref_fieldset[ "testnet" ].lower() ):
                log("***");
                log("*** ERROR: The bot advertised opennet ref is really an testnet ref.  The bot does not currently support testnet ref trading.");
                log("***");
                self.setup_opennet_refurl( opts );
                needToSave = True;
                continue;
            if( not ref_fieldset.has_key( "opennet" ) or ( ref_fieldset.has_key( "opennet" ) and "false" == ref_fieldset[ "opennet" ].lower() )):
                log("***");
                log("*** ERROR: The bot advertised opennet ref is really a darknet ref; perhaps you've got your ref URLs mixed up?");
                log("***");
                self.setup_opennet_refurl( opts );
                needToSave = True;
                continue;
            required_ref_fields = [ "dsaGroup.g", "dsaGroup.p", "dsaGroup.q", "dsaPubKey.y", "identity", "location", "opennet", "sig" ];
            for require_ref_field in required_ref_fields:
                if(not ref_fieldset.has_key(require_ref_field)):
                    log("***");
                    log("*** ERROR: No %s field in ref" % ( require_ref_field ));
                    log("***");
                    ref_has_syntax_problem = True;
            if(ref_has_syntax_problem):
                self.setup_opennet_refurl( opts );
                needToSave = True;
                continue;
            if( ref_fieldset[ "identity" ] != self.nodeOpennetIdentity ):
                log("***");
                log("*** ERROR: The bot advertised opennet ref's identity does not match the node's opennet identity; perhaps your FCP host/port setting is wrong?");
                log("***");
                self.setup_opennet_refurl( opts );
                needToSave = True;
                continue;
            if( ref_fieldset[ "identity" ] == self.nodeDarknetIdentity ):
                log("***");
                log("*** ERROR: The bot advertised opennet ref's identity matches the node's darknet identity; perhaps you've got your ref URLs mixed up?");
                log("***");
                self.setup_opennet_refurl( opts );
                needToSave = True;
                continue;
            log("Test adding advertised opennet ref...");
            try:
                addpeer_result = f.addpeer( kwdict = ref_fieldset )
            except fcp.node.FCPException, msg:
                if( 21 == msg.info[ 'Code' ] ):
                    log("***");
                    log("*** ERROR: The node had trouble parsing the bot advertised opennet ref");
                    log("***");
                    self.setup_opennet_refurl( opts );
                    needToSave = True;
                    continue;
                elif( 27 == msg.info[ 'Code' ] ):
                    log("***");
                    log("*** ERROR: The node could not verify the signature of the bot advertised opennet ref");
                    log("***");
                    self.setup_opennet_refurl( opts );
                    needToSave = True;
                    continue;
                elif( 28 == msg.info[ 'Code' ] ):
                    log("The bot advertised opennet ref appears to be good");
                    break;
                elif( 29 == msg.info[ 'Code' ] ):
                    log("***");
                    log("*** ERROR: The node has a peer with the bot advertised opennet ref; perhaps your FCP host/port setting is wrong?");
                    log("***");
                    f.shutdown()
                    my_exit( 1 )
                log("***");
                log("*** ERROR: The node had trouble test-adding the bot advertised opennet ref and gave us an unexpected error; perhaps you need to run updater.py");
                log("***");
                f.shutdown()
                my_exit( 1 )
            except Exception, msg:
                log("***");
                log("*** ERROR: caught generic exception test-adding opennet ref as peer: %s" % ( msg ));
                log("***");
                f.shutdown()
                my_exit( 1 )
            try:
                f.removepeer(ref_fieldset[ "identity" ] );
            except Exception, msg:
                pass;
            break;

        f.shutdown()

        if needToSave:
            self.refurl = opts['refurl']
            self.opennet_refurl = opts['opennet_refurl']
            self.save()

        self.nrefs = 0
        
        log("Getting Peer Update...")
        temp_cpeers = None;
        temp_dpeers = None;
        peerUpdateCallResult = getPeerUpdateHelper( self.fcp_host, self.fcp_port, self.peer_update_fcp_log_level )
        if( peerUpdateCallResult.has_key( "cpeers" )):
            temp_cpeers = peerUpdateCallResult[ "cpeers" ];
        if( peerUpdateCallResult.has_key( "tpeers" )):
            temp_tpeers = peerUpdateCallResult[ "tpeers" ];
        if( temp_cpeers != None and temp_tpeers != None ):
            while(self.number_of_refs_to_collect > 0 and (self.number_of_refs_to_collect - self.nrefs) > 0 and ((temp_cpeers + (self.number_of_refs_to_collect - self.nrefs)) > self.max_cpeers)):
                self.number_of_refs_to_collect -= 1;
            while(self.number_of_refs_to_collect > 0 and (self.number_of_refs_to_collect - self.nrefs) > 0 and ((temp_tpeers + (self.number_of_refs_to_collect - self.nrefs)) > self.max_tpeers)):
                self.number_of_refs_to_collect -= 1;
            if(self.number_of_refs_to_collect <= 0):
                log("***");
                log("*** Don't need any more refs, now terminating!")
                log("***");
                my_exit( 1 )
            self.cpeers = temp_cpeers
            self.tpeers = temp_tpeers
    
        self.timeLastChanGreeting = time.time()
        self.haveSentDownloadLink = False
    
        self.lastSendTime = time.time()
        self.multilineSendLock = threading.Lock()
        self.nextMultilineSendWhenTime = 0;
    
        self.adderThreads = []
        self.directOrDieLock = threading.Lock()
        self.nodeCommsProblemCount = 0;
        self.identityCheckerThreads = []
        self.peerUpdaterThreads = []
        self.peer_update_interval = 60
        self.announcerTokenHolder = None
        self.api_options = []
        if(self.bot2bot_enabled):
            self.api_options.append( "bot2bot" );
            if(self.bot2bot_announces_enabled):
                self.api_options.append( "bot2bot_announces" );
            if(self.bot2bot_darknet_trades_enabled):
                self.api_options.append( "bot2bot_darknet_trades" );
            if(self.bot2bot_opennet_trades_enabled):
                self.api_options.append( "bot2bot_opennet_trades" );
            if(self.bot2bot_trades_only_enabled):
                self.api_options.append( "bot2bot_trades_only" );
            if(self.privmsg_only_enabled):
                self.api_options.append( "privmsg_only" );
    
    #@-node:__init__
    #@+node:setup
    def setup(self):
        """
        """
    
        opts = {}
    
        opts['config_version'] = current_config_version
            
        print
        print "** You will need to be sure to register your IRC nick with freenode"
        print "** so that someone else can't /msg your bot and shut it down"
        print "** while you're away.  Use /msg nickserv register <password>"
        opts['ownerircnick'] = self.prompt("Enter your usual freenode.net IRC nick")
        opts['usernick'] = opts['ownerircnick']
        print
        self.setup_usernick( opts )
        print
        print "** You need to choose a new password, since this bot will"
        print "** register this password with freenode 'nickserv', and"
        print "** on subsequent runs, will identify with this password"
        opts['password'] = self.prompt("Enter a new password")
        opts['ircchannel'] = self.prompt("IRC channel to join", "#freenet-refs")
        opts['irchost'] = self.prompt("Hostname of IRC server", "irc.freenode.net")
    
        while 1:
            opts['ircport'] = self.prompt("IRC Server Port", "6667")
            try:
                opts['ircport'] = int(opts['ircport'])
                break
            except:
                print "Invalid port '%s'.  Try again." % opts['ircport']
    
        opts['tmci_host'] = self.prompt("Node TMCI (telnet) hostname", "127.0.0.1")
    
        while 1:
            opts['tmci_port'] = self.prompt("Node TMCI (telnet) port", "2323")
            try:
                opts['tmci_port'] = int(opts['tmci_port'])
                break
            except:
                print "Invalid port '%s'.  Try again." % opts['tmci_port']
    
        opts['fcp_host'] = self.prompt("Node FCP hostname", "127.0.0.1")
    
        while 1:
            opts['fcp_port'] = self.prompt("Node FCP port", "9481")
            try:
                opts['fcp_port'] = int(opts['fcp_port'])
                break
            except:
                print "Invalid port '%s'.  Try again." % opts['fcp_port']
    
        self.setup_bot2bot( opts )
        #self.setup_bot2bot_announce( opts )  **FIXME** Not implemented yet
        self.setup_bot2bot_trades( opts )
        self.setup_bot2bot_trades_only( opts )
        opts['refurl'] = '';
        opts['opennet_refurl'] = '';
        opts['opennet_trades'] = 'y';
        #self.setup_opennet_trades( opts )
        opts['darknet_trades'] = 'n';
        #self.setup_darknet_trades( opts )
        self.setup_opennet_refurl( opts )
        self.setup_refurl( opts )
        self.setup_privmsg_only( opts )

        opts['greetinterval'] = 1800
        opts['spaminterval'] = 7200
        opts['refsperrun'] = 10
        opts['refs'] = []
    
        return opts
    
    #@-node:setup
    #@+node:setup_bot2bot
    def setup_bot2bot(self, opts):
        """
        """
        while 1:
            opts['bot2bot'] = self.prompt("Enable bot-2-bot communication (required for bot-2-bot ref trading)", "y")
            opts['bot2bot'] = opts['bot2bot'].lower();
            if( opts['bot2bot'] in [ 'y', 'n' ] ):
                break;
            print "Invalid option '%s' - must be 'y' for yes or 'n' for no" % opts['bot2bot']
    
    #@-node:setup_bot2bot
    #@+node:setup_bot2bot_announces
    def setup_bot2bot_announces(self, opts):
        """
        """
        if( 'y' == opts['bot2bot'] ):
            while 1:
                opts['bot2bot_announces'] = self.prompt("Enable cooperative bot announcements (requires bot-2-bot communication to be enabled)", "n")
                opts['bot2bot_announces'] = opts['bot2bot_announces'].lower();
                if( opts['bot2bot_announces'] in [ 'y', 'n' ] ):
                    break;
                print "Invalid option '%s' - must be 'y' for yes or 'n' for no" % opts['bot2bot_announces']

    
    #@-node:setup_bot2bot_announces
    #@+node:setup_bot2bot_trades
    def setup_bot2bot_trades(self, opts):
        """
        """
        if( 'y' == opts['bot2bot'] ):
            while 1:
                opts['bot2bot_trades'] = self.prompt("Enable bot-2-bot ref trades (requires bot-2-bot communication to be enabled)", "y")
                opts['bot2bot_trades'] = opts['bot2bot_trades'].lower();
                if( opts['bot2bot_trades'] in [ 'y', 'n' ] ):
                    break;
                print "Invalid option '%s' - must be 'y' for yes or 'n' for no" % opts['bot2bot_trades']
        else:
            opts['bot2bot_trades'] = 'n';
    
    #@-node:setup_bot2bot_trades
    #@+node:setup_bot2bot_trades_only
    def setup_bot2bot_trades_only(self, opts):
        """
        """
        if( 'y' == opts['bot2bot_trades'] ):
            while 1:
                opts['bot2bot_trades_only'] = self.prompt("Trade refs via bot-2-bot ref trades only (Don't share a URL or fetch URLs)", "n")
                opts['bot2bot_trades_only'] = opts['bot2bot_trades_only'].lower();
                if( opts['bot2bot_trades_only'] in [ 'y', 'n' ] ):
                    break;
                print "Invalid option '%s' - must be 'y' for yes or 'n' for no" % opts['bot2bot_trades_only']
        else:
            opts['bot2bot_trades_only'] = 'n';
    
    #@-node:setup_bot2bot_trades_only
    #@+node:setup_darknet_trades
    def setup_darknet_trades(self, opts):
        """
        """
        while 1:
            opts['darknet_trades'] = self.prompt("Should we trade darknet refs?", "n")
            opts['darknet_trades'] = opts['darknet_trades'].lower();
            if( opts['darknet_trades'] in [ 'y', 'n' ] ):
                break;
            print "Invalid option '%s' - must be 'y' for yes or 'n' for no" % opts['darknet_trades']
    
    #@-node:setup_darknet_trades
    #@+node:setup_privmsg_only
    def setup_privmsg_only(self, opts):
        """
        """
        if( 'y' != opts['bot2bot_trades_only'] ):
            while 1:
                opts['privmsg_only'] = self.prompt("Should we only allow ref trades by private message?", "y")
                opts['privmsg_only'] = opts['privmsg_only'].lower();
                if( opts['privmsg_only'] in [ 'y', 'n' ] ):
                    break;
                print "Invalid option '%s' - must be 'y' for yes or 'n' for no" % opts['privmsg_only']
        else:
            opts['privmsg_only'] = 'y';
    
    #@-node:setup_privmsg_only
    #@+node:setup_opennet_refurl
    def setup_opennet_refurl(self, opts):
        """
        """
        if( 'y' != opts['bot2bot_trades_only'] and 'y' == opts['opennet_trades'] ):
            opts['opennet_refurl'] = self.prompt("URL of your node's opennet ref")
        else:
            opts['opennet_refurl'] = '';
    
    #@-node:setup_opennet_refurl
    #@+node:setup_opennet_trades
    def setup_opennet_trades(self, opts):
        """
        """
        while 1:
            opts['opennet_trades'] = self.prompt("Should we trade opennet refs?", "y")
            opts['opennet_trades'] = opts['opennet_trades'].lower();
            if( opts['opennet_trades'] in [ 'y', 'n' ] ):
                break;
            print "Invalid option '%s' - must be 'y' for yes or 'n' for no" % opts['opennet_trades']
    
    #@-node:setup_opennet_trades
    #@+node:setup_refurl
    def setup_refurl(self, opts):
        """
        """
        if( 'y' != opts['bot2bot_trades_only'] and 'y' == opts['darknet_trades'] ):
            opts['refurl'] = self.prompt("URL of your node's darknet ref")
        else:
            opts['refurl'] = '';
    
    #@-node:setup_refurl
    #@+node:setup_usernick
    def setup_usernick(self, opts):
        """
        """
        print "** Give a short 12 character or less version of your node's name; The bot will tack \"_bot\" onto the end of it to form it's IRC nick"
        while( 1 ):
            opts['usernick'] = self.prompt("Enter your node's name", opts['usernick'])
            if( len( opts['usernick'] ) > 12 ):
              print "The node's name used by the bot cannot be any longer than 12 characters because the bot's IRC nickname cannot be any longer than 16 characters and the bot IRC nickname will be this value with '_bot' added to the end.  Try again."
            elif( opts['usernick'][ -4: ].lower() == "_bot" ):
              print "The node's name used by the bot should not end in \"_bot\" because the bot IRC nickname will use the this node's name with '_bot' added to the end.  Try again."
            elif( ' ' in opts['usernick'] ):
              print "The node's name used by the bot should not contain spaces because the bot IRC nickname cannot contain spaces.  Try again."
            elif( '.' in opts['usernick'] ):
              print "The node's name used by the bot should not contain periods because the bot IRC nickname cannot contain periods.  Try again."
            else:
              break
    
    #@-node:setup_usernick
    #@+node:save
    def save(self):
    
        f = file(self.confpath, "w")
    
        fmt = "%s = %s\n"
        f.write(fmt % ("config_version", repr(self.config_version)))
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
        f.write(fmt % ("opennet_refurl", repr(self.opennet_refurl)))
        f.write(fmt % ("password", repr(self.password)))
        f.write(fmt % ("greetinterval", repr(self.greet_interval)))
        f.write(fmt % ("spaminterval", repr(self.spam_interval)))
        f.write(fmt % ("fcploglevel", repr(self.fcp_log_level)))
        f.write(fmt % ("fcploglevel_peerupdate", repr(self.peer_update_fcp_log_level)))
        f.write(fmt % ("logfilepath", repr(self.log_file_path)))
        f.write(fmt % ("refsperrun", repr(self.number_of_refs_to_collect_configured)))
        f.write(fmt % ("refs", repr(self.refs)))
        if(self.bot2bot_configured):
            f.write(fmt % ("bot2bot", repr('y')))
        else:
            f.write(fmt % ("bot2bot", repr('n')))
        # Not implemented yet - **FIXME**
        #if(self.bot2bot_announces_configured):
        #    f.write(fmt % ("bot2bot_announces", repr('y')))
        #else:
        #    f.write(fmt % ("bot2bot_announces", repr('n')))
        if(self.bot2bot_trades_configured):
            f.write(fmt % ("bot2bot_trades", repr('y')))
        else:
            f.write(fmt % ("bot2bot_trades", repr('n')))
        if(self.bot2bot_trades_only_configured):
            f.write(fmt % ("bot2bot_trades_only", repr('y')))
        else:
            f.write(fmt % ("bot2bot_trades_only", repr('n')))
        if(self.privmsg_only_configured):
            f.write(fmt % ("privmsg_only", repr('y')))
        else:
            f.write(fmt % ("privmsg_only", repr('n')))
        if(self.darknet_trades_configured):
            f.write(fmt % ("darknet_trades", repr('y')))
        else:
            f.write(fmt % ("darknet_trades", repr('n')))
        if(self.opennet_trades_configured):
            f.write(fmt % ("opennet_trades", repr('y')))
        else:
            f.write(fmt % ("opennet_trades", repr('n')))
    
        f.close()
    
        log("Saved configuration to %s" % self.confpath)
    
    #@-node:save
    #@+node:load
    def load(self):
    
        opts = {}
        exec file(self.confpath).read() in opts
        log("Read configuration from %s" % self.confpath)
        return opts
    
    #@-node:load
    #@+node:events
    # handle events
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
        if(self.bot2bot_enabled and -1 != msg.find("bot2bot") and "_bot" == sender[ -4: ]):
            if(not self.bots.has_key(sender)):
                bot_data = {}
                self.bots[ sender ] = bot_data
                log("** bots: %s" % ( self.bots.keys() ))
                self.after(random.randint(7, 20), self.sendBotHello, sender)  # Introduce ourselves after 7-20 seconds
            if( sender in self.usersInChan ):
                self.usersInChan.remove( sender )
    
    #@-node:on_chanmsg
    #@+node:on_ready
    def on_ready(self):
        """
        Invoked when bot is fully signed in, on channel and ready to play
        """
        if self._restarted:
            self.action(self.channel, "restarted because the server was ignoring it")
        else:
            self.getPeerUpdate()
            self.greetChannel()
        
        self.after(10, self.spamChannel)
        self.after(1, self.process_any_identities_checked)
        self.after(0.5, self.process_any_refs_added)
        self.after(1, self.process_peer_updates)
        if(self.bot2bot_announces_enabled):
            self.after(announcerTokenHolderPickDelay, self.maybe_set_announcerTokenHolder)
        
        for user in self.usersInChan:
            if( not user in self.seenChannelUsers ):
                self.seenChannelUsers.append( user );
    
        log("****** on_ready")
    
    #@-node:on_ready
    #@+node:post_on_join
    def post_on_join(self, sender, target):
        """
        When another user (or us) have joined (post processing by inheriting class)
        """
        # NOTE: We don't know if it's a bot at this point
        log("** DEBUG: post_on_join() called with sender: %s  target: %s" % ( sender, target ));
        log("** DEBUG: self.usersInChan: %d: %s" % ( len( self.usersInChan ), self.usersInChan ));
        if( not sender in self.seenChannelUsers ):
            maxSeenChannelUsersCount = getMaxSeenChannelUsers( len( self.usersInChan ));
            #log("** DEBUG: maxSeenChannelUsersCount: %s  len( self.seenChannelUsers ): %s" % ( maxSeenChannelUsersCount, len( self.seenChannelUsers )));
            while( maxSeenChannelUsersCount < len( self.seenChannelUsers )):
                oldUser = self.seenChannelUsers.pop( 0 );
                if( oldUser in self.usersInChan ):
                    self.seenChannelUsers.append( oldUser );
            #log("** DEBUG: maxSeenChannelUsersCount: %s  len( self.seenChannelUsers ): %s" % ( maxSeenChannelUsersCount, len( self.seenChannelUsers )));
            self.seenChannelUsers.append( sender );
            log("** DEBUG: self.seenChannelUsers: %d of %d: %s" % ( len( self.seenChannelUsers ), maxSeenChannelUsersCount, self.seenChannelUsers ));
            if( None != self.announcerTokenHolder ):
                #
                #
                # **FIXME** The following is temporary during cooperative bot announce infrastructure testing
                #
                if( self.announcerTokenHolder == self.botircnick and ( 4 > len( sender ) or "_bot" != sender[ -4: ].lower() )):
                    # **FIXME** This code will be replaced by the "selected announcer's" announcement private message to the joining user
                    log("** DEBUG: would welcome new, unseen-by-bot channel user here");
                    if( "Zothar" in self.usersInChan ):
                        self.privmsg(
                            "Zothar",
                            "Would welcome new, unseen-by-bot channel user here: %s  token holder: %s  botAnnouncePool: %s" % ( sender, self.announcerTokenHolder, self.botAnnouncePool[ :3 ] )
                            )
                    elif( "Zothar_Work" in self.usersInChan ):
                        self.privmsg(
                            "Zothar_Work",
                            "Would welcome new, unseen-by-bot channel user here: %s  token holder: %s  botAnnouncePool: %s" % ( sender, self.announcerTokenHolder, self.botAnnouncePool[ :3 ] )
                            )
                elif( "Zothar70d_bot" == self.botircnick and ( 4 > len( sender ) or "_bot" != sender[ -4: ].lower() )):
                    # **FIXME** This code will be removed once cooperative bot announce testing is complete
                    if( "Zothar" in self.usersInChan ):
                        self.privmsg(
                            "Zothar",
                            "%s should welcome new, unseen-by-bot channel user here: %s  botAnnouncePool: %s" % ( self.announcerTokenHolder, sender, self.botAnnouncePool[ :3 ] )
                            )
                    elif( "Zothar_Work" in self.usersInChan ):
                        self.privmsg(
                            "Zothar_Work",
                            "%s should welcome new, unseen-by-bot channel user here: %s  botAnnouncePool: %s" % ( self.announcerTokenHolder, sender, self.botAnnouncePool[ :3 ] )
                            )
        
    #@-node:post_on_join
    #@+node:post_on_kick
    def post_on_kick(self, sender, channel, target, msg):
        """
        When a user has been kicked from a channel (post processing by inheriting class)
        """
        log("** DEBUG: self.usersInChan: %d: %s" % ( len( self.usersInChan ), self.usersInChan ));
        if( target in self.botAnnouncePool ):
            self.botAnnouncePool.remove( target );
            if( self.bot2bot_announces_enabled and target == self.announcerTokenHolder ):
                if( self.botircnick != self.announcerTokenHolder ):
                    self.announcerTokenHolder = self.getAnnouncerTokenHolder()
                    log("** DEBUG: gonna send 'announcertokennotify' to %s" % ( self.announcerTokenHolder ))
                    self.sendAnnouncerTokenHolderNotify(self.announcerTokenHolder)
                else:
                    # **FIXME** Do nothing; For now, this is handled by everybody else noticing the kick
                    pass;
        if(self.bots.has_key( target )):
            del self.bots[ target ]
            log("** bots: %s" % ( self.bots.keys() ))
            log("** DEBUG: self.botAnnouncePool: %d: %s" % ( len( self.botAnnouncePool ), self.botAnnouncePool ));
    
    #@-node:post_on_kick
    #@+node:post_on_nick
    def post_on_nick(self, sender, target):
        """
        When another user (or us) have changed nicks (post processing by inheriting class)
        """
        log("** DEBUG: self.usersInChan: %d: %s" % ( len( self.usersInChan ), self.usersInChan ));
        if( sender in self.botAnnouncePool ):
            k = self.botAnnouncePool.index( sender );
            self.botAnnouncePool[ k ] = target;
            self.botAnnouncePool.sort();
            if( self.bot2bot_announces_enabled and sender == self.announcerTokenHolder ):
                if( self.botircnick != self.announcerTokenHolder ):
                    self.announcerTokenHolder = self.getAnnouncerTokenHolder()
                    log("** DEBUG: gonna send 'announcertokennotify' to %s" % ( self.announcerTokenHolder ))
                    self.sendAnnouncerTokenHolderNotify(self.announcerTokenHolder)
                else:
                    # **FIXME** Do nothing; For now, this is handled by everybody else noticing our nick change
                    pass;
        if(self.bots.has_key( sender )):
          bot_data = self.bots[ sender ]
          del self.bots[ sender ]
          self.bots[ target ] = bot_data
          log("** bots: %s" % ( self.bots.keys() ))
        if( not target in self.seenChannelUsers ):
            maxSeenChannelUsersCount = getMaxSeenChannelUsers( len( self.usersInChan ));
            #log("** DEBUG: maxSeenChannelUsersCount: %s  len( self.seenChannelUsers ): %s" % ( maxSeenChannelUsersCount, len( self.seenChannelUsers )));
            while( maxSeenChannelUsersCount < len( self.seenChannelUsers )):
                oldUser = self.seenChannelUsers.pop( 0 );
                if( oldUser in self.usersInChan ):
                    self.seenChannelUsers.append( oldUser );
            #log("** DEBUG: maxSeenChannelUsersCount: %s  len( self.seenChannelUsers ): %s" % ( maxSeenChannelUsersCount, len( self.seenChannelUsers )));
            self.seenChannelUsers.append( target );
            log("** DEBUG: self.seenChannelUsers: %d of %d: %s" % ( len( self.seenChannelUsers ), maxSeenChannelUsersCount, self.seenChannelUsers ));
            log("** DEBUG: self.botAnnouncePool: %d: %s" % ( len( self.botAnnouncePool ), self.botAnnouncePool ));
    
    #@-node:post_on_nick
    #@+node:post_on_part
    def post_on_part(self, sender, target, msg):
        """
        When another user (or us) have left a channel (post processing by inheriting class)
        """
        log("** DEBUG: self.usersInChan: %d: %s" % ( len( self.usersInChan ), self.usersInChan ));
        if( sender in self.botAnnouncePool ):
            self.botAnnouncePool.remove( sender );
            if( self.bot2bot_announces_enabled and sender == self.announcerTokenHolder ):
                if( self.botircnick != self.announcerTokenHolder ):
                    self.announcerTokenHolder = self.getAnnouncerTokenHolder()
                    log("** DEBUG: gonna send 'announcertokennotify' to %s" % ( self.announcerTokenHolder ))
                    self.sendAnnouncerTokenHolderNotify(self.announcerTokenHolder)
                else:
                    # **FIXME** Do nothing; this should be handled in our pre_part_and_quit()
                    pass;
        if(self.bots.has_key( sender )):
            del self.bots[ sender ]
            log("** bots: %s" % ( self.bots.keys() ))
            log("** DEBUG: self.botAnnouncePool: %d: %s" % ( len( self.botAnnouncePool ), self.botAnnouncePool ));
    
    #@-node:post_on_part
    #@+node:post_on_quit
    def post_on_quit(self, sender, msg):
        """
        When another user (or us) have quit a server (post processing by inheriting class)
        """
        log("** DEBUG: self.usersInChan: %d: %s" % ( len( self.usersInChan ), self.usersInChan ));
        if( sender in self.botAnnouncePool ):
            self.botAnnouncePool.remove( sender );
            if( self.bot2bot_announces_enabled and sender == self.announcerTokenHolder ):
                if( self.botircnick != self.announcerTokenHolder ):
                    self.announcerTokenHolder = self.getAnnouncerTokenHolder()
                    log("** DEBUG: gonna send 'announcertokennotify' to %s" % ( self.announcerTokenHolder ))
                    self.sendAnnouncerTokenHolderNotify(self.announcerTokenHolder)
                else:
                    # **FIXME** Do nothing; For now, this is handled by everybody else noticing our quitting
                    pass;
        if(self.bots.has_key( sender )):
            if( self.bots[ sender ].has_key( "identity" )):
                identity = self.bots[ sender ][ "identity" ]
                if( self.botDarknetIdentities.has_key( identity )):
                    del self.botDarknetIdentities[ identity ]
            if( self.bots[ sender ].has_key( "opennet_identity" )):
                identity = self.bots[ sender ][ "opennet_identity" ]
                if( self.botDarknetIdentities.has_key( identity )):
                    del self.botDarknetIdentities[ identity ]
            del self.bots[ sender ]
            log("** bots: %s" % ( self.bots.keys() ))
            log("** DEBUG: self.botAnnouncePool: %d: %s" % ( len( self.botAnnouncePool ), self.botAnnouncePool ));
    
    #@-node:post_on_quit
    #@-node:events
    #@+node:actions
    # action methods
    
    #@+others
    #@+node:addBotIdentity
    def addBotIdentity(self, botNick, botDarknetIdentity ):
    
        if( "None" == botDarknetIdentity ):
            return False;
        if( self.botDarknetIdentities.has_key( botDarknetIdentity )):
            return False;
        if( not self.bots.has_key( botNick )):
            return False;
        if( self.bots[ botNick ].has_key( "identity" )):
            return False;
        self.bots[ botNick ][ "identity" ] = botDarknetIdentity;
        self.botDarknetIdentities[ botDarknetIdentity ] = botNick;
        return True;
    
    #@-node:addBotIdentity
    #@+node:addBotOpennetIdentity
    def addBotOpennetIdentity(self, botNick, botOpennetIdentity ):
    
        if( "None" == botOpennetIdentity ):
            return False;
        if( self.botOpennetIdentities.has_key( botOpennetIdentity )):
            return False;
        if( not self.bots.has_key( botNick )):
            return False;
        if( self.bots[ botNick ].has_key( "opennet_identity" )):
            return False;
        self.bots[ botNick ][ "opennet_identity" ] = botOpennetIdentity;
        self.botOpennetIdentities[ botOpennetIdentity ] = botNick;
        return True;
    
    #@-node:addBotOpennetIdentity
    #@+node:addSeenChannelUsers
    def addSeenChannelUsers(self, botNick, botSeenChannelUsers ):

        if(self.bots.has_key( botNick )):
            try:
                seenChannelUsers = eval( botSeenChannelUsers )
            except:
                return
            for user in seenChannelUsers:
                if( not user in self.seenChannelUsers and not self.bots.has_key( user )):
                    self.seenChannelUsers.append( user );
            maxSeenChannelUsersCount = getMaxSeenChannelUsers( len( self.usersInChan ));
            #log("** DEBUG: maxSeenChannelUsersCount: %s  len( self.seenChannelUsers ): %s" % ( maxSeenChannelUsersCount, len( self.seenChannelUsers )));
            while( maxSeenChannelUsersCount < len( self.seenChannelUsers )):
                oldUser = self.seenChannelUsers.pop( 0 );
                if( oldUser in self.usersInChan ):
                    self.seenChannelUsers.append( oldUser );
            log("** DEBUG: maxSeenChannelUsersCount: %s  len( self.seenChannelUsers ): %s" % ( maxSeenChannelUsersCount, len( self.seenChannelUsers )));

    #@-node:addSeenChannelUsers
    #@+node:getPeerUpdate
    def getPeerUpdate(self):
    
        peerUpdaterThread = GetPeerUpdate(self.fcp_host, self.fcp_port, self.peer_update_fcp_log_level)
        self.peerUpdaterThreads.append(peerUpdaterThread)
        peerUpdaterThread.start()
        if(self.peer_update_interval > 0):
            self.after(self.peer_update_interval, self.getPeerUpdate)
    
    #@-node:getPeerUpdate
    #@+node:getRevisionsString
    def getRevisionsString(self):
        """
        Return a string of the relevant file revisions (should be overridden inheriting class)
        """
        return "refbot.py:%s|minibot.py:%s|fcp/node.py:%s" % ( FreenetNodeRefBot.svnRevision, MiniBot.svnRevision, fcp.FCPNode.svnRevision )
        
    #@-node:getRevisionsString
    #@+node:greetChannel
    def greetChannel(self):
    
        if(self.tpeers == None):
            self.after(0.25, self.greetChannel);
            return;
        if( self.number_of_refs_to_collect <= 0 ):
            return
        refs_to_go = self.number_of_refs_to_collect - self.nrefs
        refs_plural_str = ''
        if( refs_to_go > 1 ):
            refs_plural_str = "s"
        dark_open_str = "";
        if( self.darknet_trades_enabled and self.opennet_trades_enabled ):
            dark_open_str = "darknet and opennet";
        elif( self.darknet_trades_enabled ):
            dark_open_str = "darknet";
        else:
            dark_open_str = "opennet";
        if( self.bot2bot_trades_only_enabled ):
            self.privmsg(
                self.channel,
                "Hi, I'm %s's noderef swap bot.  I'm configured to only trade %s refs with other bots and will not trade directly with humans.  Send me the \"help\" command to learn how to run your own ref swapping bot.  (%d ref%s to go)" \
                % ( self.nodenick, dark_open_str, refs_to_go, refs_plural_str )
            )
        elif( self.privmsg_only_enabled ):
            if( self.bot2bot_trades_enabled ):
                self.privmsg(
                    self.channel,
                    "Hi, I'm %s's noderef swap bot.  I'm configured to trade %s refs with bots and with humans only via private message (requires registering with nickserv, i.e. /ns register <password>).  To swap a ref with me, /msg me with your ref url  (%d ref%s to go)" \
                    % ( self.nodenick, dark_open_str, refs_to_go, refs_plural_str )
                )
            else:
                self.privmsg(
                    self.channel,
                    "Hi, I'm %s's noderef swap bot.  I'm configured to only trade %s refs with humans via private message (requires registering with nickserv, i.e. /ns register <password>) and will not trade with bots.  To swap a ref with me, /msg me with your ref url  (%d ref%s to go)" \
                    % ( self.nodenick, dark_open_str, refs_to_go, refs_plural_str )
                )
        else:
            if( self.bot2bot_trades_enabled ):
                self.privmsg(
                    self.channel,
                    "Hi, I'm %s's noderef swap bot.  I'm configured to trade %s refs with humans or bots.  To swap a ref with me, /msg me or say %s: your_ref_url  (%d ref%s to go)" \
                    % ( self.nodenick, dark_open_str, self.nick, refs_to_go, refs_plural_str )
                )
            else:
                self.privmsg(
                    self.channel,
                    "Hi, I'm %s's noderef swap bot.  I'm configured to trade %s refs with humans, but not with bots.  To swap a ref with me, /msg me or say %s: your_ref_url  (%d ref%s to go)" \
                    % ( self.nodenick, dark_open_str, self.nick, refs_to_go, refs_plural_str )
                )
        if(self.greet_interval > 0 and not self.bot2bot_trades_only_enabled):
            self.after(self.greet_interval, self.greetChannel)
    
    #@-node:greetChannel
    #@+node:maybe_set_announcerTokenHolder
    def maybe_set_announcerTokenHolder(self):
        """
        Set announcerTokenHolder if it's not already set (called after some time after startup to give the bot time to integrate with other bots on the channel)
        """
        log("** DEBUG: maybe_set_announcerTokenHolder() called");
        log("** DEBUG: self.usersInChan: %d: %s" % ( len( self.usersInChan ), self.usersInChan ));
        if( self.bot2bot_announces_enabled ):
            log("** DEBUG: self.botAnnouncePool: %d: %s" % ( len( self.botAnnouncePool ), self.botAnnouncePool ));
            if( None == self.announcerTokenHolder ):
                log("** DEBUG: announcerTokenHolder %s -> %s" % ( self.announcerTokenHolder, self.getAnnouncerTokenHolder() ))
                self.announcerTokenHolder = self.getAnnouncerTokenHolder()
        
    #@-node:maybe_set_announcerTokenHolder
    #@+node:pre_part_and_quit
    def pre_part_and_quit(self, reason):
        """
        Called before doing anything in part_and_quit() (pre processing by inheriting class)
        """
        # **FIXME** should be updated once announcerTokenHolder is selected better
        if( self.bot2bot_announces_enabled and self.botircnick == self.announcerTokenHolder ):
            if( self.botircnick in self.botAnnouncePool ):
                self.botAnnouncePool.remove( self.botircnick );
            # **FIXME** Needs looking when selection scheme is better
            log("** DEBUG: announcerTokenHolder %s -> %s" % ( self.announcerTokenHolder, self.getAnnouncerTokenHolder() ))
            # **FIXME** There's a potential race condition with a "super-recent" join by a new announcer vs. another announce that's already integrated with the other announcers
            #         - Perhaps a new joiner can determine how well integrated it is and send an explicit "I'm ready"
            #         - announcerTokenHolder changes should probably be broadcast or chained to all announcers rather than only sent from the old "authoritative" announcer to the new one
            #         - other announcers should track how long each announcer has been known for the first 15 minutes or something?
            self.announcerTokenHolder = self.getAnnouncerTokenHolder()
            if( None != self.announcerTokenHolder ):
                log("** DEBUG: gonna send 'announcertokennotify' to %s" % ( self.announcerTokenHolder ))
                self.sendAnnouncerTokenHolderNotify(self.announcerTokenHolder)
        
    #@-node:pre_part_and_quit
    #@+node:sendAnnouncerTokenHolderNotify
    def sendAnnouncerTokenHolderNotify(self, target):
        """
        Send a notification of the current/new/calculated announce token holder to the target nick
        """
        log("** DEBUG: self.bot2bot_announces_enabled: %s" % ( self.bot2bot_announces_enabled ))
        log("** DEBUG: self.announcerTokenHolder: %s" % ( self.announcerTokenHolder ))
        if( self.bot2bot_announces_enabled and None != self.announcerTokenHolder ):
            log("** DEBUG: calling privmsg in sendAnnouncerTokenHolderNotify() now")
            self.privmsg( target, "announcertokennotify %s %s" % ( self.announcerTokenHolder, self.botAnnouncePool[ :10 ] ))
            if( "Zothar70d_bot" != target and "Zothar70d_bot" in self.usersInChan ):
                self.privmsg( "Zothar70d_bot", "announcertokennotify %s %s" % ( self.announcerTokenHolder, self.botAnnouncePool[ :10 ] ))
    
    #@-node:sendAnnouncerTokenHolderNotify
    #@+node:sendBotHello
    def sendBotHello(self, target):
        """
        Introduce ourselves to a just connected bot
        """
        self.privmsg( target, "bothello" )
    
    #@-node:sendBotHello
    #@+node:sendDoOpennetRefSwapAllow
    def sendDoOpennetRefSwapAllow(self, target):
        """
        Tell the bot with the target IRC nick that we agree to swap opennet refs with them as negotiated
        """
        self.privmsg( target, "doopennetrefswapallow" )
    
    #@-node:sendDoOpennetRefSwapAllow
    #@+node:sendDoOpennetRefSwapCompleted
    def sendDoOpennetRefSwapCompleted(self, target):
        """
        Tell the bot with the target IRC nick that we have completed the negotiated opennet ref swap with them
        """
        self.privmsg( target, "doopennetrefswapcompleted" )
    
    #@-node:sendDoOpennetRefSwapCompleted
    #@+node:sendDoOpennetRefSwapDeny
    def sendDoOpennetRefSwapDeny(self, target):
        """
        Tell the bot with the target IRC nick that we are denying their request to swap opennet refs with us as negotiated
        """
        self.privmsg( target, "doopennetrefswapdeny" )
    
    #@-node:sendDoOpennetRefSwapDeny
    #@+node:sendDoOpennetRefSwapFailed
    def sendDoOpennetRefSwapFailed(self, target):
        """
        Tell the bot with the target IRC nick that we have failed to complete the negotiated opennet ref swap with them
        """
        self.privmsg( target, "doopennetrefswapfailed" )
    
    #@-node:sendDoOpennetRefSwapFailed
    #@+node:sendDoOpennetRefSwapRequest
    def sendDoOpennetRefSwapRequest(self, target):
        """
        Ask the bot with the target IRC nick to swap opennet refs with us
        """
        self.privmsg( target, "doopennetrefswaprequest" )
    
    #@-node:sendDoOpennetRefSwapRequest
    #@+node:sendDoRefSwapAllow
    def sendDoRefSwapAllow(self, target):
        """
        Tell the bot with the target IRC nick that we agree to swap darknet refs with them as negotiated
        """
        self.privmsg( target, "dorefswapallow" )
    
    #@-node:sendDoRefSwapAllow
    #@+node:sendDoRefSwapCompleted
    def sendDoRefSwapCompleted(self, target):
        """
        Tell the bot with the target IRC nick that we have completed the negotiated darknet ref swap with them
        """
        self.privmsg( target, "dorefswapcompleted" )
    
    #@-node:sendDoRefSwapCompleted
    #@+node:sendDoRefSwapDeny
    def sendDoRefSwapDeny(self, target):
        """
        Tell the bot with the target IRC nick that we are denying their request to swap darknet refs with us as negotiated
        """
        self.privmsg( target, "dorefswapdeny" )
    
    #@-node:sendDoRefSwapDeny
    #@+node:sendDoRefSwapFailed
    def sendDoRefSwapFailed(self, target):
        """
        Tell the bot with the target IRC nick that we have failed to complete the negotiated darknet ref swap with them
        """
        self.privmsg( target, "dorefswapfailed" )
    
    #@-node:sendDoRefSwapFailed
    #@+node:sendDoRefSwapRequest
    def sendDoRefSwapRequest(self, target):
        """
        Ask the bot with the target IRC nick to swap darknet refs with us
        """
        self.privmsg( target, "dorefswaprequest" )
    
    #@-node:sendDoRefSwapRequest
    #@+node:sendGetIdentity
    def sendGetIdentity(self, target):
        """
        Ask for a bot's darknet identity and send them ours
        """
        if(self.bots.has_key( target ) and not self.bots[ target ].has_key( "identity" )):
            self.privmsg( target, "getidentity %s" % ( self.nodeDarknetIdentity ))
    
    #@-node:sendGetIdentity
    #@+node:sendGetOpennetIdentity
    def sendGetOpennetIdentity(self, target):
        """
        Ask for a bot's opennet identity and send them ours
        """
        if(self.bots.has_key( target ) and not self.bots[ target ].has_key( "opennet_identity" )):
            self.privmsg( target, "getopennetidentity %s" % ( self.nodeOpennetIdentity ))
    
    #@-node:sendGetOpennetIdentity
    #@+node:sendGetOpennetRefDirect
    def sendGetOpennetRefDirect(self, target):
        """
        Get their opennet ref directly
        """
        if(self.bots.has_key( target ) and not self.bots[ target ].has_key( "opennet_ref" )):
            self.privmsg( target, "getopennetrefdirect" )
    
    #@-node:sendGetOpennetRefDirect
    #@+node:sendGetOptions
    def sendGetOptions(self, target):
        """
        Ask for a bot's options and send them ours
        """
        if(self.bots.has_key( target ) and not self.bots[ target ].has_key( "options" )):
            self.privmsg( target, "getoptions %s" % ( self.api_options ))
    
    #@-node:sendGetOptions
    #@+node:sendGetRefDirect
    def sendGetRefDirect(self, target):
        """
        Get their darknet ref directly
        """
        if(self.bots.has_key( target ) and not self.bots[ target ].has_key( "ref" )):
            self.privmsg( target, "getrefdirect" )
    
    #@-node:sendGetRefDirect
    #@+node:sendMyIdentity
    def sendMyIdentity(self, target):
        """
        Give them our darknet identity
        """
        self.privmsg( target, "myidentity %s" % ( self.nodeDarknetIdentity ))
    
    #@-node:sendMyIdentity
    #@+node:sendMyOpennetIdentity
    def sendMyOpennetIdentity(self, target):
        """
        Give them our opennet identity
        """
        self.privmsg( target, "myopennetidentity %s" % ( self.nodeOpennetIdentity ))
    
    #@-node:sendMyIdentity
    #@+node:sendMyOptions
    def sendMyOptions(self, target):
        """
        Give them our options
        """
        self.privmsg( target, "myoptions %s" % ( self.api_options ))
    
    #@-node:sendMyOptions
    #@+node:sendSeenChannelUsers
    def sendSeenChannelUsers(self, target):
        """
        Give them our seenChannelUsers
        """
        #log( "** sendrefdirect(): multilineSendLock.acquire() before processing target: %s" % ( target ));
        self.multilineSendLock.acquire( 1 );  # Lock shared between all multiline senders
        # Spread out the chunks of users so we don't trigger the babbler detector of a receiving refbot
        nextWhen = 0;
        now = long( math.floor( time.time() ));
        if( self.nextMultilineSendWhenTime > now):  # self.nextMultilineSendWhenTime shared between all multiline senders
          nextWhen = self.nextMultilineSendWhenTime - now;
        else:
          self.nextMultilineSendWhenTime = now;
        beginningNextWhenTime = self.nextMultilineSendWhenTime;
        #log( "** DEBUG: before: nextWhen: %d  nextMultilineSendWhenTime: %d" % ( nextWhen, self.nextMultilineSendWhenTime ));
        seenChannelUsers = [];
        # Make a copy of the user list, excluding user nicks still currently in the channel
        for seenChannelUser in self.seenChannelUsers:
            if( not seenChannelUser in self.usersInChan ):
                seenChannelUsers.append( seenChannelUser );
        i = 0;
        chunkSize = 10;
        while( i < len( seenChannelUsers )):
            self.after( nextWhen, self.privmsg, target, "myseenchannelusers %s" % ( seenChannelUsers[ i : ( i + chunkSize ) ] ))
            i += chunkSize;
            delay = random.randint(7,14)  # 7-14 seconds between each line
            nextWhen += delay;
            self.nextMultilineSendWhenTime += delay;
        #log( "** DEBUG: after: nextWhen: %d  nextMultilineSendWhenTime: %d  beginningNextWhenTime: %d  diff: %d" % ( nextWhen, self.nextMultilineSendWhenTime, beginningNextWhenTime, self.nextMultilineSendWhenTime - beginningNextWhenTime ));
        #log( "** sendrefdirect(): multilineSendLock.release() after processing target: %s" % ( target ));
        self.multilineSendLock.release();  # Lock shared between all multiline senders
    
    #@-node:sendSeenChannelUsers
    #@+node:setPeerBotOptions
    def setPeerBotOptions(self, botNick, botOptions ):

        if(self.bots.has_key( botNick )):
            try:
                options = eval( botOptions )
            except:
                return
            self.bots[ botNick ][ "options" ] = options;
            if( self.check_bot_peer_has_option( botNick, "bot2bot_announces" )):
                if( botNick not in self.botAnnouncePool ):
                    self.botAnnouncePool.append( botNick );
                    self.botAnnouncePool.sort();
            if( self.check_bot_peer_has_option( botNick, "bot2bot" )):
                if( botNick in self.botAnnouncePool ):
                    self.after( 2, self.sendAnnouncerTokenHolderNotify, botNick)
                    self.after( 4, self.sendSeenChannelUsers, botNick );

    #@-node:setPeerBotOptions
    #@+node:spamChannel
    def spamChannel(self):
        """
        Periodic plugs
        """

        if(self.tpeers == None):
            self.after(5, self.spamChannel);
            return
        if( self.number_of_refs_to_collect <= 0 ):
            return
        bot2bot_string = '';
        if( self.bot2bot_enabled ):
            bot2bot_string = "(bot2bot)";
        self.action(
            self.channel,
            "is a Freenet NodeRef Swap-bot owned by %s (install pyfcp as detailed at http://wiki.freenetproject.org/Refbot then run refbot.py; run updater.py periodically)(r%s/r%s)%s" % ( self.owner, FreenetNodeRefBot.svnRevision, MiniBot.svnRevision, bot2bot_string )
            )
        if(self.spam_interval > 0 and not self.bot2bot_trades_only_enabled):
            self.after(self.spam_interval, self.spamChannel)
    
    #@-node:spamChannel
    #@+node:thankChannel
    def thankChannelThenDie(self):
    
        if( self.nrefs > 0 ):
            if( self.number_of_refs_to_collect > 0 ):
                refs_plural_str = ''
                if( self.number_of_refs_to_collect > 1 ):
                    refs_plural_str = "s"
                self.privmsg(
                    self.channel,
                    "OK, I've got my %d noderef%s.  Thanks all." \
                    % ( self.number_of_refs_to_collect, refs_plural_str )
                    )
            else:
                self.privmsg(
                    self.channel,
                    "OK, I've got all the noderefs I need.  Thanks all."
                    )
            self.privmsg(
                self.channel,
                "Bye"
                )
        self.after(4, self.die)
    
    #@-node:thankChannelThenDie
    #@+node:addref
    def addref(self, url, replyfunc, sender_irc_nick, peerRef = None, botAddType = None):
    
        log("** adding ref: %s" % url)
        adderThread = AddRef(self.tmci_host, self.tmci_port, self.fcp_host, self.fcp_port, self.fcp_log_level, url, replyfunc, sender_irc_nick, self.irc_host, self.nodeDarknetIdentity, self.nodeDarknetRef, self.hasOpennet, self.nodeOpennetIdentity, self.nodeOpennetRef, self.darknet_trades_enabled, self.opennet_trades_enabled, peerRef, botAddType)
        self.adderThreads.append(adderThread)
        adderThread.start()
    
    #@-node:addref
    #@+node:check_bot_peer_has_option
    def check_bot_peer_has_option( self, botNick, option ):

        if( not self.bots.has_key( botNick )):
            return False;
        if( self.bots[ botNick ].has_key( "options" ) and option in self.bots[ botNick ][ "options" ] ):
            return True;
        return False;
    
    #@-node:check_bot_peer_has_option
    #@+node:check_bot_peer_is_already_added
    def check_bot_peer_is_already_added( self, botNick ):

        if( not self.bots.has_key( botNick )):
            return False;
        if( self.bots[ botNick ].has_key( "already_added" ) and self.bots[ botNick ][ "already_added" ] ):
            return True;
        if( self.bots[ botNick ].has_key( "opennet_already_added" ) and self.bots[ botNick ][ "opennet_already_added" ] ):
            return True;
        return False;
    
    #@-node:check_bot_peer_is_already_added
    #@+node:check_identity_with_node
    def check_identity_with_node(self, botIdentity):
    
        log("** checking identity with node: %s" % ( botIdentity ))
        identityCheckerThread = CheckIdentityWithNode(self.fcp_host, self.fcp_port, self.fcp_log_level, botIdentity)
        self.identityCheckerThreads.append(identityCheckerThread)
        identityCheckerThread.start()
    
    #@-node:check_identity_with_node
    #@+node:check_darknet_ref_from_bot_and_act
    def check_darknet_ref_from_bot_and_act(self, botNick ):

        if( not self.bots.has_key( botNick )):
            log("** can't check a ref from a bot using a nick (%s) we don't have a bots entry for.  They must have disconnected." % ( botNick ));
            return
        if( not self.bots[ botNick ].has_key( "identity" )):
            log("** can't check a ref from a bot using a nick (%s) we don't know the darknet identity of." % ( botNick ));
            return
        botIdentity = self.bots[ botNick ][ "identity" ];
        if( not self.botDarknetIdentities.has_key( botIdentity )):
            log("** don't want to check a ref from a bot with an identity (%s) we don't have a botDarknetIdentities entry for." % ( botIdentity ));
            return
        if( not self.bots[ botNick ].has_key( "ref" )):
            log("** can't check a ref from a bot using a nick (%s) we don't have any ref lines for." % ( botNick ));
            return
        if( not self.bots[ botNick ].has_key( "ref_terminated" )):
            log("** can't check a ref from a bot using a nick (%s) we don't have all the ref lines for." % ( botNick ));
            return
        if( self.bots[ botNick ].has_key( "ref_is_good" )):
            log("** don't want to check a ref from a bot using a nick (%s) we already think is good." % ( botNick ));
            return
        reflines = self.bots[ botNick ][ "ref" ]
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
        if( ref_fieldset.has_key( "testnet" ) and "true" == ref_fieldset[ "testnet" ].lower() ):
            log("** bot using nick '%s' gave us a testnet ref as a darknet ref." % ( botNick ));
            del self.bots[ botNick ][ "ref" ]
            del self.bots[ botNick ][ "ref_terminated" ]
            return
        if( ref_fieldset.has_key( "opennet" ) and "true" == ref_fieldset[ "opennet" ].lower() ):
            log("** bot using nick '%s' gave us an opennet ref as a darknet ref." % ( botNick ));
            del self.bots[ botNick ][ "ref" ]
            del self.bots[ botNick ][ "ref_terminated" ]
            return
        required_ref_fields = [ "dsaGroup.g", "dsaGroup.p", "dsaGroup.q", "dsaPubKey.y", "identity", "location", "myName", "sig" ];
        for require_ref_field in required_ref_fields:
            if(not ref_fieldset.has_key(require_ref_field)):
                log("** bot using nick '%s' gave us a ref missing the required '%s' field." % ( botNick, require_ref_field ));
                del self.bots[ botNick ][ "ref" ]
                del self.bots[ botNick ][ "ref_terminated" ]
                return
        if( ref_fieldset[ "identity" ] == self.nodeDarknetIdentity ):
            log("** bot using nick '%s' gave us our own node's darknet ref." % ( botNick ));
            del self.bots[ botNick ][ "ref" ]
            del self.bots[ botNick ][ "ref_terminated" ]
            return
        if( ref_fieldset[ "identity" ] == self.nodeOpennetIdentity ):
            log("** bot using nick '%s' gave us our own node's opennet ref." % ( botNick ));
            del self.bots[ botNick ][ "ref" ]
            del self.bots[ botNick ][ "ref_terminated" ]
            return
        if( ref_fieldset[ "identity" ] != botIdentity ):
            log("** bot using nick '%s' gave us a ref that doesn't match the identity they claimed they have: %s" % ( botNick, botIdentity ));
            del self.bots[ botNick ][ "ref" ]
            del self.bots[ botNick ][ "ref_terminated" ]
            return
        self.bots[ botNick ][ "ref_is_good" ] = True
        self.privmsg( botNick, "haveref" );

    #@-node:check_darknet_ref_from_bot_and_act
    #@+node:check_opennet_ref_from_bot_and_act
    def check_opennet_ref_from_bot_and_act(self, botNick ):

        if( not self.bots.has_key( botNick )):
            log("** can't check a ref from a bot using a nick (%s) we don't have a bots entry for.  They must have disconnected." % ( botNick ));
            return
        if( not self.bots[ botNick ].has_key( "opennet_identity" )):
            log("** can't check a ref from a bot using a nick (%s) we don't know the opennet identity of." % ( botNick ));
            return
        botIdentity = self.bots[ botNick ][ "opennet_identity" ];
        if( not self.botOpennetIdentities.has_key( botIdentity )):
            log("** don't want to check an opennet ref from a bot with an identity (%s) we don't have a botOpennetIdentities entry for." % ( botIdentity ));
            return
        if( not self.bots[ botNick ].has_key( "opennet_ref" )):
            log("** can't check an opennet ref from a bot using a nick (%s) we don't have any opennet ref lines for." % ( botNick ));
            return
        if( not self.bots[ botNick ].has_key( "opennet_ref_terminated" )):
            log("** can't check an opennet ref from a bot using a nick (%s) we don't have all the opennet ref lines for." % ( botNick ));
            return
        if( self.bots[ botNick ].has_key( "opennet_ref_is_good" )):
            log("** don't want to check an opennet ref from a bot using a nick (%s) we already think is good." % ( botNick ));
            return
        reflines = self.bots[ botNick ][ "opennet_ref" ]
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
        if( ref_fieldset.has_key( "testnet" ) and "true" == ref_fieldset[ "testnet" ].lower() ):
            log("** bot using nick '%s' gave us a testnet ref as an opennet ref." % ( botNick ));
            del self.bots[ botNick ][ "opennet_ref" ]
            del self.bots[ botNick ][ "opennet_ref_terminated" ]
            return
        if( not ref_fieldset.has_key( "opennet" ) or "false" == ref_fieldset[ "opennet" ].lower() ):
            log("** bot using nick '%s' gave us a darknet ref as an opennet ref." % ( botNick ));
            del self.bots[ botNick ][ "opennet_ref" ]
            del self.bots[ botNick ][ "opennet_ref_terminated" ]
            return
        required_ref_fields = [ "dsaGroup.g", "dsaGroup.p", "dsaGroup.q", "dsaPubKey.y", "identity", "location", "opennet", "sig" ];
        for require_ref_field in required_ref_fields:
            if(not ref_fieldset.has_key(require_ref_field)):
                log("** bot using nick '%s' gave us a ref missing the required '%s' field." % ( botNick, require_ref_field ));
                del self.bots[ botNick ][ "opennet_ref" ]
                del self.bots[ botNick ][ "opennet_ref_terminated" ]
                return
        if( ref_fieldset[ "identity" ] == self.nodeDarknetIdentity ):
            log("** bot using nick '%s' gave us our own node's darknet ref." % ( botNick ));
            del self.bots[ botNick ][ "opennet_ref" ]
            del self.bots[ botNick ][ "opennet_ref_terminated" ]
            return
        if( ref_fieldset[ "identity" ] == self.nodeOpennetIdentity ):
            log("** bot using nick '%s' gave us our own node's opennet ref." % ( botNick ));
            del self.bots[ botNick ][ "opennet_ref" ]
            del self.bots[ botNick ][ "opennet_ref_terminated" ]
            return
        if( ref_fieldset[ "identity" ] != botIdentity ):
            log("** bot using nick '%s' gave us a ref that doesn't match the identity they claimed they have: %s" % ( botNick, botIdentity ));
            del self.bots[ botNick ][ "opennet_ref" ]
            del self.bots[ botNick ][ "opennet_ref_terminated" ]
            return
        self.bots[ botNick ][ "opennet_ref_is_good" ] = True
        self.privmsg( botNick, "haveopennetref" );

    #@-node:check_opennet_ref_from_bot_and_act
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
    #@+node:dodirectordie
    def dodirectordie(self, peernick ):
        
        #log( "** dodirectordie(): directOrDieLock.acquire() before processing peernick: %s" % ( peernick ));
        self.directOrDieLock.acquire( 1 );
        f = None;
        nodeIsUp = False;
        try:
            f = fcp.FCPNode( host = self.fcp_host, port = self.fcp_port, logfunc = log, verbosity = self.fcp_log_level )
            nodeIsUp = True;
            f.shutdown();
            self.nodeCommsProblemCount = 0;
        except Exception, msg:
            nodeIsUp = False;
            if(f != None):
              f.shutdown();
        #log( "** dodirectordie(): directOrDieLock.release() after processing peernick: %s" % ( peernick ));
        self.directOrDieLock.release();
        if( nodeIsUp ):
            self.privmsg( peernick, "I can talk to my node" )
        else:
            self.privmsg( peernick, "I cannot talk to my node" )
            self.privmsg(
                self.channel,
                "Sorry, seems I couldn't collect my target number of refs before the node stopped talking to me.  Thanks anyway."
                )
            self.privmsg(
                self.channel,
                "Bye"
                )
            self.after(4, self.die)
    
    #@-node:dodirectordie
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
        url = self.sanitize_ref_url( url );
        if( self.check_ref_url_and_complain(url, replyfunc)):
           self.addref(url, replyfunc, sender_irc_nick)

    #@-node:maybe_add_ref
    #@+node:sanitize_ref_url
    def sanitize_ref_url(self, url):
        """
        Remove extra characters that can be sent by a user, but which may trip up the bot unintentionally
        """
        url = url.strip();
        sanitized_url = '';
        for item in url:
          if( item in string.printable ):
            sanitized_url += item;
        return sanitized_url;

    #@-node:sanitize_ref_url
    #@+node:sendopennetrefdirect
    def sendopennetrefdirect(self, peernick, is_bot ):
        
        nodeOpennetRefKeys = self.nodeOpennetRef.keys()
        nodeOpennetRefKeys.sort()
        #log( "** sendrefdirect(): multilineSendLock.acquire() before processing peernick: %s" % ( peernick ));
        self.multilineSendLock.acquire( 1 );  # Lock shared between all multiline senders
        # Spread out the lines of the ref so we don't trigger the babbler detector of a receiving refbot
        nextWhen = 0;
        now = long( math.floor( time.time() ));
        if( self.nextMultilineSendWhenTime > now):  # self.nextMultilineSendWhenTime shared between all multiline senders
          nextWhen = self.nextMultilineSendWhenTime - now;
        else:
          self.nextMultilineSendWhenTime = now;
        beginningNextWhenTime = self.nextMultilineSendWhenTime;
        #log( "** DEBUG: before: nextWhen: %d  nextMultilineSendWhenTime: %d" % ( nextWhen, self.nextMultilineSendWhenTime ));
        for nodeOpennetRefKey in nodeOpennetRefKeys:
            self.after( nextWhen, self.privmsg, peernick, "opennetrefdirect %s=%s" % ( nodeOpennetRefKey, self.nodeOpennetRef[ nodeOpennetRefKey ] ))
            delay = random.randint(7,14)  # 7-14 seconds between each line
            nextWhen += delay;
            self.nextMultilineSendWhenTime += delay;
        self.after( nextWhen, self.privmsg, peernick, "opennetrefdirect End" )
        #log( "** DEBUG: after: nextWhen: %d  nextMultilineSendWhenTime: %d  beginningNextWhenTime: %d  diff: %d" % ( nextWhen, self.nextMultilineSendWhenTime, beginningNextWhenTime, self.nextMultilineSendWhenTime - beginningNextWhenTime ));
        #log( "** sendrefdirect(): multilineSendLock.release() after processing peernick: %s" % ( peernick ));
        self.multilineSendLock.release();  # Lock shared between all multiline senders
    
    #@-node:sendopennetrefdirect
    #@+node:process_any_identities_checked
    def process_any_identities_checked(self):
        if(len(self.identityCheckerThreads) != 0):
            for identityCheckerThread in self.identityCheckerThreads:
                if(not identityCheckerThread.isAlive()):
                    identityCheckerThread.join()
                    log("identityCheckerThread has status: %s  identity: %s  status_msg: %s" % (identityCheckerThread.status, identityCheckerThread.identity, identityCheckerThread.status_msg))
                    self.identityCheckerThreads.remove(identityCheckerThread)
                    status = identityCheckerThread.status
                    botIdentity = identityCheckerThread.identity;
                    if( self.botDarknetIdentities.has_key( botIdentity )):
                      botNick = self.botDarknetIdentities[ botIdentity ];
                      if( not self.bots.has_key( botNick )):
                          log("** checked bot nick (%s) we don't have a bots entry for.  They must have disconnected." % ( botNick ));
                          continue
                      if( self.check_bot_peer_is_already_added( botNick )):
                          continue
                      if(1 == status):
                          self.nodeCommsProblemCount = 0;
                          self.privmsg( botNick, "havepeer" );
                          self.bots[ botNick ][ "already_added" ] = True;
                      elif( 0 == status ):
                          self.nodeCommsProblemCount = 0;
                          if( self.bots[ botNick ].has_key( "ref" ) and self.bots[ botNick ].has_key( "ref_terminated" ) and self.bots[ botNick ].has_key( "ref_is_good" )):
                              self.privmsg( botNick, "haveref" );
                          elif( self.bots[ botNick ].has_key( "ref" )):
                              log("** completed an darknet identity check, but the darknet ref is already being transferred, so will take no further action");
                          else:
                              if( self.bot2bot_darknet_trades_enabled ):
                                  if( self.bot2bot_darknet_trades_enabled and self.check_bot_peer_has_option( botNick, "bot2bot_darknet_trades" )):
                                      self.after(random.randint(15, 90), self.sendGetRefDirect, botNick)  # Ask for their ref to be sent directly after 15-90 seconds
                      else:
                          log("** error checking bot identity (%s): %s" % ( botIdentity, identityCheckerThread.status_msg ));
                      continue
                    elif( self.botOpennetIdentities.has_key( botIdentity )):
                      botNick = self.botOpennetIdentities[ botIdentity ];
                      if( not self.bots.has_key( botNick )):
                          log("** checked bot nick (%s) we don't have a bots entry for.  They must have disconnected." % ( botNick ));
                          continue
                      if( self.check_bot_peer_is_already_added( botNick )):
                          continue
                      if(1 == status):
                          self.nodeCommsProblemCount = 0;
                          self.privmsg( botNick, "haveopennetpeer" );
                          self.bots[ botNick ][ "opennet_already_added" ] = True;
                      elif( 0 == status ):
                          self.nodeCommsProblemCount = 0;
                          if( self.bots[ botNick ].has_key( "opennet_ref" ) and self.bots[ botNick ].has_key( "opennet_ref_terminated" ) and self.bots[ botNick ].has_key( "opennet_ref_is_good" )):
                              self.privmsg( botNick, "haveopennetref" );
                          elif( self.bots[ botNick ].has_key( "opennet_ref" )):
                              log("** completed an opennet identity check, but the opennet ref is already being transferred, so will take no further action");
                          else:
                              if( self.bot2bot_opennet_trades_enabled ):
                                  if( self.bot2bot_opennet_trades_enabled and self.check_bot_peer_has_option( botNick, "bot2bot_opennet_trades" )):
                                      self.after(random.randint(15, 90), self.sendGetOpennetRefDirect, botNick)  # Ask for their ref to be sent directly after 15-90 seconds
                      else:
                          log("** error checking bot identity (%s): %s" % ( botIdentity, identityCheckerThread.status_msg ));
                      continue
                    log("** checked bot identity (%s) we don't have a bot nickname for.  They must have disconnected." % ( botIdentity ));
        self.after(1, self.process_any_identities_checked)
    
    #@-node:process_any_identities_checked
    #@+node:process_any_refs_added
    def process_any_refs_added(self):
        if(len(self.adderThreads) != 0):
            for adderThread in self.adderThreads:
                if(not adderThread.isAlive()):
                    adderThread.join()
                    log("adderThread has status: %s  url: %s  error_msg: %s" % (adderThread.status, adderThread.url, adderThread.error_msg))
                    self.adderThreads.remove(adderThread)
                    if(0 < adderThread.status):
                        self.nodeCommsProblemCount = 0;
                        if( adderThread.peerRef != None ):
                            if( adderThread.botAddType == "request" ):
                                if(adderThread.isDarknetRef):
                                    self.after(random.randint(7, 20), self.sendDoRefSwapAllow, adderThread.sender_irc_nick)  # After 7-20 seconds, agree to swap refs with them
                                elif(adderThread.isOpennetRef):
                                    self.after(random.randint(7, 20), self.sendDoOpennetRefSwapAllow, adderThread.sender_irc_nick)  # After 7-20 seconds, agree to swap refs with them
                            else:
                                if(adderThread.isDarknetRef):
                                    self.after(2, self.sendDoRefSwapCompleted, adderThread.sender_irc_nick)  # After 2 seconds, tell them we've completed the swap
                                elif(adderThread.isOpennetRef):
                                    self.after(2, self.sendDoOpennetRefSwapCompleted, adderThread.sender_irc_nick)  # After 2 seconds, tell them we've completed the swap
                                self.nrefs += 1
                                refs_to_go = self.number_of_refs_to_collect - self.nrefs
                                refs_plural_str = ''
                                if( refs_to_go > 1 ):
                                    refs_plural_str = "s"
                                if(adderThread.isDarknetRef):
                                  log("** Added darknet ref via bot2bot trade with %s (%d ref%s to go)" % ( adderThread.sender_irc_nick, refs_to_go, refs_plural_str ))
                                else:
                                  log("** Added opennet ref via bot2bot trade with %s (%d ref%s to go)" % ( adderThread.sender_irc_nick, refs_to_go, refs_plural_str ))
                                if self.nrefs >= self.number_of_refs_to_collect:
                                    log("Got our %d refs, now terminating!" % ( self.number_of_refs_to_collect ))
                                    self.after(3, self.thankChannelThenDie)
                        elif( self.bot2bot_trades_only_enabled ):
                            log("** Somehow we got in the post-add phase of things, but not from a bot2bot trade when we're doing bot2bot trades only")
                        else:
                            self.refs.append(adderThread.url)
                            self.save()
                            self.nrefs += 1
                            if(adderThread.isDarknetRef):
                              log("** added darknet ref: %s" % adderThread.url)
                            else:
                              log("** added opennet ref: %s" % adderThread.url)
                            refs_to_go = self.number_of_refs_to_collect - self.nrefs
                            refs_to_go_str = ''
                            if refs_to_go > 0:
                                refs_plural_str = ''
                                if( refs_to_go > 1 ):
                                    refs_plural_str = "s"
                                refs_to_go_str = " (%d ref%s to go)" % ( refs_to_go, refs_plural_str )
                            if(2 == adderThread.status):
                                adderThread.replyfunc("while adding your ref, I noticed that it does not have a physical.udp line.  Once you get a connection and that line is added to your ref, renew the URL you share with people (and bots)")
                            if(adderThread.isDarknetRef):
                                adderThread.replyfunc("added your ref.  Now please add mine <%s> to create a peer connection.%s" % (self.refurl, refs_to_go_str))
                            else:
                                adderThread.replyfunc("added your ref.  Now please add mine <%s> to create a peer connection.%s" % (self.opennet_refurl, refs_to_go_str))
                            if self.nrefs >= self.number_of_refs_to_collect:
                                log("Got our %d refs, now terminating!" % ( self.number_of_refs_to_collect ))
                                self.after(3, self.thankChannelThenDie)
                    else:
                        if( adderThread.peerRef != None ):
                            if( adderThread.botAddType == "request" ):
                                if(adderThread.isDarknetRef):
                                    self.after(random.randint(7, 20), self.sendDoRefSwapDeny, adderThread.sender_irc_nick)  # After 7-20 seconds, agree to swap refs with them
                                elif(adderThread.isOpennetRef):
                                    self.after(random.randint(7, 20), self.sendDoOpennetRefSwapDeny, adderThread.sender_irc_nick)  # After 7-20 seconds, agree to swap refs with them
                            else:
                                if(adderThread.isDarknetRef):
                                    self.after(random.randint(7, 20), self.sendDoRefSwapFailed, adderThread.sender_irc_nick)  # After 7-20 seconds, agree to swap refs with them
                                elif(adderThread.isDarknetRef):
                                    self.after(random.randint(7, 20), self.sendDoOpennetRefSwapFailed, adderThread.sender_irc_nick)  # After 7-20 seconds, agree to swap refs with them
                        else:
                            error_str = "there was some unknown problem while trying to add your ref.  Try again and/or try again later."
                            if(0 == adderThread.status):
                                error_str = "there was a general error while trying to add your ref.  Try again and/or try again later."
                            elif(-1 == adderThread.status):
                                error_str = "the URL does not contain a valid ref (%s).  Please correct the ref at the URL or the URL itself <%s> and try again." % (adderThread.error_msg, adderThread.url)
                            elif(-2 == adderThread.status):
                                known_pastebin_result = self.url_is_known_pastebin( adderThread.url );
                                if( None == known_pastebin_result ):
                                    error_str = "there was a problem fetching the given URL.  Please correct the URL <%s> and try again or try again later/try a different server if you suspect server troubles." % (adderThread.url)
                                else:
                                    error_str = "there was a problem fetching the given URL.  Please correct the URL <%s> and try again, try again later or perhaps try a different pastebin such as %s" % (adderThread.url, known_pastebin_result)
                            elif(-3 == adderThread.status):
                                error_str = "there was a problem while I was talking to my partner node.  Please try again later."
                                self.nodeCommsProblemCount += 1;
                                if( "Zothar" in self.usersInChan ):
                                    self.privmsg(
                                        "Zothar",
                                        "%s had trouble talking to it's partner node while adding the ref from %s (extended_error_msg is %s)" % (self.botircnick, adderThread.sender_irc_nick, adderThread.extended_error_msg)
                                        )
                                elif( "Zothar_Work" in self.usersInChan ):
                                    self.privmsg(
                                        "Zothar_Work",
                                        "%s had trouble talking to it's partner node while adding the ref from %s (extended_error_msg is %s)" % (self.botircnick, adderThread.sender_irc_nick, adderThread.extended_error_msg)
                                        )
                            elif(-4 == adderThread.status):
                                error_str = "the node reports that it already has a peer with that identity.  Ref not re-added."
                            elif(-5 == adderThread.status):
                                error_str = "the node reports that it already has a ref with its own identity.  Ref not added."
                            elif(-6 == adderThread.status):
                                error_str = adderThread.error_msg
                            elif(-7 == adderThread.status):
                                error_str = "the node could not add your peer for some reason.  Gave it a corrupted ref maybe?  It cannot be edited nor \"word wrapped\".  Check your ref and try again.  Ref not added."
                            elif(-8 == adderThread.status):
                                error_str = "this bot does not currently trade testnet node references.  Ref not added."
                            elif(-9 == adderThread.status):
                                error_str = "this bot does not currently trade darknet node references.  Ref not added."
                            elif(-10 == adderThread.status):
                                error_str = "this bot does not currently trade opennet node references.  Ref not added."
                            refs_to_go = self.number_of_refs_to_collect - self.nrefs
                            refs_to_go_str = ''
                            if refs_to_go > 0:
                                refs_plural_str = ''
                                if( refs_to_go > 1 ):
                                    refs_plural_str = "s"
                                refs_to_go_str = " (%d ref%s to go)" % ( refs_to_go, refs_plural_str )
                            adderThread.replyfunc("%s%s" % (error_str, refs_to_go_str))
                            if( 2 <= self.nodeCommsProblemCount ):
                                # Die if we've had too many failures talking to the node
                                self.privmsg(
                                    self.channel,
                                    "Sorry, seems I couldn't collect my target number of refs before the node stopped talking to me.  Thanks anyway."
                                    )
                                self.privmsg(
                                    self.channel,
                                    "Bye"
                                    )
                                self.after(4, self.die)
        self.after(0.5, self.process_any_refs_added)
    
    #@-node:process_any_refs_added
    #@+node:process_peer_updates
    def process_peer_updates(self):
        if(len(self.peerUpdaterThreads) != 0):
            for peerUpdaterThread in self.peerUpdaterThreads:
                if(not peerUpdaterThread.isAlive()):
                    peerUpdaterThread.join()
                    self.peerUpdaterThreads.remove(peerUpdaterThread)
                    if(peerUpdaterThread.cpeers == None):
                        continue
                    if(peerUpdaterThread.tpeers == None):
                        continue
                    while(self.number_of_refs_to_collect > 0 and (self.number_of_refs_to_collect - self.nrefs) > 0 and ((peerUpdaterThread.cpeers + (self.number_of_refs_to_collect - self.nrefs)) > self.max_cpeers)):
                        self.number_of_refs_to_collect -= 1;
                    while(self.number_of_refs_to_collect > 0 and (self.number_of_refs_to_collect - self.nrefs) > 0 and ((peerUpdaterThread.tpeers + (self.number_of_refs_to_collect - self.nrefs)) > self.max_tpeers)):
                        self.number_of_refs_to_collect -= 1;
                    if(self.number_of_refs_to_collect <= 0):
                        log("Don't need any more refs, now terminating!")
                        self.after(3, self.thankChannelThenDie)
                        break
                    self.cpeers = peerUpdaterThread.cpeers
                    self.tpeers = peerUpdaterThread.tpeers
        self.after(1, self.process_peer_updates)
    
    #@-node:process_peer_updates
    #@+node:prompt
    def prompt(self, msg, dflt=None):
        if dflt:
            return raw_input(msg + " [%s]: " % dflt) or dflt
        else:
            while 1:
                resp = raw_input(msg + ": ")
                if resp:
                    return resp

    #@-node:prompt
    #@+node:sendrefdirect
    def sendrefdirect(self, peernick, is_bot ):
        
        nodeDarknetRefKeys = self.nodeDarknetRef.keys()
        nodeDarknetRefKeys.sort()
        #log( "** sendrefdirect(): multilineSendLock.acquire() before processing peernick: %s" % ( peernick ));
        self.multilineSendLock.acquire( 1 );  # Lock shared between all multiline senders
        # Spread out the lines of the ref so we don't trigger the babbler detector of a receiving refbot
        nextWhen = 0;
        now = long( math.floor( time.time() ));
        if( self.nextMultilineSendWhenTime > now):
          nextWhen = self.nextMultilineSendWhenTime - now;
        else:
          self.nextMultilineSendWhenTime = now;
        beginningNextWhenTime = self.nextMultilineSendWhenTime;
        #log( "** DEBUG: before: nextWhen: %d  nextMultilineSendWhenTime: %d" % ( nextWhen, self.nextMultilineSendWhenTime ));
        for nodeDarknetRefKey in nodeDarknetRefKeys:
            self.after( nextWhen, self.privmsg, peernick, "refdirect %s=%s" % ( nodeDarknetRefKey, self.nodeDarknetRef[ nodeDarknetRefKey ] ))
            delay = random.randint(7,14)  # 7-14 seconds between each line
            nextWhen += delay;
            self.nextMultilineSendWhenTime += delay;
        self.after( nextWhen, self.privmsg, peernick, "refdirect End" )
        #log( "** DEBUG: after: nextWhen: %d  nextMultilineSendWhenTime: %d  beginningNextWhenTime: %d  diff: %d" % ( nextWhen, self.nextMultilineSendWhenTime, beginningNextWhenTime, self.nextMultilineSendWhenTime - beginningNextWhenTime ));
        #log( "** sendrefdirect(): multilineSendLock.release() after processing peernick: %s" % ( peernick ));
        self.multilineSendLock.release();  # Lock shared between all multiline senders
    
    #@-node:sendrefdirect
    #@+node:url_is_known_pastebin
    def url_is_known_pastebin(self, url):
    
        if( "http://code.bulix.org/" == url[ :22 ].lower() ):
            return "pastebin.ca or rafb.net/paste/"
        if( "http://dark-code.bulix.org/" == url[ :27 ].lower() ):
            return "pastebin.ca or rafb.net/paste/"
        if( "http://pastebin.ca/" == url[ :19 ].lower() ):
            return "dark-code.bulix.org or rafb.net/paste/"
        if( "http://rafb.net/paste/results/" == url[ :30 ].lower() ):
            return "dark-code.bulix.org or pastebin.ca"
        if( "http://www.rafb.net/paste/results/" == url[ :34 ].lower() ):
            return "dark-code.bulix.org or pastebin.ca"
        return None
    
    #@-node:url_is_known_pastebin
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
            if(self.greet_interval > 0 and t > self.greet_interval and not self.bot2bot_trades_only_enabled):
                self.greetChannel()
    
    #@-node:thrd
    #@+node:addBogonCIDRNet
    def addBogonCIDRNet( self, networkstr ):

        if( FreenetNodeRefBot.bogons.has_key( networkstr )):
            log("DEBUG: already has net: %s" % ( networkstr ));
            return False;
        nums_result = cidrNetToNumbers( networkstr );
        if( None == nums_result ):
            return None;
        ( network, bits ) = nums_result;
        fields = string.split( network, '.' );
        one = fields[ 0 ];
        two = string.join(( fields[ 0 ], fields[ 1 ] ), '.' );
        three = string.join(( fields[ 0 ], fields[ 1 ], fields[ 2 ] ), '.' );
        if( bits >= 24 ):
            self.addBogonCIDRNetHelper( three, networkstr );
        elif( bits >= 16 ):
            self.addBogonCIDRNetHelper( two, networkstr );
        elif( bits >= 8 ):
            self.addBogonCIDRNetHelper( one, networkstr );
        else:
            self.addBogonCIDRNetHelper( "0", networkstr );
        networknum = refbot_inet_aton( network );
        network = getNetworkAddressFromCIDRNet( networkstr );
        FreenetNodeRefBot.bogons[ networkstr ] = [ network, networknum, bits ];

    #@-node:addBogonCIDRNet
    #@-node:addBogonCIDRNetHelper
    def addBogonCIDRNetHelper( self, key, networkstr ):

        if( not FreenetNodeRefBot.bogons.has_key( key )):
            FreenetNodeRefBot.bogons[ key ] = networkstr;
        else:
            tmpstr = FreenetNodeRefBot.bogons[ key ];
            tmpstr = tmpstr + ' ' + networkstr;
            FreenetNodeRefBot.bogons[ key ] = tmpstr;

    #@-node:addBogonCIDRNetHelper
    #@-node:getAnnouncerTokenHolder
    def getAnnouncerTokenHolder( self ):

        # **FIXME** This is a minimal implementation; needs to do token passing and elections
        if( 0 >= len( self.botAnnouncePool )):
            return None
        return self.botAnnouncePool[ 0 ]

    #@-node:getAnnouncerTokenHolder
    #@+node:findBogonCIDRNet
    def findBogonCIDRNet( self, ipstr ):

        fields = string.split( ipstr, '.' );
        if( len( fields ) != 4 ):
            return None;
        one = fields[ 0 ];
        two = string.join(( fields[ 0 ], fields[ 1 ] ), '.' );
        three = string.join(( fields[ 0 ], fields[ 1 ], fields[ 2 ] ), '.' );
        if( FreenetNodeRefBot.bogons.has_key( three )):
            result = self.findBogonCIDRNetHelper( three, ipstr );
            if( result != 0 ):
              return result;
        if( FreenetNodeRefBot.bogons.has_key( two )):
            result = self.findBogonCIDRNetHelper( two, ipstr );
            if( result != 0 ):
              return result;
        if( FreenetNodeRefBot.bogons.has_key( one )):
            result = self.findBogonCIDRNetHelper( one, ipstr );
            if( result != 0 ):
              return result;
        if( FreenetNodeRefBot.bogons.has_key( "0" )):
            result = self.findBogonCIDRNetHelper( "0", ipstr );
            if( result != 0 ):
              return result;
        return False;

    #@-node:findBogonCIDRNet
    #@+node:findBogonCIDRNetHelper
    def findBogonCIDRNetHelper( self, key, ipstr ):

        cidr_net_list_str = FreenetNodeRefBot.bogons[ key ];
        cidr_net_list = string.split( cidr_net_list_str, ' ' );
        cidr_net_list.sort( sortByHostmaskCompareFunction );
        cidr_net_list.reverse();
        for cidr_net in cidr_net_list:
            result = isIPInCIDRNet( ipstr, cidr_net );
            if( result ):
                return cidr_net;
        return False;

    #@-node:findBogonCIDRNetHelper
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
    def on_unknownCommand(self, replyfunc, is_from_privmsg, cmd, msg):
        """
        Pick up possible URLs
        """
        if(cmd.startswith("http://")):
            if( self.bot.bot2bot_trades_only_enabled ):
                replyfunc("Sorry, I'm configured to only trade refs with other bots and to not trade directly with humans.  Send me the \"help\" command to learn how to run your own ref swapping bot.")
                return True
            if( self.bot.privmsg_only_enabled and not is_from_privmsg ):
                replyfunc = self.privmsg
            if(cmd == self.bot.refurl):
                self.privmsg("error - already have my own ref <%s>" % (cmd))
                return True
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
    #@+node:cmd_addref
    def cmd_addref(self, replyfunc, is_from_privmsg, args):
    
        if( self.bot.bot2bot_trades_only_enabled ):
            replyfunc("Sorry, I'm configured to only trade refs with other bots and to not trade directly with humans.  Send me the \"help\" command to learn how to run your own ref swapping bot.")
            return
        if( self.bot.privmsg_only_enabled and not is_from_privmsg ):
            replyfunc = self.privmsg
        if len(args) != 1:
            self.privmsg(
                "Invalid argument count",
                "Syntax: addref <url>"
                )
            return
        
        url = args[0]
        if(url == self.bot.refurl):
            self.privmsg("error - already have my own ref <%s>" % (url))
            return
        if(not self.bot.has_ref(url)):
            self.bot.maybe_add_ref(url.strip(), replyfunc, self.peernick)
        else:
            self.privmsg("error - already have your ref <%s>"% (url))
    
    #@-node:cmd_addref
    #@+node:cmd_announcertokennotify
    def cmd_announcertokennotify(self, replyfunc, is_from_privmsg, args):
    
        if( not self.bot.bot2bot_announces_enabled ):
            replyfunc("error - Sorry, I'm not configured to do bot2bot-based cooperative announcing.")
            return
        if( self.bot.privmsg_only_enabled and not is_from_privmsg ):
            replyfunc = self.privmsg
        if( 2 > len( args )):
            self.privmsg(
                "error: Invalid argument count for 'announcertokennotify'",
                )
            return
        
        purportedAnnouncerTokenHolder = args[0]
        partialAnnouncerCandidatesString = " ".join( args[ 1: ] )
        try:
            partialAnnouncerCandidates = eval( partialAnnouncerCandidatesString )
        except:
            log("?? DEBUG: Failed to eval partialAnnouncerCandidatesString: %s" % ( partialAnnouncerCandidatesString ))
            log_traceback()
        if( not self.bot.check_bot_peer_has_option( self.peernick, "bot2bot_announces" )):
            log("** DEBUG: NOTICE: Following from bot that we don't have an 'bot2bot_announces' option specified for yet")
        log("** DEBUG: purportedAnnouncerTokenHolder: %s" % ( purportedAnnouncerTokenHolder ))
        log("** DEBUG: partialAnnouncerCandidates: %s" % ( partialAnnouncerCandidates ))
        # **FIXME** The following probably needs some sort of "popularity" check before it's accepted
        if( self.bot.check_bot_peer_has_option( self.peernick, "bot2bot_announces" )):
            if( None == self.bot.announcerTokenHolder and purportedAnnouncerTokenHolder in self.bot.usersInChan ):
                log("** DEBUG: announcerTokenHolder %s -> %s" % ( self.bot.announcerTokenHolder, purportedAnnouncerTokenHolder ))
                self.bot.announcerTokenHolder = purportedAnnouncerTokenHolder
            elif( None != self.bot.announcerTokenHolder ):
                if( not purportedAnnouncerTokenHolder in self.bot.usersInChan ):
                    #log("** DEBUG: ignoring non-changing announcertokennotify from %s about not-in-channel holder %s" % ( self.peernick, purportedAnnouncerTokenHolder ))
                    log("** DEBUG: ignoring non-changing announcertokennotify from %s about not-in-channel holder %s and forcing a re-election" % ( self.peernick, purportedAnnouncerTokenHolder ))
                    # **FIXME** perhaps this should instead set the holder to None and force an "election", but that might a DoS opportunity
                    # **FIXME** perhaps instead this should have us pick who we think it should be and notify the sender of that fact (hmm... with "hop limit" or something???)
                    self.bot.announcerTokenHolder = None
                    self.after(announcerTokenHolderPickDelay, self.bot.maybe_set_announcerTokenHolder)
                if( self.bot.announcerTokenHolder == purportedAnnouncerTokenHolder ):
                    log("** DEBUG: ignoring non-changing announcertokennotify from %s about holder %s" % ( self.peernick, purportedAnnouncerTokenHolder ))
                elif( self.peernick == self.bot.announcerTokenHolder ):
                    log("** DEBUG: announcerTokenHolder %s -> %s" % ( self.bot.announcerTokenHolder, purportedAnnouncerTokenHolder ))
                    self.bot.announcerTokenHolder = purportedAnnouncerTokenHolder
                else:
                    log("** DEBUG: ignoring announcerTokenHolder change notification from 'non-authoritative' source (%s): %s -> %s" % ( self.peernick, self.bot.announcerTokenHolder, purportedAnnouncerTokenHolder ))
    
    #@-node:cmd_announcertokennotify
    #@+node:cmd_bothello
    def cmd_bothello( self, replyfunc, is_from_privmsg, args ):

        if( self.bot.bot2bot_enabled ):
            if(not self.bot.bots.has_key( self.peernick )):
                bot_data = {}
                self.bot.bots[ self.peernick ] = bot_data
                log("** bots: %s" % ( self.bot.bots.keys() ))
            if(self.bot.bots.has_key( self.peernick ) and not self.bot.bots[ self.peernick ].has_key( "options" )):
                self.after(random.randint(7, 20), self.bot.sendGetOptions, self.peernick)  # Ask for their options after 7-20 seconds
            if( self.peernick in self.bot.usersInChan ):
                self.bot.usersInChan.remove( self.peernick )
    
    #@-node:cmd_bothello
    #@+node:cmd_dodirectordie
    def cmd_dodirectordie(self, replyfunc, is_from_privmsg, args):
    
        if( not is_from_privmsg ):
            return;
        self.bot.dodirectordie(self.peernick)

    #@-node:cmd_dodirectordie
    #@+node:cmd_doopennetrefswapallow
    def cmd_doopennetrefswapallow(self, replyfunc, is_from_privmsg, args):

        # NOTE: We'll not have asked if from our perspective we didn't want to swap, but we don't want to add a opennet ref for a bot we don't think we can respond to (because they disconnected or something)
        # NOTE: Also, we don't want anybody to try to "cheat" the "negotiation" scheme
        if( self.bot.bot2bot_opennet_trades_enabled ):
            if( self.bot.check_bot_peer_has_option( self.peernick, "bot2bot_opennet_trades" )):
                if( self.bot.bots[ self.peernick ].has_key( "opennet_ref" ) and self.bot.bots[ self.peernick ].has_key( "opennet_ref_terminated" ) and self.bot.bots[ self.peernick ].has_key( "opennet_ref_is_good" )):
                    self.bot.addref( "(opennet from bot: %s)" % ( self.peernick ), replyfunc, self.peernick, self.bot.bots[ self.peernick ][ "opennet_ref" ], "allow" )
                elif( self.bot.bots[ self.peernick ].has_key( "opennet_already_added" )):
                    self.after(2, self.bot.sendDoOpennetRefSwapCompleted, self.peernick)  # After 2 seconds, tell them we've completed the swap (since we already had the peer added to the node)
    
    #@-node:cmd_doopennetrefswapallow
    #@+node:cmd_doopennetrefswapcompleted
    def cmd_doopennetrefswapcompleted(self, replyfunc, is_from_privmsg, args):

        self.bot.nrefs += 1
        refs_to_go = self.bot.number_of_refs_to_collect - self.bot.nrefs
        refs_plural_str = ''
        if( refs_to_go > 1 ):
            refs_plural_str = "s"
        log("** Added opennet ref via bot2bot trade with %s (%d ref%s to go)" % ( self.peernick, refs_to_go, refs_plural_str ))
        if self.bot.nrefs >= self.bot.number_of_refs_to_collect:
            log("Got our %d refs, now terminating!" % ( self.bot.number_of_refs_to_collect ))
            self.after(3, self.bot.thankChannelThenDie)
    
    #@-node:cmd_doopennetrefswapcompleted
    #@+node:cmd_doopennetrefswapdeny
    def cmd_doopennetrefswapdeny(self, replyfunc, is_from_privmsg, args):

        pass  # So nothing is going to continue from here in the current "state machine"

    #@-node:cmd_doopennetrefswapdeny
    #@+node:cmd_doopennetrefswapfailed
    def cmd_doopennetrefswapfailed(self, replyfunc, is_from_privmsg, args):

        pass  # So nothing is going to continue from here in the current "state machine"

    #@-node:cmd_doopennetrefswapfailed
    #@+node:cmd_doopennetrefswaprequest
    def cmd_doopennetrefswaprequest(self, replyfunc, is_from_privmsg, args):

        if( self.bot.bot2bot_opennet_trades_enabled ):
            if( self.bot.check_bot_peer_has_option( self.peernick, "bot2bot_opennet_trades" )):
                if( self.bot.bots[ self.peernick ].has_key( "opennet_ref" ) and self.bot.bots[ self.peernick ].has_key( "opennet_ref_terminated" ) and self.bot.bots[ self.peernick ].has_key( "opennet_ref_is_good" )):
                    # NOTE: Later we may have some criterion for rejecting the request other than we don't have their opennet ref and we don't trade refs or we don't do bot2bot at all
                    self.bot.addref( "(opennet from bot: %s)" % ( self.peernick ), replyfunc, self.peernick, self.bot.bots[ self.peernick ][ "opennet_ref" ], "request" )
                    return
        self.after(random.randint(7, 20), self.bot.sendDoOpennetRefSwapDeny, self.peernick)  # After 7-20 seconds, deny their request to swap opennet refs
    
    #@-node:cmd_doopennetrefswaprequest
    #@+node:cmd_dorefswapallow
    def cmd_dorefswapallow(self, replyfunc, is_from_privmsg, args):

        # NOTE: We'll not have asked if from our perspective we didn't want to swap, but we don't want to add a darknet ref for a bot we don't think we can respond to (because they disconnected or something)
        # NOTE: Also, we don't want anybody to try to "cheat" the "negotiation" scheme
        if( self.bot.bot2bot_darknet_trades_enabled ):
            if( self.bot.check_bot_peer_has_option( self.peernick, "bot2bot_darknet_trades" )):
                if( self.bot.bots[ self.peernick ].has_key( "ref" ) and self.bot.bots[ self.peernick ].has_key( "ref_terminated" ) and self.bot.bots[ self.peernick ].has_key( "ref_is_good" )):
                    self.bot.addref( "(darknet from bot: %s)" % ( self.peernick ), replyfunc, self.peernick, self.bot.bots[ self.peernick ][ "ref" ], "allow" )
                elif( self.bot.bots[ self.peernick ].has_key( "already_added" )):
                    self.after(2, self.bot.sendDoRefSwapCompleted, self.peernick)  # After 2 seconds, tell them we've completed the swap (since we already had the peer added to the node)
    
    #@-node:cmd_dorefswapallow
    #@+node:cmd_dorefswapcompleted
    def cmd_dorefswapcompleted(self, replyfunc, is_from_privmsg, args):

        self.bot.nrefs += 1
        refs_to_go = self.bot.number_of_refs_to_collect - self.bot.nrefs
        refs_plural_str = ''
        if( refs_to_go > 1 ):
            refs_plural_str = "s"
        log("** Added darknet ref via bot2bot trade with %s (%d ref%s to go)" % ( self.peernick, refs_to_go, refs_plural_str ))
        if self.bot.nrefs >= self.bot.number_of_refs_to_collect:
            log("Got our %d refs, now terminating!" % ( self.bot.number_of_refs_to_collect ))
            self.after(3, self.bot.thankChannelThenDie)
    
    #@-node:cmd_dorefswapcompleted
    #@+node:cmd_dorefswapdeny
    def cmd_dorefswapdeny(self, replyfunc, is_from_privmsg, args):

        pass  # So nothing is going to continue from here in the current "state machine"

    #@-node:cmd_dorefswapdeny
    #@+node:cmd_dorefswapfailed
    def cmd_dorefswapfailed(self, replyfunc, is_from_privmsg, args):

        pass  # So nothing is going to continue from here in the current "state machine"

    #@-node:cmd_dorefswapfailed
    #@+node:cmd_dorefswaprequest
    def cmd_dorefswaprequest(self, replyfunc, is_from_privmsg, args):

        if( self.bot.bot2bot_darknet_trades_enabled ):
            if( self.bot.check_bot_peer_has_option( self.peernick, "bot2bot_darknet_trades" )):
                if( self.bot.bots[ self.peernick ].has_key( "ref" ) and self.bot.bots[ self.peernick ].has_key( "ref_terminated" ) and self.bot.bots[ self.peernick ].has_key( "ref_is_good" )):
                    # NOTE: Later we may have some criterion for rejecting the request other than we don't have their darknet ref and we don't trade refs or we don't do bot2bot at all
                    self.bot.addref( "(darknet from bot: %s)" % ( self.peernick ), replyfunc, self.peernick, self.bot.bots[ self.peernick ][ "ref" ], "request" )
                    return
        self.after(random.randint(7, 20), self.bot.sendDoRefSwapDeny, self.peernick)  # After 7-20 seconds, deny their request to swap darknet refs
    
    #@-node:cmd_dorefswaprequest
    #@+node:cmd_error
    def cmd_error(self, replyfunc, is_from_privmsg, args):

        pass
    
    #@-node:cmd_error
    #@+node:cmd_getannouncers
    def cmd_getannouncers(self, replyfunc, is_from_privmsg, args):
        
        if( not self.bot.bot2bot_announces_enabled ):
            replyfunc("error - Sorry, I'm not configured to do bot2bot-based cooperative announcing.")
            return
        replyfunc("The announcers I know: %s" % self.bot.botAnnouncePool)
    
    #@-node:cmd_getannouncers
    #@+node:cmd_getbots
    def cmd_getbots(self, replyfunc, is_from_privmsg, args):
        
        if( not self.bot.bot2bot_enabled ):
            replyfunc("Sorry, I'm not configured to do bot2bot communications, thus I don't know who the bots are.")
            return
        localBotList = [];
        localBotList.append( self.bot.botircnick );
        for bot in self.bot.bots:
            localBotList.append( bot );
        localBotList.sort();
        replyfunc("The bots I know: %s" % localBotList)
    
    #@-node:cmd_getbots
    #@+node:cmd_getidentity
    def cmd_getidentity(self, replyfunc, is_from_privmsg, args):
        
        self.bot.sendMyIdentity( self.peernick )
        if( 1 == len( args ) and self.bot.bots.has_key( self.peernick )):
            peerIdentity = args[ 0 ];
            if( not self.bot.botDarknetIdentities.has_key( peerIdentity )):
                self.bot.addBotIdentity( self.peernick, peerIdentity );
                log("** botDarknetIdentities: %s" % ( self.bot.botDarknetIdentities.keys() ))
                if( not self.bot.check_bot_peer_is_already_added( self.peernick )):
                    if( self.bot.bot2bot_darknet_trades_enabled ):
                        if( self.bot.check_bot_peer_has_option( self.peernick, "bot2bot_darknet_trades" )):
                            self.bot.check_identity_with_node( peerIdentity )
    
    #@-node:cmd_getidentity
    #@+node:cmd_getopennetidentity
    def cmd_getopennetidentity(self, replyfunc, is_from_privmsg, args):
        
        self.bot.sendMyOpennetIdentity( self.peernick )
        if( 1 == len( args ) and self.bot.bots.has_key( self.peernick )):
            peerIdentity = args[ 0 ];
            if( not self.bot.botOpennetIdentities.has_key( peerIdentity )):
                self.bot.addBotOpennetIdentity( self.peernick, peerIdentity );
                log("** botOpennetIdentities: %s" % ( self.bot.botOpennetIdentities.keys() ))
                if( not self.bot.check_bot_peer_is_already_added( self.peernick )):
                    if( self.bot.bot2bot_opennet_trades_enabled ):
                        if( self.bot.check_bot_peer_has_option( self.peernick, "bot2bot_opennet_trades" )):
                            self.bot.check_identity_with_node( peerIdentity )
    
    #@-node:cmd_getopennetidentity
    #@+node:cmd_getopennetref
    def cmd_getopennetref(self, replyfunc, is_from_privmsg, args):
        
        if( self.bot.bot2bot_trades_only_enabled ):
            replyfunc("Sorry, I'm configured to only trade refs with other bots and to not trade directly with humans.  Send me the \"help\" command to learn how to run your own ref swapping bot.")
            return
        if( self.bot.privmsg_only_enabled and not is_from_privmsg ):
            replyfunc("Sorry, I'm configured to trade refs with humans only using private messages.  Use the /msg command to send me a private message, after registering with nickserv if needed (i.e. /ns register <password>).")
            return
        if( not self.bot.opennet_trades_enabled ):
            if( self.bot.darknet_trades_enabled ):
                replyfunc("Sorry, I'm not configured to trade opennet refs at the moment, but I will trade darknet refs.  Try the \"getref\" command.")
            else:
                replyfunc("Sorry, I'm not configured to trade opennet refs at the moment.")
            return
        replyfunc("My ref is at %s" % self.bot.opennet_refurl)
    
    #@-node:cmd_getopennetref
    #@+node:cmd_getopennetrefdirect
    def cmd_getopennetrefdirect(self, replyfunc, is_from_privmsg, args):
        
        if( self.bot.bot2bot_trades_only_enabled and not self.bot.bots.has_key( self.peernick )):
            replyfunc("Sorry, I'm configured to only trade refs with other bots and to not trade directly with humans.  Send me the \"help\" command to learn how to run your own ref swapping bot.")
            return
        if( self.bot.privmsg_only_enabled and not is_from_privmsg ):
            replyfunc("Sorry, I'm configured to trade refs with humans only using private messages.  Use the /msg command to send me a private message, after registering with nickserv if needed (i.e. /ns register <password>).")
            return
        if( not self.bot.opennet_trades_enabled ):
            replyfunc("Sorry, I'm not configured to trade opennet refs.")
            return
        if( not self.bot.bot2bot_opennet_trades_enabled ):
            replyfunc("Sorry, I'm not configured to trade opennet refs with bots.")
            return
        self.bot.sendopennetrefdirect( self.peernick, self.bot.bots.has_key( self.peernick ));
    
    #@-node:cmd_getopennetrefdirect
    #@+node:cmd_getoptions
    def cmd_getoptions(self, replyfunc, is_from_privmsg, args):
        
        args = string.join( args, " " );
        self.bot.sendMyOptions( self.peernick )
        if( self.bot.bots.has_key( self.peernick )):
            self.bot.setPeerBotOptions( self.peernick, args );
    
    #@-node:cmd_getoptions
    #@+node:cmd_getref
    def cmd_getref(self, replyfunc, is_from_privmsg, args):
        
        if( self.bot.bot2bot_trades_only_enabled ):
            replyfunc("Sorry, I'm configured to only trade refs with other bots and to not trade directly with humans.  Send me the \"help\" command to learn how to run your own ref swapping bot.")
            return
        if( self.bot.privmsg_only_enabled and not is_from_privmsg ):
            replyfunc("Sorry, I'm configured to trade refs with humans only using private messages.  Use the /msg command to send me a private message, after registering with nickserv if needed (i.e. /ns register <password>).")
            return
        if( not self.bot.darknet_trades_enabled ):
            if( self.bot.opennet_trades_enabled ):
                replyfunc("Sorry, I'm not configured to trade darknet refs at the moment, but I will trade opennet refs.  Try the \"getopennetref\" command.")
            else:
                replyfunc("Sorry, I'm not configured to trade darknet refs at the moment.")
            return
        replyfunc("My ref is at %s" % self.bot.refurl)
    
    #@-node:cmd_getref
    #@+node:cmd_getrefdirect
    def cmd_getrefdirect(self, replyfunc, is_from_privmsg, args):
        
        if( self.bot.bot2bot_trades_only_enabled and not self.bot.bots.has_key( self.peernick )):
            replyfunc("Sorry, I'm configured to only trade refs with other bots and to not trade directly with humans.  Send me the \"help\" command to learn how to run your own ref swapping bot.")
            return
        if( self.bot.privmsg_only_enabled and not is_from_privmsg ):
            replyfunc("Sorry, I'm configured to trade refs with humans only using private messages.  Use the /msg command to send me a private message, after registering with nickserv if needed (i.e. /ns register <password>).")
            return
        if( not self.bot.darknet_trades_enabled ):
            replyfunc("Sorry, I'm not configured to trade darknet refs.")
            return
        if( not self.bot.bot2bot_darknet_trades_enabled ):
            replyfunc("Sorry, I'm not configured to trade darknet refs with bots.")
            return
        self.bot.sendrefdirect( self.peernick, self.bot.bots.has_key( self.peernick ));
    
    #@-node:cmd_getrefdirect
    #@+node:cmd_getseenchannelusers
    def cmd_getseenchannelusers(self, replyfunc, is_from_privmsg, args):
        
        self.bot.sendSeenChannelUsers( self.peernick )
    
    #@-node:cmd_getseenchannelusers
    #@+node:cmd_haveopennetpeer
    def cmd_haveopennetpeer(self, replyfunc, is_from_privmsg, args):
        if( 1 == len( args ) and self.bot.bots.has_key( self.peernick )):
            self.bot.bots[ self.peernick ][ "opennet_already_added" ] = True;
    
    #@-node:cmd_haveopennetpeer
    #@+node:cmd_haveopennetref
    def cmd_haveopennetref(self, replyfunc, is_from_privmsg, args):
        if( self.bot.bot2bot_opennet_trades_enabled ):
            if( self.bot.check_bot_peer_has_option( self.peernick, "bot2bot_opennet_trades" )):
                if( self.bot.bots[ self.peernick ].has_key( "opennet_already_added" ) or ( self.bot.bots[ self.peernick ].has_key( "opennet_ref" ) and self.bot.bots[ self.peernick ].has_key( "opennet_ref_terminated" ) and self.bot.bots[ self.peernick ].has_key( "opennet_ref_is_good" ))):
                    self.after(random.randint(7, 20), self.bot.sendDoOpennetRefSwapRequest, self.peernick)  # Ask to swap refs with them after 7-20 seconds
    
    #@-node:cmd_haveopennetref
    #@+node:cmd_havepeer
    def cmd_havepeer(self, replyfunc, is_from_privmsg, args):
        if( 1 == len( args ) and self.bot.bots.has_key( self.peernick )):
            self.bot.bots[ self.peernick ][ "already_added" ] = True;
    
    #@-node:cmd_havepeer
    #@+node:cmd_haveref
    def cmd_haveref(self, replyfunc, is_from_privmsg, args):
        if( self.bot.bot2bot_darknet_trades_enabled ):
            if( self.bot.check_bot_peer_has_option( self.peernick, "bot2bot_darknet_trades" )):
                if( self.bot.bots[ self.peernick ].has_key( "already_added" ) or ( self.bot.bots[ self.peernick ].has_key( "ref" ) and self.bot.bots[ self.peernick ].has_key( "ref_terminated" ) and self.bot.bots[ self.peernick ].has_key( "ref_is_good" ))):
                    self.after(random.randint(7, 20), self.bot.sendDoRefSwapRequest, self.peernick)  # Ask to swap refs with them after 7-20 seconds
    
    #@-node:cmd_haveref
    #@+node:cmd_help
    def cmd_help(self, replyfunc, is_from_privmsg, args):
    
        dark_open_str = "";
        if( self.bot.darknet_trades_enabled and self.bot.opennet_trades_enabled ):
            dark_open_str = "darknet and opennet";
        elif( self.bot.darknet_trades_enabled ):
            dark_open_str = "darknet";
        else:
            dark_open_str = "opennet";
        self.privmsg(
            "I am a bot for exchanging freenet %s node references (refs)" % ( dark_open_str ),
            "I am part of pyfcp.  To run your own copy of me, install pyfcp as detailed at http://wiki.freenetproject.org/Refbot and then run refbot.py",
            "If you do run your own copy of me, you'll want to run my updater.py script periodically to make sure you have my latest features and bug fixes.",
            "My version numbers are refbot.py at r%s and minibot.py at r%s" % (FreenetNodeRefBot.svnRevision, MiniBot.svnRevision),
            "Available commands:",
            "  help           - display this help",
            "  version        - display the above version information",
            "  die            - terminate me (PM from owner only)"
        )
        if( not self.bot.bot2bot_trades_only_enabled ):
            self.privmsg(
                "  addref <URL>   - add ref at <URL> to my node",
            )
        if( not self.bot.bot2bot_trades_only_enabled and self.bot.darknet_trades_enabled):
            self.privmsg(
                "  getref         - print out my own darknet ref so you can add me (assuming I already have yours)"
            )
        if( not self.bot.bot2bot_trades_only_enabled and self.bot.opennet_trades_enabled):
            self.privmsg(
                "  getopennetref  - print out my own opennet ref so you can add me (assuming I already have yours)"
            )
        self.privmsg(
            "** (end of help listing) **"
        )
    
    #@-node:cmd_help
    #@+node:cmd_hi
    def cmd_hi(self, replyfunc, is_from_privmsg, args):
    
        log("cmd_hi: %s" % str(args))
    
        self.action("waits for a bit")
    
        self.privmsg("Hi - type 'help' for help")
    
    #@-node:cmd_hi
    #@+node:cmd_identity
    def cmd_identity(self, replyfunc, is_from_privmsg, args):
    
        self.privmsg(
            "identity: %s" % (self.bot.nodeDarknetIdentity),
            )
    
    #@-node:cmd_identity
    #@+node:cmd_myidentity
    def cmd_myidentity(self, replyfunc, is_from_privmsg, args):
        
        if( 1 == len( args ) and self.bot.bots.has_key( self.peernick )):
            peerIdentity = args[ 0 ];
            if( not self.bot.botDarknetIdentities.has_key( peerIdentity )):
                self.bot.addBotIdentity( self.peernick, peerIdentity )
                log("** botDarknetIdentities: %s" % ( self.bot.botDarknetIdentities.keys() ))
                if( self.bot.bot2bot_darknet_trades_enabled ):
                    if( self.bot.check_bot_peer_has_option( self.peernick, "bot2bot_darknet_trades" )):
                        self.bot.check_identity_with_node( peerIdentity )
    
    #@-node:cmd_myidentity
    #@+node:cmd_myopennetidentity
    def cmd_myopennetidentity(self, replyfunc, is_from_privmsg, args):
        
        if( 1 == len( args ) and self.bot.bots.has_key( self.peernick )):
            peerIdentity = args[ 0 ];
            if( not self.bot.botOpennetIdentities.has_key( peerIdentity )):
                self.bot.addBotOpennetIdentity( self.peernick, peerIdentity )
                log("** botOpennetIdentities: %s" % ( self.bot.botOpennetIdentities.keys() ))
                if( self.bot.bot2bot_opennet_trades_enabled ):
                    if( self.bot.check_bot_peer_has_option( self.peernick, "bot2bot_opennet_trades" )):
                        self.bot.check_identity_with_node( peerIdentity )
    
    #@-node:cmd_myopennetidentity
    #@+node:cmd_myoptions
    def cmd_myoptions(self, replyfunc, is_from_privmsg, args):
        
        args = string.join( args, " " );
        if( self.bot.bots.has_key( self.peernick )):
            self.bot.setPeerBotOptions( self.peernick, args );
            if(self.bot.bots.has_key( self.peernick ) and not self.bot.bots[ self.peernick ].has_key( "identity" )):
                self.after(random.randint(7, 20), self.bot.sendGetIdentity, self.peernick)  # Ask for their darknet identity after 7-20 seconds
            if(self.bot.bots.has_key( self.peernick ) and not self.bot.bots[ self.peernick ].has_key( "opennet_identity" )):
                self.after(random.randint(7, 20), self.bot.sendGetOpennetIdentity, self.peernick)  # Ask for their opennet identity after 7-20 seconds
    
    #@-node:cmd_myoptions
    #@+node:cmd_myseenchannelusers
    def cmd_myseenchannelusers(self, replyfunc, is_from_privmsg, args):
        
        args = string.join( args, " " );
        if( self.bot.bots.has_key( self.peernick )):
            self.bot.addSeenChannelUsers( self.peernick, args );
    
    #@-node:cmd_myseenchannelusers
    #@+node:cmd_opennetIdentity
    def cmd_opennetIdentity(self, replyfunc, is_from_privmsg, args):
    
        self.privmsg(
            "opennetIdentity: %s" % (self.bot.nodeOpennetIdentity),
            )
    
    #@-node:cmd_opennetIdentity
    #@+node:cmd_opennetrefdirect
    def cmd_opennetrefdirect(self, replyfunc, is_from_privmsg, args):

        args = string.join( args, " " );
        if( self.bot.bots.has_key( self.peernick )):
            peerRefLine = args;
            if( not self.bot.bots[ self.peernick ].has_key( "opennet_ref" )):
                self.bot.bots[ self.peernick ][ "opennet_ref" ] = []
            self.bot.bots[ self.peernick ][ "opennet_ref" ].append( peerRefLine )
            if("end" == peerRefLine.lower()):
                # **FIXME** Perhaps a check for getting a darknet ref instead of an opennet ref
                self.bot.bots[ self.peernick ][ "opennet_ref_terminated" ] = True
                self.bot.check_opennet_ref_from_bot_and_act( self.peernick )
    
    #@-node:cmd_opennetrefdirect
    #@+node:cmd_options
    def cmd_options(self, replyfunc, is_from_privmsg, args):
    
        self.privmsg(
            "options: %s" % (self.bot.api_options),
            )
    
    #@-node:cmd_options
    #@+node:cmd_refdirect
    def cmd_refdirect(self, replyfunc, is_from_privmsg, args):

        args = string.join( args, " " );
        if( self.bot.bots.has_key( self.peernick )):
            peerRefLine = args;
            if( not self.bot.bots[ self.peernick ].has_key( "ref" )):
                self.bot.bots[ self.peernick ][ "ref" ] = []
            self.bot.bots[ self.peernick ][ "ref" ].append( peerRefLine )
            if("end" == peerRefLine.lower()):
                # **FIXME** Perhaps a check for getting a opennet ref instead of an darknet ref
                self.bot.bots[ self.peernick ][ "ref_terminated" ] = True
                self.bot.check_darknet_ref_from_bot_and_act( self.peernick )
    
    #@-node:cmd_refdirect
    #@+node:cmd_version
    def cmd_version(self, replyfunc, is_from_privmsg, args):
    
        self.privmsg(
            "version: refbot.py: r%s  minibot.py: r%s  fcp/node.py: r%s" % (FreenetNodeRefBot.svnRevision, MiniBot.svnRevision, fcp.FCPNode.svnRevision),
            )
    
    #@-node:cmd_version
    #@-others
    
    #@-node:command handlers
    #@-others

#@-node:class RefBotConversation
#@+node:class AddRef
class AddRef(threading.Thread):

    minimumFCPAddNodeBuild = 1008;

    def __init__(self, tmci_host, tmci_port, fcp_host, fcp_port, fcp_log_level, url, replyfunc, sender_irc_nick, irc_host, nodeDarknetIdentity, nodeDarknetRef, hasOpennet, nodeOpennetIdentity, nodeOpennetRef, darknet_trades_enabled, opennet_trades_enabled, peerRef, botAddType):
        threading.Thread.__init__(self)
        self.tmci_host = tmci_host
        self.tmci_port = tmci_port
        self.fcp_host = fcp_host
        self.fcp_port = fcp_port
        self.fcp_log_level = fcp_log_level
        self.url = url
        self.replyfunc = replyfunc
        self.sender_irc_nick = sender_irc_nick
        self.irc_host = irc_host
        self.nodeDarknetIdentity = nodeDarknetIdentity
        self.nodeDarknetRef = nodeDarknetRef
        self.hasOpennet = hasOpennet
        self.nodeOpennetIdentity = nodeOpennetIdentity
        self.nodeOpennetRef = nodeOpennetRef
        self.isDarknetRef = False
        self.isOpennetRef = False
        self.isTestnetRef = False
        self.darknet_trades_enabled = darknet_trades_enabled
        self.opennet_trades_enabled = opennet_trades_enabled
        self.peerRef = peerRef
        self.botAddType = botAddType
        self.status = 0
        self.error_msg = None
        self.plugin_args = { "fcp_module" : fcp, "tmci_host" : self.tmci_host, "tmci_port" : self.tmci_port, "fcp_host" : self.fcp_host, "fcp_port" : self.fcp_port, "sender_irc_nick" : self.sender_irc_nick, "irc_host" : self.irc_host, "log_function" : log, "reply_function" : self.replyfunc, "nodeIdentity" : self.nodeDarknetIdentity, "nodeRef" : self.nodeDarknetRef, "nodeOpennetIdentity" : self.nodeOpennetIdentity, "nodeOpennetRef" : self.nodeOpennetRef, "darknet_trades_enabled" : self.darknet_trades_enabled, "opennet_trades_enabled" : self.opennet_trades_enabled, "botAddType" : self.botAddType };

    def run(self):
        if( self.peerRef == None ):
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
        else:
            reflines = self.peerRef
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
        if( ref_fieldset.has_key( "testnet" ) and "true" == ref_fieldset[ "testnet" ].lower() ):
            self.isTestnetRef = True;
        if( self.isTestnetRef ):
            self.status = -8
            self.error_msg = "Bot does not currently trade testnet refs"
            return
        if( ref_fieldset.has_key( "opennet" ) and "true" == ref_fieldset[ "opennet" ].lower() ):
            self.isOpennetRef = True;
        else:
            self.isDarknetRef = True;
        if( self.isDarknetRef and not self.darknet_trades_enabled):
            self.status = -9
            self.error_msg = "Bot does not currently trade darknet refs"
            return
        if( self.isOpennetRef and not self.opennet_trades_enabled):
            self.status = -10
            self.error_msg = "Bot does not currently trade opennet refs"
            return
        self.plugin_args[ "isDarknetRef" ] = self.isDarknetRef;
        self.plugin_args[ "isOpennetRef" ] = self.isOpennetRef;
        if( self.isDarknetRef ):
            required_ref_fields = [ "dsaGroup.g", "dsaGroup.p", "dsaGroup.q", "dsaPubKey.y", "identity", "location", "myName", "sig" ];
        else:
            required_ref_fields = [ "dsaGroup.g", "dsaGroup.p", "dsaGroup.q", "dsaPubKey.y", "identity", "location", "opennet", "sig" ];
        for require_ref_field in required_ref_fields:
            if(not ref_fieldset.has_key(require_ref_field)):
                self.status = -1  # invalid ref found at URL
                self.error_msg = "No %s field in ref" % ( require_ref_field );
                return
        if( ref_fieldset[ "identity" ] == self.nodeDarknetIdentity ):
            self.status = -5
            self.error_msg = "Node already has a ref with its own identity"
            return
        if( ref_fieldset[ "identity" ] == self.nodeOpennetIdentity ):
            self.status = -5
            self.error_msg = "Node already has a ref with its own identity"
            return

        f = None;
        try:
            f = fcp.FCPNode( host = self.fcp_host, port = self.fcp_port, logfunc = log, verbosity = self.fcp_log_level )
            if( have_plugin_module ):
                try:
                    self.plugin_args[ "fcpNode" ] = f;
                    self.plugin_args[ "ref" ] = ref_fieldset;
                    plugin_result = botplugin.pre_add( self.plugin_args );
                    if( plugin_result != None ):
                        self.status = -6
                        self.error_msg = plugin_result
                        f.shutdown();
                        return
                except Exception, msg:
                    log("Got exception calling botplugin.pre_add(): %s" % ( msg ));
            returned_peer = f.listpeer( NodeIdentifier = ref_fieldset[ "identity" ] )
            if( type( returned_peer ) == type( [] )):
                returned_peer = returned_peer[ 0 ];
            if( returned_peer[ "header" ] == "Peer" ):
                self.status = -4
                self.error_msg = "Node already has a peer with that identity"
                f.shutdown();
                return
            if( f.nodeBuild < self.minimumFCPAddNodeBuild ):
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
            else:
                addpeer_result = f.addpeer( kwdict = ref_fieldset )
        except Exception, msg:
            self.status = -3
            log("?? ERROR: Uncaught Exception while adding ref:")
            log_traceback()
            self.error_msg = msg
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
                self.extended_error_msg = "Exception: type=[%s]  value=[%s]  traceback=[%s]" % ( exc_type, exc_value, reported_traceback )
            except:
                self.extended_error_msg = msg
                log("?? ERROR: Exception while generating the exception message:")
                log_traceback()
            if(f != None):
                f.shutdown();
            return  

        try:
            returned_peer = f.listpeer( NodeIdentifier = ref_fieldset[ "identity" ] )
            if( type( returned_peer ) == type( [] )):
                returned_peer = returned_peer[ 0 ];
            if( returned_peer[ "header" ] == "UnknownNodeIdentifier" ):
                self.status = -7
                self.error_msg = "Node couldn't add peer for some reason."
                f.shutdown();
                return
        except Exception, msg:
            # We'll let this part fail open for now
            pass
        if( have_plugin_module ):
            try:
                plugin_result = botplugin.post_add( self.plugin_args );
            except Exception, msg:
                log("Got exception calling botplugin.post_add(): %s" % ( msg ));
        if(self.isDarknetRef):
            try:
                if( self.peerRef == None ):
                    note_text = "%s added via refbot.py from %s@%s at %s" % ( ref_fieldset[ "myName" ], self.sender_irc_nick, self.irc_host, time.strftime( "%Y%m%d-%H%M%S", time.localtime() ) )
                else:
                    note_text = "%s bot2bot traded via refbot.py with %s@%s at %s" % ( ref_fieldset[ "myName" ], self.sender_irc_nick, self.irc_host, time.strftime( "%Y%m%d-%H%M%S", time.localtime() ) )
                encoded_note_text = base64.encodestring( note_text ).replace( "\r", "" ).replace( "\n", "" );
                f.modifypeernote( NodeIdentifier = ref_fieldset[ "identity" ], PeerNoteType = fcp.node.PEER_NOTE_PRIVATE_DARKNET_COMMENT, NoteText = encoded_note_text )
            except Exception, msg:
                # We'll just not have added a private peer note if we get an exception here
                pass
        f.shutdown();

        if(not ref_fieldset.has_key("physical.udp")):
            self.status = 2
            self.error_msg = "No physical.udp field in ref"
            return
        self.status = 1

#@-node:class AddRef
#@+node:class CheckIdentityWithNode
class CheckIdentityWithNode(threading.Thread):
    def __init__(self, fcp_host, fcp_port, fcp_log_level, identity):
        threading.Thread.__init__(self)
        self.fcp_host = fcp_host
        self.fcp_port = fcp_port
        self.fcp_log_level = fcp_log_level
        self.identity = identity
        self.status = -1
        self.status_msg = None

    def run(self):
        f = None;
        try:
          f = fcp.FCPNode( host = self.fcp_host, port = self.fcp_port, logfunc = log, verbosity = self.fcp_log_level )
          returned_peer = f.listpeer( NodeIdentifier = self.identity )
          if( type( returned_peer ) == type( [] )):
              returned_peer = returned_peer[ 0 ];
          if( returned_peer[ "header" ] == "Peer" ):
              self.status = 1
              self.status_msg = "Node already has a peer with that identity"
              f.shutdown();
              return
          self.status = 0
          self.status_msg = "Node does not yet have a peer with that identity"
          f.shutdown();
          return
        except Exception, msg:
          self.status = -1
          self.status_msg = msg
          if(f != None):
              f.shutdown();
          return  

#@-node:class CheckIdentityWithNode
#@+node:class GetPeerUpdate
class GetPeerUpdate(threading.Thread):
    def __init__(self, fcp_host, fcp_port, fcp_log_level):
        threading.Thread.__init__(self)
        self.fcp_host = fcp_host
        self.fcp_port = fcp_port
        self.fcp_log_level = fcp_log_level
        self.status = -1
        self.status_msg = None
        self.cpeers = None
        self.tpeers = None

    def run(self):
        peerUpdateCallResult = getPeerUpdateHelper( self.fcp_host, self.fcp_port, self.fcp_log_level )
        if( peerUpdateCallResult.has_key( "status" )):
            self.status = peerUpdateCallResult[ "status" ];
        if( peerUpdateCallResult.has_key( "status_msg" )):
            self.status_msg = peerUpdateCallResult[ "status_msg" ];
        if( peerUpdateCallResult.has_key( "cpeers" )):
            self.cpeers = peerUpdateCallResult[ "cpeers" ];
        if( peerUpdateCallResult.has_key( "tpeers" )):
            self.tpeers = peerUpdateCallResult[ "tpeers" ];

#@-node:class GetPeerUpdateHelper
#@+node:cidrNetToNumbers
def cidrNetToNumbers( networkstr ):
    if( networkstr == None ):
        return None;
    if( networkstr == '' ):
        return None;
    fields = string.split( networkstr, '/' );
    if( len( fields ) != 2 ):
        return None;
    return(( fields[ 0 ], int( fields[ 1 ] )));

#@-node:cidrNetToNumbers
#@+node:getGetHostmaskFromBits
def getHostmaskFromBits( bits ):
    hostmask = 0;
    for i in range( 32 - bits ):
        hostmask = hostmask << 1;
        hostmask = hostmask + 1;
    return refbot_inet_ntoa( hostmask );

#@-node:getGetHostmaskFromBits
#@+node:getGetNetmaskFromBits
def getNetmaskFromBits( bits ):
    hostmask = refbot_inet_aton( getHostmaskFromBits( bits ));
    fullmask = refbot_inet_aton( "255.255.255.255" );
    netmask = fullmask ^ hostmask;
    return refbot_inet_ntoa( netmask );

#@-node:getGetNetmaskFromBits
#@+node:getNetworkAddress
def getNetworkAddress( ip, netmask ):
    ipdottest = string.split( ip, '.' );
    if( 4 != len( ipdottest )):
        return None;
    netmaskdottest = string.split( netmask, '.' );
    if( 4 != len( netmaskdottest )):
        return None;
    ip = refbot_inet_aton( ip );
    netmask = refbot_inet_aton( netmask );
    networkaddr = ip & netmask;
    return refbot_inet_ntoa( networkaddr );

#@-node:getNetworkAddress
#@+node:getNetworkAddressFromCIDRNet
def getNetworkAddressFromCIDRNet( networkstr ):
    nums_result = cidrNetToNumbers( networkstr );
    if( None == nums_result ):
        return None;
    ( network, bits ) = nums_result;
    netmask = getNetmaskFromBits( bits );
    if( None == netmask ):
        return None;
    return getNetworkAddress( network, netmask );

#@+node:getNetworkAddressFromCIDRNet
#@+node:getPeerUpdateHelper
def getPeerUpdateHelper( fcp_host, fcp_port, fcp_log_level ):
    cpeers = 0
    tpeers = 0
    f = None;
    try:
        f = fcp.FCPNode( host = fcp_host, port = fcp_port, logfunc = log, verbosity = fcp_log_level )
        returned_peerlist = f.listpeers( WithVolatile = True )
    except Exception, msg:
        if(f != None):
            f.shutdown()
        return { "status" : -1, "status_msg" : msg, "cpeers" : None, "tpeers" : None }
    try:
        f.shutdown();
    except Exception, msg:
        pass  # Ignore a failure to end the FCP session as we've got what we want now
    if( type( returned_peerlist ) != type( [] )):
        returned_peerlist = [ returned_peerlist ];
    for peer in returned_peerlist:
        if( peer[ "header" ] != "Peer" ):
            break
        if( not peer.has_key( "volatile.status" )):
            continue;
        if( peer[ "volatile.status" ] == "CONNECTED" or peer[ "volatile.status" ] == "BACKED OFF" ):
            cpeers += 1
        tpeers += 1
    return { "status" : 0, "status_msg" : "getPeerUpdateHelper completed normally", "cpeers" : cpeers, "tpeers" : tpeers }

#@-node:getPeerUpdateHelper
def isIPInCIDRNet( ipstr, networkstr ):
  nums_result = cidrNetToNumbers( networkstr );
  if( None == nums_result ):
    return None;
  ( network, bits ) = nums_result;
  netmask = getNetmaskFromBits( bits );
  networkaddr = getNetworkAddress( network, netmask );
  ipnetworkaddr = getNetworkAddress( ipstr, netmask );
  if( ipnetworkaddr == networkaddr ):
    return 1;
  return 0;

#@+node:isProperCIDRNetwork
def isProperCIDRNetwork( networkstr ):
    dottest = string.split( networkstr, '.' );
    if( 4 != len( dottest )):
        return False;
    slashtest = string.split( networkstr, '/' );
    if( 2 < len( slashtest )):
        return False;
    nums_result = cidrNetToNumbers( networkstr );
    if( None == nums_result ):
        return False;
    ( network, bits ) = nums_result;
    fields = string.split( network, '.' );
    if( len( fields ) != 4 ):
        return False;
    netmask = getNetmaskFromBits( bits );
    networkaddr = getNetworkAddress( network, netmask );
    if( networkaddr == network ):
        return True;
    return False;

#@-node:isProperCIDRNetwork
#@+node:main
def main():

    if nargs > 0:
        cfgFile = args[0]
    else:
        cfgFile = None
    bot = FreenetNodeRefBot(cfgFile)
    bot.run()

#@-node:main
#@+node:getMaxSeenChannelUsers
def getMaxSeenChannelUsers( usersInChannelCount ):
  temp1 = usersInChannelCount * 3
  temp2 = usersInChannelCount + 100
  return max( temp1, temp2 )

#@-node:getMaxSeenChannelUsers
#@+node:readBogonFile
def readBogonFile( bogon_filename, bogon_list_adder_callback ):
    bogon_file = open( bogon_filename );
    bogon_file_entries = bogon_file.readlines();
    bogon_file.close();
    for entry in bogon_file_entries:
        #log("DEBUG: readBogonFile(): %s\n" % ( entry ));
        i = string.find( entry, '#' );
        if( i != -1 ):
            entry = entry[ :i ];
        i = string.find( entry, ';' );
        if( i != -1 ):
            entry = entry[ :i ];
        if( len( entry ) == 0 ):
            continue;
        entry = string.strip( entry );
        fields = string.split( entry );
        if( 1 < len( fields )):
            log("Error: Invalid bogon entry: %s" % ( entry ));
            continue;
        net = string.lower( fields[ 0 ] );
        netslashtest = string.split( net, '/' );
        if( 1 == len( netslashtest )):
            net = net + "/32";
        if( not isProperCIDRNetwork( net )):
            log("Warning: %s is not a proper CIDR network" % ( net ));
            log("DEBUG: %s should possibly be %s" % ( net, get_networkaddr_from_cidr_net( net )));
            continue;
        bogon_list_adder_callback( net );

#@-node:readBogonFile
#@+node:refbot_inet_aton
def refbot_inet_aton( str_in ):
    '''A Python implementation of socket.inet_aton(), which might be needed for backwards compatibilitywith older versions of Python'''

    fields = string.split( str_in, "." );
    if( len( fields ) != 4 ):
        return None;
    #log("DEBUG: fields: %s" % ( fields ));
    fields2 = [];
    for item in fields:
        fields2.append( int( item ));
    #log("DEBUG: fields2: %s" % ( fields2 ));
    str = struct.pack( ">BBBB", fields2[ 0 ], fields2[ 1 ], fields2[ 2 ], fields2[ 3 ] );
    str2 = struct.unpack( ">L", str );
    return str2[ 0 ];

#@-node:refbot_inet_aton
#@+node:refbot_inet_ntoa
def refbot_inet_ntoa( num_in ):
    '''A Python implementation of socket.inet_ntoa(), which might be needed for backwards compatibilitywith older versions of Python'''

    str = struct.pack( ">L", num_in );
    str2 = struct.unpack( ">BBBB", str );
    return "%d.%d.%d.%d" % ( str2[ 0 ], str2[ 1 ], str2[ 2 ], str2[ 3 ] );

#@-node:refbot_inet_ntoa
#@+node:sortByHostmaskCompareFunction
def sortByHostmaskCompareFunction( a, b ):
  #print "DEBUG: sbhcf:", a, b;
  ( a_network, a_bits ) = cidrNetToNumbers( a );
  ( b_network, b_bits ) = cidrNetToNumbers( b );
  if( a_bits < b_bits ):
    return -1;
  if( a_bits > b_bits ):
    return 1;
  if( a_network < b_network ):
    return -1;
  if( a_network > b_network ):
    return 1;
  return 0;

#@-node:sortByHostmaskCompareFunction
#@+node:mainline
if __name__ == '__main__':
    main()

#@-node:mainline
#@-others
#@-node:@file refbot.py
#@-leo
