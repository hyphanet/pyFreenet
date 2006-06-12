import sys, os

from node import FCPNode, JobTicket
from node import ConnectionRefused, FCPException, FCPGetFailed, \
                 FCPPutFailed, FCPProtocolError

from node import SILENT, FATAL, CRITICAL, ERROR, INFO, DETAIL, DEBUG, NOISY

isDoze = sys.platform.lower().startswith("win")

if not isDoze:
    import freenetfs


__all__ = ['node', 'sitemgr', 'xmlrpc',
           'FCPNode', 'JobTicket',
           'ConnectionRefused', 'FCPException', 'FCPPutFailed',
           'FCPProtocolError',
           ]

if not isDoze:
    __all__.append('freenetfs')

