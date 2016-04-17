#!/usr/bin/env python2
# encoding: utf-8

"""Implementation of Freenet Commmunication Primitives"""


import sys
import argparse # commandline arguments
import cmd # interactive shell
import fcp
import random
import threading # TODO: replace by futures once we have Python3
import logging
import functools

slowtests = False


# first, parse commandline arguments
def parse_args():
    """Parse commandline arguments."""
    parser = argparse.ArgumentParser(description="Implementation of Freenet Communication Primitives")
    parser.add_argument('-u', '--user', default=None, help="Identity to use (default: create new)")
    parser.add_argument('--host', default=None, help="Freenet host address (default: 127.0.0.1)")
    parser.add_argument('--port', default=None, help="Freenet FCP port (default: 9481)")
    parser.add_argument('--verbosity', default=None, help="Set verbosity (default: 3, to FCP calls: 5)")
    parser.add_argument('--test', default=False, action="store_true", help="Run the tests")
    parser.add_argument('--slowtests', default=False, action="store_true", help="Run slow tests, many of them with actual network operation in Freenet")
    args = parser.parse_args()
    return args


def withprogress(func):
    @functools.wraps(func)
    def fun(*args, **kwds):
        def waiting():
            sys.stderr.write(".")
            sys.stderr.flush()
        tasks = []
        for i in range(1200):
            tasks.append(threading.Timer(i, waiting))
        [i.start() for i in tasks]
        res = func(*args, **kwds)
        [i.cancel() for i in tasks]
        sys.stderr.write("\n")
        sys.stderr.flush()
        return res

    return fun


# then add interactive usage, since this will be a communication tool
class Babcom(cmd.Cmd):
    prompt = "--> "
    # TODO: change to "!5> " for 5 messages which can then be checked
    #       with the command read.
    username = None
    identity = None
    #: seed identity keys for initial visibility. This is currently BabcomTest. They need to be maintained: a daemon needs to actually check their CAPTCHA queue and update the trust, and a human needs to check whether what they post is spam or not.
    seedkeys = [
        ("USK@fVzf7fg0Va7vNTZZQNKMCDGo6-FSxzF3PhthcXKRRvA,"
         "~JBPb2wjAfP68F1PVriphItLMzioBP9V9BnN59mYb0o,"
         "AQACAAE/WebOfTrust/12"),
    ]
    seedtrust = 100
    # iterators which either return a CAPTCHA or None.
    captchaiters = []

    def preloop(self):
        if self.username is None:
            self.username = randomname()
            print "No user given."
            print "Generating random identity with name", self.username, "Please wait..."
        else:
            print "Retrieving identity information from Freenet using name", self.username + ". Please wait ..."

        matches = myidentity(self.username)
        print "... retrieved", len(matches) ,"identities matching", self.username
        if matches[1:]:
            choice = None
            print "more than one identity with name", self.username, "please select one."
            while choice is None:
                for i in range(len(matches)):
                    print i+1, matches[i][0]+"@"+matches[i][1]["Identity"]
                res = raw_input("Insert the number of the identity to use (1 to " + str(len(matches)) + "): ")
                try:
                    choice = int(res)
                except ValueError:
                    print "not a number"
                if choice < 1 or len(matches) < choice:
                    choice = None
                    print "the number is not in the range", str(i+1), "to", str(len(matches))
            self.username = matches[choice - 1][0]
            self.identity = matches[choice - 1][1]["Identity"]
        else:
            self.username = matches[0][0]
            self.identity = matches[0][1]["Identity"]
        
        print "Logged in as", self.username + "@" + self.identity
        print
    
    def do_intro(self, *args):
        "Introduce Babcom"
        print """It began in the Earth year 2016, with the founding of the first of
the Babcom systems, located deep in decentralized space. It was a
port of call for journalists, writers, hackers, activists . . . and
travelers from a hundred worlds. Could be a dangerous place – but we
accepted the risk, because Babcom 1 was societies next, best hope for
freedom.
— Tribute to Babylon 5, where humanity learned to forge its own path.

Type help or help <command> to learn how to use babcom.
"""
    # for testing: 
    # announce USK@FpcnriKy19ztmHhg0QzTJjGwEJJ0kG7xgLiOvKXC7JE,CIpXjQej5StQRC8LUZnu3nvvh1l9UbZMinyFQyLSdMY,AQACAAE/WebOfTrust/0
    # announce USK@0kq3fHCn12-93PSV4kk56B~beIkh-XfjennLapmmapM,9hQr66rxc9O5ptdmfhMk37h2vZGrsE6NYXcFDMGMiTw,AQACAAE/WebOfTrust/1
    # announce USK@0kq3fHCn12-93PSV4kk56B~beIkh-XfjennLapmmapM,9hQr66rxc9O5ptdmfhMk37h2vZGrsE6NYXcFDMGMiTw,AQACAAE/WebOfTrust/1
    # announce USK@FZynnK5Ngi6yTkBAZXGbdRLHVPvQbd2poW6DmZT8vbs,bcPW8yREf-66Wfh09yvx-WUt5mJkhGk5a2NFvbCUDsA,AQACAAE/WebOfTrust/1
    # announce USK@B324z0kMF27IjNEVqn6oRJPJohAP2NRZDFhQngZ1GOI,DRf8JZviHLIFOYOdu42GLL2tDhVaWb6ihdNO18DkTpc,AQACAAE/WebOfTrust/0

        
    def do_announce(self, *args):
        """Announce your own ID. Usage announce [<id key> ...]."""
        usingseeds = args[0] == ""
        if usingseeds and self.captchaiters:
            for captchaiter in self.captchaiters[:]:
                try:
                    captchas = captchaiter.next()
                except StopIteration: # captchaiter is finished, nothing more to gain
                    self.captchhaiters.remove(captchaiter)
                else:
                    if captchas is not None:
                        print captchas
            return

        if usingseeds:
            ids = [i.split("@")[1].split(",")[0] for i in self.seedkeys]
            keys = self.seedkeys
            trustifmissing = self.seedtrust
            commentifmissing = "Automatically assigned trust to a seed identity."
        else:
            ids = [i.split("@")[1].split(",")[0] for i in args[0].split()]
            keys = args[0].split()
            trustifmissing = 0
            commentifmissing = "babcom announce"

        # store the iterator. If the first 
        captchaiter = prepareannounce(ids, keys, self.identity, trustifmissing, commentifmissing)
        try:
            captchas = captchaiter.next()
        except StopIteration:
            pass # iteration finished
        else:
            self.captchaiters.append(captchaiter)
            if captchas is not None:
                print captchas
        
        
    def do_hello(self, *args):
        """Says Hello. Usage: hello [<name>]"""
        name = args[0] if args else 'World'
        print "Hello {}".format(name)

    def do_quit(self, *args):
        "Leaves the program"
        raise SystemExit

    def do_EOF(self, *args):
        "Leaves the program. Commonly called via CTRL-D"
        raise SystemExit

    def emptyline(self, *args):
        "What is done for an empty line"
        print "Type help and hit enter to get help"


class ProtocolError(Exception):
    """
    Did not get the expected reply.
    """
    

def _parse_name(wot_identifier):
    """
    Parse identifier of the forms: nick
                                   nick@key
                                   @key
    :Return: nick, key. If a part is not given return an empty string for it.
    
    >>> _parse_name("BabcomTest@123")
    ('BabcomTest', '123')
    """
    split = wot_identifier.split('@', 1)
    nickname_prefix = split[0]
    key_prefix = (split[1] if split[1:] else '')
    return nickname_prefix, key_prefix


@withprogress
def wotmessage(messagetype, **params):
    """Send a message to the Web of Trust plugin

    >>> name = wotmessage("RandomName")["Replies.Name"]
    """
    params["Message"] = messagetype
    def sendmessage(params):
        with fcp.FCPNode() as n:
            return n.fcpPluginMessage(plugin_name="plugins.WebOfTrust.WebOfTrust",
                                      plugin_params=params)[0]
    try:
        resp = sendmessage(params)
    except fcp.FCPProtocolError as e:
        if str(e) == "ProtocolError;No such plugin":
            logging.warn("Plugin Web Of Trust not loaded. Trying to load it.")
            with fcp.FCPNode() as n:
                jobid = n._getUniqueId()
                resp = n._submitCmd(jobid, "LoadPlugin",
                                    PluginURL="WebOfTrust",
                                    URLType="official",
                                    OfficialSource="freenet")[0]
                print resp
            resp = sendmessage(params)
        else: raise
    return resp


def randomname():
    return wotmessage("RandomName")["Replies.Name"]
        

def createidentity(name="BabcomTest"):
    """Create a new Web of Trust identity.

    >>> name = "BabcomTest"
    >>> if slowtests:
    ...     createidentity(name)
    ... else: name
    'BabcomTest'
    
    :returns: the name of the identity created.
    """
    if not name:
        name = wotmessage("RandomName")["Name"]
    resp = wotmessage("CreateIdentity", Nickname=name, Context="babcom", # context cannot be empty
                      PublishTrustList="true", # must use string "true"
                      PublishIntroductionPuzzles="true")
    if resp['header'] != 'FCPPluginReply' or resp.get('Replies.Message', "") != 'IdentityCreated':
        raise ProtocolError(resp)
    return name


def parseownidentitiesresponse(response):
    """Parse the response to Get OwnIdentities from the WoT plugin.

    :returns: [(name, {InsertURI: ..., ...}), ...]

    >>> parseownidentitiesresponse({'Replies.Nickname0': 'FAKE', 'Replies.RequestURI0': 'USK@...', 'Replies.InsertURI0': 'USK@...', 'Replies.Identity0': 'fVzf7fg0Va7vNTZZQNKMCDGo6-FSxzF3PhthcXKRRvA', 'Replies.Message': 'OwnIdentities', 'Success': 'true', 'header': 'FCPPluginReply', 'Replies.Properties0.Property0.Name': 'fake', 'Replies.Properties0.Property0.Value': 'true'})
    [('FAKE', {'Contexts': [], 'RequestURI': 'USK@...', 'id_num': '0', 'InsertURI': 'USK@...', 'Properties': {'fake': 'true'}, 'Identity': 'fVzf7fg0Va7vNTZZQNKMCDGo6-FSxzF3PhthcXKRRvA'})]
    """
    field = "Replies.Nickname"
    identities = []
    for i in response:
        if i.startswith(field):
            # format: Replies.Nickname<id_num>
            id_num = i[len(field):]
            nickname = response[i]
            pubkey_hash = response['Replies.Identity{}'.format(id_num)]
            request = response['Replies.RequestURI{}'.format(id_num)]
            insert = response['Replies.InsertURI{}'.format(id_num)]
            contexts = [response[j] for j in response if j.startswith("Replies.Contexts{}.Context".format(id_num))]
            property_keys_keys = [j for j in sorted(response.keys())
                                  if (j.startswith("Replies.Properties{}.Property".format(id_num))
                                      and j.endswith(".Name"))]
            property_value_keys = [j for j in sorted(response.keys())
                                   if (j.startswith("Replies.Properties{}.Property".format(id_num))
                                       and j.endswith(".Value"))]
            properties = dict((response[j], response[k]) for j,k in zip(property_keys_keys, property_value_keys))
            identities.append((nickname, {"id_num": id_num, "Identity":
                                          pubkey_hash, "RequestURI": request, "InsertURI": insert,
                                          "Contexts": contexts, "Properties": properties}))
    return identities


def parseidentityresponse(response):
    """Parse the response to Get OwnIdentities from the WoT plugin.

    :returns: [(name, {InsertURI: ..., ...}), ...]

    >>> resp = {'Replies.Identity': 'jFEicE8bMY0pBN4x6VaN8PsCW342VuuTr0hAc0t39Ls', 'Replies.Identities.0.CurrentEditionFetchState': 'Fetched', 'Replies.Identities.0.Property0.Name': 'IntroductionPuzzleCount', 'Replies.Property0.Value': 10, 'Replies.Rank': 'null', 'Replies.Identities.0.Contexts.0.Name': 'babcom', 'Replies.Identities.0.Property0.Value': 10, 'Replies.Properties0.Property0.Name': 'IntroductionPuzzleCount', 'header': 'FCPPluginReply', 'Replies.Type': 'OwnIdentity', 'Replies.Identities.0.Nickname': 'BabcomTest_other', 'Replies.ID': 'jFEicE8bMY0pBN4x6VaN8PsCW342VuuTr0hAc0t39Ls', 'Replies.Identities.0.Type': 'OwnIdentity', 'Replies.Message': 'Identity', 'Replies.Contexts0.Amount': 2, 'Replies.Identity0': 'jFEicE8bMY0pBN4x6VaN8PsCW342VuuTr0hAc0t39Ls', 'Replies.Identities.Amount': 1, 'Replies.Scores.0.Value': 'Nonexistent', 'Replies.PublishesTrustList0': 'true', 'Replies.RequestURI': 'USK@jFEicE8bMY0pBN4x6VaN8PsCW342VuuTr0hAc0t39Ls,-6yAY9Qq2YildfGRFikIsWQf6RDzPAc84q-gPcbXR7o,AQACAAE/WebOfTrust/1', 'Replies.VersionID': 'a60e2f40-d5e0-4069-8297-05ce8819d817', 'Replies.ID0': 'jFEicE8bMY0pBN4x6VaN8PsCW342VuuTr0hAc0t39Ls', 'Replies.Score0': 'null', 'Replies.CurrentEditionFetchState0': 'Fetched', 'Replies.Contexts0.Context1': 'Introduction', 'Replies.Rank0': 'null', 'Replies.Identities.0.PublishesTrustList': 'true', 'Replies.Contexts.1.Name': 'Introduction', 'Replies.Properties0.Amount': 1, 'Replies.Trust0': 'null', 'Replies.Nickname': 'BabcomTest_other', 'Replies.Identities.0.Properties.0.Value': 10, 'Replies.Properties.0.Value': 10, 'Replies.Score': 'null', 'Replies.Trusts.0.Value': 'Nonexistent', 'Replies.Identities.0.VersionID': '118044f9-0ee8-4986-b798-d0645779ac1b', 'Replies.Properties.0.Name': 'IntroductionPuzzleCount', 'Replies.Context1': 'Introduction', 'Replies.Context0': 'babcom', 'Success': 'true', 'Replies.VersionID0': '84e4aba7-ebfe-4ee6-884f-ea7275decc7b', 'Replies.CurrentEditionFetchState': 'Fetched', 'Replies.Contexts.Amount': 2, 'Replies.Contexts0.Context0': 'babcom', 'Replies.Identities.0.Contexts.1.Name': 'Introduction', 'Replies.Trust': 'null', 'Replies.Properties0.Property0.Value': 10, 'Replies.PublishesTrustList': 'true', 'Identifier': 'id2342652746084203', 'Replies.Nickname0': 'BabcomTest_other', 'Replies.Property0.Name': 'IntroductionPuzzleCount', 'Replies.Contexts.0.Name': 'babcom', 'Replies.Type0': 'OwnIdentity', 'Replies.Properties.Amount': 1, 'Replies.Identities.0.ID': 'jFEicE8bMY0pBN4x6VaN8PsCW342VuuTr0hAc0t39Ls', 'PluginName': 'plugins.WebOfTrust.WebOfTrust', 'Replies.Identities.0.Identity': 'jFEicE8bMY0pBN4x6VaN8PsCW342VuuTr0hAc0t39Ls', 'Replies.Identities.0.RequestURI': 'USK@jFEicE8bMY0pBN4x6VaN8PsCW342VuuTr0hAc0t39Ls,-6yAY9Qq2YildfGRFikIsWQf6RDzPAc84q-gPcbXR7o,AQACAAE/WebOfTrust/1', 'Replies.Identities.0.Context0': 'babcom', 'Replies.Identities.0.Context1': 'Introduction', 'Replies.Identities.0.Properties.0.Name': 'IntroductionPuzzleCount', 'Replies.Identities.0.Contexts.Amount': 2, 'Replies.Identities.0.Properties.Amount': 1, 'Replies.RequestURI0': 'USK@jFEicE8bMY0pBN4x6VaN8PsCW342VuuTr0hAc0t39Ls,-6yAY9Qq2YildfGRFikIsWQf6RDzPAc84q-gPcbXR7o,AQACAAE/WebOfTrust/1'}
    >>> name, info = parseidentityresponse(resp)
    >>> name
    'BabcomTest_other'
    >>> info['RequestURI'].split(",")[-1]
    'AQACAAE/WebOfTrust/1'
    >>> info.keys()
    ['Contexts', 'RequestURI', 'CurrentEditionFetchState', 'Properties', 'Identity']
    """
    fetchedstate = response["Replies.CurrentEditionFetchState"]
    if fetchedstate != "NotFetched":
        nickname = response["Replies.Nickname"]
    else:
        nickname = None
    pubkey_hash = response['Replies.Identity']
    request = response['Replies.RequestURI']
    contexts = [response[j] for j in response if j.startswith("Replies.Contexts.Context")]
    property_keys_keys = [j for j in sorted(response.keys())
                          if (j.startswith("Replies.Properties")
                              and j.endswith(".Name"))]
    property_value_keys = [j for j in sorted(response.keys())
                           if (j.startswith("Replies.Properties")
                               and j.endswith(".Value"))]
    properties = dict((response[j], response[k]) for j,k in zip(property_keys_keys, property_value_keys))
    info = {"Identity": pubkey_hash, "RequestURI": request,
            "Contexts": contexts, "Properties": properties,
            "CurrentEditionFetchState": fetchedstate}
    return nickname, info


def _requestallownidentities():
    """Get all own identities.

    >>> resp = _requestallownidentities()
    >>> name, info = _matchingidentities("BabcomTest", resp)[0]
    """
    with fcp.FCPNode() as n:
        resp = wotmessage("GetOwnIdentities")
    if resp['header'] != 'FCPPluginReply' or resp.get('Replies.Message', '') != 'OwnIdentities':
        raise ProtocolError(resp)
    return resp

    
def _matchingidentities(prefix, response):
    """Find matching identities in a Web of Trust Plugin response.

    >>> _matchingidentities("BabcomTest", {})
    []
    """
    identities = parseownidentitiesresponse(response)
    nickname_prefix, key_prefix = _parse_name(prefix)
    matches =  [(name, info) for name,info in identities
                if (info["Identity"].startswith(key_prefix) and
                    name.startswith(nickname_prefix))]
    # sort the matches by smallest difference to the prefix so that an
    # exact match of the nickname always wins against longer names.
    return sorted(matches, key=lambda match: len(match[0]) - len(nickname_prefix))


def getownidentities(user):
    """Get all own identities which match user."""
    resp = _requestallownidentities()
    return _matchingidentities(user, resp)


def myidentity(user=None):
    """Get an identity from the Web of Trust plugin.

    :param user: Name of the Identity, optionally with additional
                 prefix of the key to disambiguate it.

    If there are multiple IDs matching the name, the user has to
    disambiguate them by selecting one or by adding parts of the
    identity key to the name.

    :returns: [(name, info), ...]
    
    >>> matches = myidentity("BabcomTest")
    >>> matches[0][0]
    'BabcomTest'

    """
    if user is None:
        user = createidentity()
    matches = getownidentities(user)
    if not matches:
        createidentity(user)
        matches = getownidentities(user)
        
    return matches


def getidentity(identity, truster):
    """Get all own identities which match user.

    >>> othername = "BabcomTest_other"
    >>> if slowtests:
    ...     matches = myidentity("BabcomTest")
    ...     name, info = matches[0]
    ...     truster = info["Identity"]
    ...     matches = myidentity(othername)
    ...     name, info = matches[0]
    ...     identity = info["Identity"]
    ...     name, info = getidentity(identity, truster)
    ...     name
    ... else: othername
    'BabcomTest_other'
    """
    with fcp.FCPNode() as n:
        resp = wotmessage("GetIdentity",
                          Identity=identity, Truster=truster)
    if resp['header'] != 'FCPPluginReply' or resp.get('Replies.Message', '') != 'Identity':
        raise ProtocolError(resp)

    name, info = parseidentityresponse(resp)
    return name, info


def addcontext(identity, context):
    """Add a context to an identity to show others that it supports a certain service.

    >>> matches = myidentity("BabcomTest")
    >>> name, info = matches[0]
    >>> identity = info["Identity"]
    >>> addcontext(identity, "testadd")
    >>> matches = myidentity(name)
    >>> info = matches[0][1]
    >>> "testadd" in info["Contexts"]
    True
    """
    with fcp.FCPNode() as n:
        resp = wotmessage("AddContext",
                          Identity=identity,
                          Context=context)
    if resp['header'] != 'FCPPluginReply' or resp.get('Replies.Message', '') != 'ContextAdded':
        raise ProtocolError(resp)
    

def removecontext(identity, context):
    """Add a context to an identity to show others that it supports a certain service.

    >>> matches = myidentity("BabcomTest")
    >>> name, info = matches[0]
    >>> identity = info["Identity"]
    >>> addcontext(identity, "testremove")
    >>> removecontext(identity, "testremove")
    >>> removecontext(identity, "testadd")
    """
    with fcp.FCPNode() as n:
        resp = wotmessage("RemoveContext",
                          Identity=identity,
                          Context=context)
    if resp['header'] != 'FCPPluginReply' or resp.get('Replies.Message', '') != 'ContextRemoved':
        raise ProtocolError(resp)
    

def ssktousk(ssk, foldername):
    """Convert an SSK to a USK.

    >>> ssktousk("SSK@pAOgyTDft8bipMTWwoHk1hJ1lhWDvHP3SILOtD1e444,Wpx6ypjoFrsy6sC9k6BVqw-qVu8fgyXmxikGM4Fygzw,AQACAAE/", "folder")
    'USK@pAOgyTDft8bipMTWwoHk1hJ1lhWDvHP3SILOtD1e444,Wpx6ypjoFrsy6sC9k6BVqw-qVu8fgyXmxikGM4Fygzw,AQACAAE/folder/0'
    """
    return "".join(("U", ssk[1:].split("/")[0],
                    "/", foldername, "/0"))


@withprogress
def fastput(private, data, node=None):
    """Upload a small amount of data as fast as possible.

    >>> with fcp.FCPNode() as n:
    ...    pub, priv = n.genkey(name="hello.txt")
    >>> if slowtests:
    ...     pubtoo = fastput(priv, "Hello Friend!")
    >>> with fcp.FCPNode() as n:
    ...    pub, priv = n.genkey()
    ...    insertusk = ssktousk(priv, "folder")
    ...    data = "Hello USK"
    ...    if slowtests:
    ...        pub = fastput(insertusk, data, node=n)
    ...        dat = fastget(pub)[1]
    ...    else: 
    ...        pub = "something,AQACAAE/folder/0"
    ...        dat = data
    ...    pub.split(",")[-1], dat
    ('AQACAAE/folder/0', 'Hello USK')
    """
    if node is None:
        with fcp.FCPNode() as node:
            return node.put(uri=private, data=data,
                            mimetype="application/octet-stream",
                            realtime=True, priority=1)
    return node.put(uri=private, data=data,
                    mimetype="application/octet-stream",
                    realtime=True, priority=1)


@withprogress
def fastget(public, node=None):
    """Download a small amount of data as fast as possible.

    :param public: the (public) key of the data to fetch.

    :returns: the data the key references.

    Note: only use this for small files. For large files it is slower
    than regular node.get() and might block other usage of the node.

    >>> with fcp.FCPNode() as n:
    ...    pub, priv = n.genkey(name="hello.txt")
    ...    data = "Hello Friend!"
    ...    if slowtests:
    ...        pubkey = fastput(priv, data, node=n)
    ...        fastget(pub, node=n)[1]
    ...    else: data
    'Hello Friend!'

    """
    def n():
        if node is None:
            return fcp.FCPNode()
        return node
    with n() as node:
        return node.get(public,
                        realtime=True, priority=1,
                        followRedirect=True)


def getinsertkey(identity):
    """Get the insert key of the given identity.

    >>> matches = myidentity("BabcomTest")
    >>> name, info = matches[0]
    >>> identity = info["Identity"]
    >>> insertkey = getinsertkey(identity)
    >>> insertkey.split("/")[0].split(",")[-1]
    'AQECAAE'
    """
    resp = _requestallownidentities()
    identities = parseownidentitiesresponse(resp)
    insertkeys = [info["InsertURI"]
                  for name,info in identities
                  if info["Identity"] == identity]
    if insertkeys[1:]:
        raise ProtocolError(
            "More than one insert key for the same identity: {}".format(
                insertkeys))
    return insertkeys[0]


def getrequestkey(identity):
    """Get the insert key of the given identity.

    >>> matches = myidentity("BabcomTest")
    >>> name, info = matches[0]
    >>> identity = info["Identity"]
    >>> insertkey = getinsertkey(identity)
    >>> insertkey.split("/")[0].split(",")[-1]
    'AQECAAE'
    """
    resp = _requestallownidentities()
    identities = parseownidentitiesresponse(resp)
    requestkeys = [info["RequestURI"]
                   for name,info in identities
                   if info["Identity"] == identity]
    if requestkeys[1:]:
        raise ProtocolError(
            "More than one request key for the same identity: {}".format(
                requestkeys))
    return requestkeys[0]


def createcaptchas(number=10, seed=None):
    """Create text captchas

    >>> createcaptchas(number=1, seed=42)
    [('KSK@hBQM_njuE_XBMb_? with 10 plus 32 = ?', 'hBQM_njuE_XBMb_42')]
    
    :returns: [(captchatext, solution), ...]
    """
    # prepare the random number generator for reproducible tests.
    random.seed(seed)
    
    def plus(x, y):
        "KSK@{2}? with {0} plus {1} = ?"
        return x + y
        
    def minus(x, y):
        "KSK@{2}? with {0} minus {1} = ?"
        return x - y
        
    def plusequals(x, y):
        "KSK@{2}? with {0} plus ? = {1}"
        return y - x
        
    def minusequals(x, y):
        "KSK@{2}? with {0} minus ? = {1}"
        return x + y
        
    questions = [plus, minus,
                 plusequals,
                 minusequals]

    captchas = []
    
    def fourletters():
        return [random.choice("ABCDEFHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
                for i in range(4)]
    
    def secret():
        return "".join(fourletters() + ["_"] +
                       fourletters() + ["_"] +
                       fourletters() + ["_"])
    
    for i in range(number):
        sec = secret()
        question = random.choice(questions)
        x = random.randint(1, 49)
        y = random.randint(1, 49)
        captcha = question.__doc__.format(x, y, sec)
        solution = sec + str(question(x, y))
        captchas.append((captcha, solution))

    return captchas


def insertcaptchas(identity):
    """Insert a list of CAPTCHAs.

    >>> matches = myidentity("BabcomTest")
    >>> name, info = matches[0]
    >>> identity = info["Identity"]
    >>> if slowtests:
    ...     usk, solutions = insertcaptchas(identity)
    ...     solutions[0][:4]
    ... else: "KSK@"
    'KSK@'

    :returns: captchasuri, ["KSK@solution", ...]
    """
    insertkey = getinsertkey(identity)
    captchas = createcaptchas()
    captchasdata = "\n".join(captcha for captcha,solution in captchas)
    captchasolutions = [solution for captcha,solution in captchas]
    captchausk = ssktousk(insertkey, "babcomcaptchas")
    with fcp.FCPNode() as n:
        pub = fastput(captchausk, captchasdata, node=n)
    return pub, ["KSK@" + solution
                 for solution in captchasolutions]
    

def announcecaptchas(identity):
    """Provide a link to the CAPTCHA queue as property of the identity.

    >>> matches = myidentity("BabcomTest")
    >>> name, info = matches[0]
    >>> identity = info["Identity"]
    >>> if slowtests:
    ...     solutions = announcecaptchas(identity)
    ...     matches = myidentity("BabcomTest")
    ...     name, info = matches[0]
    ...     "babcomcaptchas" in info["Properties"]
    ... else: True
    True
    
    :returns: ["KSK@...", ...] # the solutions to watch
    """
    pubusk, solutions = insertcaptchas(identity)
    resp = wotmessage("SetProperty", Identity=identity,
                      Property="babcomcaptchas",
                      Value=pubusk)
    if resp['header'] != 'FCPPluginReply' or resp.get('Replies.Message', "") != 'PropertyAdded':
        raise ProtocolError(resp)

    return solutions


def _captchasolutiontokey(captcha, solution):
    """Turn the CAPTCHA and its solution into a key.
    
    >>> captcha = 'KSK@hBQM_njuE_XBMb_? with 10 plus 32 = ?'
    >>> solution = '42'
    >>> _captchasolutiontokey(captcha, solution)
    'KSK@hBQM_njuE_XBMb_42'
    """
    secret = captcha.split("?")[0]
    return secret + str(solution)
    

def solvecaptcha(captcha, identity, solution):
    """Use the solution to solve the CAPTCHA.

    >>> captcha = 'KSK@hBQM_njuE_XBMb_? with 10 plus 32 = ?'
    >>> solution = '42'
    >>> matches = myidentity("BabcomTest")
    >>> name, info = matches[0]
    >>> identity = info["Identity"]
    >>> idrequestkey = getrequestkey(identity)
    >>> captchakey = _captchasolutiontokey(captcha, solution)
    >>> if slowtests:
    ...     solvecaptcha(captcha, identity, solution)
    ...     idrequestkey == fastget(captchakey)[1]
    ... else: True
    True
    """
    captchakey = _captchasolutiontokey(captcha, solution)
    idkey = getrequestkey(identity)
    with fcp.FCPNode() as n:
        fastput(captchakey, idkey, node=n)


def gettrust(truster, trustee):
    """Set trust to an identity.

    >>> my = myidentity("BabcomTest")[0][1]["Identity"]
    >>> other = myidentity("BabcomTest_other")[0][1]["Identity"]
    >>> gettrust(my, other)
    'Nonexistent'
    """
    resp = wotmessage("GetTrust",
                      Truster=truster, Trustee=trustee)
    if resp['header'] != 'FCPPluginReply' or resp.get('Replies.Message', "") != 'Trust':
        raise ProtocolError(resp)
    return resp['Replies.Trusts.0.Value']


def settrust(myidentity, otheridentity, trust, comment):
    """Set trust to an identity.

    :param trust: -100..100. 
                  -100 to -2: report as spammer, do not download.
                  -1: do not download.
                   0: download and show.
                   1 to 100: download, show and mark as non-spammer so
                       others download the identity, too.
    """
    resp = wotmessage("SetTrust",
                      Truster=myidentity, Trustee=otheridentity,
                      Value=str(trust), Comment=comment)
    if resp['header'] != 'FCPPluginReply' or resp.get('Replies.Message', "") != 'TrustSet':
        raise ProtocolError(resp)


def addidentity(requesturi):
    """Ensure that WoT knows the given identity."""
    resp = wotmessage("AddIdentity",
                      RequestURI=requesturi)
    if resp['header'] != 'FCPPluginReply' or resp.get('Replies.Message', "") != 'IdentityAdded':
        raise ProtocolError(resp)


def watchcaptchas(solutions):
    """Watch the solutions to the CAPTCHAs
    
    :param solutions: Freenet Keys where others can upload solved CAPTCHAs. 
    
    Just call watcher = watchcaptchas(solutions), then you can ask
    watcher whether there’s a solution via watcher.next(). It should
    return after roughly 10ms, either with None or with (key, data)
    
    :returns: generator which yields None or (key, data).
              <generator with ('KSK@...<captchakey>', 'USK@...<identity>')...>

    >>> d1 = "Test"
    >>> d2 = "Test2"
    >>> k1 = "KSK@tcshrietshcrietsnhcrie-Test"
    >>> k2 = "KSK@tcshrietshcrietsnhcrie-Test2"
    >>> if slowtests or True:
    ...     k1res = fastput(k1, d1)
    ...     k2res = fastput(k2, d2)
    ...     watcher = watchcaptchas([k1,k2])
    ...     [i for i in watcher if i is not None] # drain watcher.
    ...     # note: I cannot use i.next() in the doctest, else I’d get "I/O operation on closed file"
    ... else:
    ...     [(k1, d1), (k2, d2)]
    [('KSK@tcshrietshcrietsnhcrie-Test', 'Test'), ('KSK@tcshrietshcrietsnhcrie-Test2', 'Test2')]

    """
    # TODO: in Python3 this could be replaced with less than half the lines using futures.
    lock = threading.Lock()
    
    def gettolist(key, results):
        """Append the key and data from the key to the results."""
        res = fastget(key)
        with lock:
            results.append((key, res[1]))
    
    threads = []
    results = []
    for i in solutions:
        thread = threading.Thread(target=gettolist, args=(i, results))
        thread.start()
        threads.append(thread)
    while threads:
        for thread in threads[:]:
            if not thread.is_alive():
                thread.join()
                threads.remove(thread)
            else:
                # found at least one running get, give it 10ms
                thread.join(0.01)
                break
        if threads:
            for r in results[:]:
                results.remove(r)
                yield r
            else:   # no CAPTCHA solved yet. This moves all
                    # threading requirements into this function.
                yield None


def prepareannounce(identities, requesturis, ownidentity, trustifmissing, commentifmissing):
    """Prepare announcing to the identities.

    This ensures that the identity is known to WoT, gives it trust to
    ensure that it will be fetched, pre-fetches the ID and fetches the
    captchas. It returns an iterator which yields either a captcha to
    solve or None.
    """
    # ensure that we have a real copy to avoid mutating the original lists.
    ids = identities[:]
    keys = requesturis[:]
    tasks = zip(ids, keys)
    while tasks:
        for identity, requesturi in tasks[:]:
            try:
                print "getting identity information for {}.".format(identity)
                name, info = getidentity(identity, ownidentity)
            except ProtocolError as e:
                print e.args[0]
                unknowniderror = 'plugins.WebOfTrust.exceptions.UnknownIdentityException: {}'.format(identity)
                if e.args[0]['Replies.Description'] == unknowniderror:
                    logging.warn("identity to announce not yet known. Adding trust {} for {}".format(trustifmissing, identity))
                    addidentity(requesturi)
                    settrust(ownidentity, identity, trustifmissing, commentifmissing)
                name, info = getidentity(identity, ownidentity)
            if "babcomcaptchas" in info["Properties"]:
                with fcp.FCPNode() as n:
                    print "Getting CAPTCHAs for id", identity
                    captchas = fastget(info["Properties"]["babcomcaptchas"])[1]
                # task finished
                tasks.remove((identity, requesturi))
                yield captchas
            else:
                if info["CurrentEditionFetchState"] == "NotFetched":
                    print "Cannot announce to identity {}, because it has not been fetched, yet.".format(identity)
                    trust = gettrust(ownidentity, identity)
                    if trust == "Nonexistent":
                        print "No trust set yet. Setting trust", trustifmissing, "to ensure that identity {} gets fetched.".format(identity)
                        settrust(ownidentity, identity, trustifmissing, commentifmissing)
                        print "firing fastget({}) to make it more likely that the ID is fetched quickly (since it’s already in the local store, then).".format(requesturi)
                        fastget(requesturi)
                        yield None # unsuccessful, but feel free to try again
                    elif int(trust) >= 0:
                        print "The identity has trust {}, so it should be fetched soon.".format(trust)
                        print "firing fastget({}) to make it more likely that the ID is fetched quickly (since it’s already in the local store, then).".format(requesturi)
                        fastget(requesturi)
                        yield None # unsuccessful, but feel free to try again
                    else:
                        print "You marked this identity as spammer or disruptive by setting trust {}, so it cannot be fetched.".format(trust)
                else:
                    print "Identity {} published no CAPTCHAs, cannot announce to it.".format(identity)
                    tasks.remove((identity, requesturi))



def _test():

    """Run the tests

    >>> True
    True
    """
    try:
        import newbase60
        numtostring = newbase60.numtosxg
    except:
        numtostring = str
        
    import doctest
    tests = doctest.testmod()
    if tests.failed:
        return "☹"*tests.failed + " / " + numtostring(tests.attempted)
    return "^_^ (" + numtostring(tests.attempted) + ")"


if __name__ == "__main__":
    args = parse_args()
    slowtests = args.slowtests
    if args.port:
        fcp.node.defaultFCPPort = args.port
    if args.host:
        fcp.node.defaultFCPHost = args.host
    if args.verbosity:
        fcp.node.defaultVerbosity = int(args.verbosity)
    if args.test:
        print _test()
        sys.exit(0)
    prompt = Babcom()
    prompt.username = args.user
    prompt.cmdloop('Starting babcom, type help or intro')
