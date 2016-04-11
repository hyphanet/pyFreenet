#!/usr/bin/env python2
# encoding: utf-8

"""Implementation of Freenet Commmunication Primitives"""


import sys
import argparse # commandline arguments
import cmd # interactive shell
import fcp


slowtests = False


# first, parse commandline arguments
def parse_args():
    """Parse commandline arguments."""
    parser = argparse.ArgumentParser(description="Implementation of Freenet Communication Primitives")
    parser.add_argument('-u', '--user', default=None, help="Identity to use (default: create new)")
    parser.add_argument('--test', default=False, action="store_true", help="Run the tests")
    args = parser.parse_args()
    return args


# then add interactive usage, since this will be a communication tool
class Babcom(cmd.Cmd):
    prompt = "> "
    
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


def _matchingidentities(prefix, response):
    """Find matching identities in a Web of Trust Plugin response.

    >>> _matchingidentities("BabcomTest", {})
    []
    """
    field = "Replies.Nickname"
    matches = []
    nickname_prefix, key_prefix = _parse_name(prefix)
    for i in response:
        if i.startswith(field) and response[i].startswith(prefix):
            # format: Replies.Nickname<id_num>
            id_num = i[len(field):]
            nickname = response[i]
            pubkey_hash = response['Replies.Identity{}'.format(id_num)]
            request = response['Replies.RequestURI{}'.format(id_num)]
            insert = response['Replies.InsertURI{}'.format(id_num)]
            contexts = [response[j] for j in response if j.startswith("Replies.Contexts{}.Context".format(id_num))]
            property_keys_keys = [j for j in response
                                  if (j.startswith("Replies.Properties{}.Property".format(id_num))
                                      and j.endswith(".Name"))]
            property_value_keys = [j for j in response
                                   if (j.startswith("Repllies.Properties{}.Property".format(id_num))
                                       and j.endswith(".Value"))]
            properties = dict((i[j], i[k]) for j,k in zip(property_keys_keys, property_value_keys))
            if pubkey_hash.startswith(key_prefix):
                matches.append((nickname, {"id_num": id_num, "Identity":
                                           pubkey_hash, "RequestURI": request, "InsertURI": insert,
                                           "Contexts": contexts, "Properties": properties}))

    return matches


def wotmessage(messagetype, **params):
    """Send a message to the Web of Trust plugin

    >>> name = wotmessage("RandomName")["Replies.Name"]
    """
    params["Message"] = messagetype
    with fcp.FCPNode() as n:
        resp = n.fcpPluginMessage(plugin_name="plugins.WebOfTrust.WebOfTrust",
                                  plugin_params=params)[0]
    return resp
    
        

def createidentity(name="BabcomTest"):
    """Create a new Web of Trust identity.

    >>> # createidentity("BabcomTest")
    
    returns {'Replies.Message': 'IdentityCreated', 'Success': 'true', 'Replies.RequestURI': 'USK@...,AQACAAE/WebOfTrust/0', 'Replies.InsertURI': 'USK@...,AQECAAE/WebOfTrust/0', 'header': 'FCPPluginReply', 'PluginName': 'plugins.WebOfTrust.WebOfTrust', 'Replies.ID': '...', 'Identifier': 'id...'}
    """
    if not name:
        name = wotmessage("RandomName")["Name"]
    resp = wotmessage("CreateIdentity", Nickname=name, Context="", # empty context
                      PublishTrustList="true", # must use string "true"
                      PublishIntroductionPuzzles="true")
    if resp['header'] != 'FCPPluginReply' or resp.get('Replies.Message', "") != 'IdentityCreated':
        raise ProtocolError()
    return name

    
def getownidentities(user):
    """Get all own identities which match user."""
    with fcp.FCPNode() as n:
        # n.verbosity = 5
        resp = n.fcpPluginMessage(plugin_name="plugins.WebOfTrust.WebOfTrust",
                                  plugin_params={"Message": "GetOwnIdentities"})[0]
    if resp['header'] != 'FCPPluginReply' or resp.get('Replies.Message', '') != 'OwnIdentities':
        return None
    return _matchingidentities(user, resp)

    
def myidentity(user=None):
    """Get an identity from the Web of Trust plugin.

    :param user: Name of the Identity, optionally with additional
                 prefix of the key to disambiguate it.

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
        resp = n.fcpPluginMessage(plugin_name="plugins.WebOfTrust.WebOfTrust",
                                  plugin_params={"Message": "AddContext",
                                                 "Identity": identity,
                                                 "Context": context})[0]
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
        resp = n.fcpPluginMessage(plugin_name="plugins.WebOfTrust.WebOfTrust",
                                  plugin_params={"Message": "RemoveContext",
                                                 "Identity": identity,
                                                 "Context": context})[0]
    if resp['header'] != 'FCPPluginReply' or resp.get('Replies.Message', '') != 'ContextRemoved':
        raise ProtocolError(resp)
    

def fastput(node, private, data, async=False):
    """Upload a small amount of data as fast as possible.

    >>> with fcp.FCPNode() as n:
    ...    pub, priv = n.genkey(name="hello.txt")
    ...    if slowtests or True:
    ...        pubtoo = fastput(n, priv, "Hello Friend!")
    """
    return node.put(uri=private, data="Hello Friend!",
                    async=async,
                    mimetype="application/octet-stream",
                    realtime=True, priority=1)


def fastget(node, public, async=False):
    """Download a small amount of data as fast as possible.

    >>> with fcp.FCPNode() as n:
    ...    pub, priv = n.genkey(name="hello.txt")
    ...    if slowtests:
    ...        fastput(n, priv, "Hello Friend!")
    ...        fastget(n, pub, "Hello Friend!")
    """
    return node.get(public, async=async,
                    realtime=True, priority=1)
    
    
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
    if args.test:
        print _test()
        sys.exit(0)
    prompt = Babcom()
    prompt.cmdloop('Starting babcom, type help for help')
