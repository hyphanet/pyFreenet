import sys, os

from .node import FCPNode, JobTicket
from .node import ConnectionRefused, FCPException, FCPGetFailed, \
                 FCPPutFailed, FCPProtocolError

from .node import fcpVersion

from .node import SILENT, FATAL, CRITICAL, ERROR, INFO, DETAIL, DEBUG, NOISY

#from put import main as put
#from get import main as get
#from genkey import main as genkey
#from invertkey import main as invertkey
#from redirect import main as redirect
#from names import main as names
from . import upload, put, get, genkey, invertkey, redirect, names
from . import fproxyproxy
#import fproxyaddref
from . import pseudopythonparser

isDoze = sys.platform.lower().startswith("win")

if not isDoze:
    from . import freenetfs


__all__ = ['node', 'sitemgr', 'xmlrpc',
           'FCPNode', 'JobTicket',
           'ConnectionRefused', 'FCPException', 'FCPPutFailed',
           'FCPProtocolError',
           'get', 'put', 'genkey', 'invertkey', 'redirect', 'names',
           'fproxyproxy', "fproxyaddref",
           ]

if not isDoze:
    __all__.append('freenetfs')


