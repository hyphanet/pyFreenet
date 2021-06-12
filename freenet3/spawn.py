#!/usr/bin/env python3

"""Spawn Freenet nodes on demand."""

import sys
import os
import glob
import time
import shutil
import stat
import zipfile
import socket
import urllib.request
import subprocess
import fcp3 as fcp
import random
import logging
try:
    from . import appdirs
except ImportError:
    from freenet3 import appdirs
    
logging.basicConfig(format="[%(levelname)s] %(message)s",
                    level=logging.INFO)


def _spawn_node(target_path, base_files, fcp_port, fproxy_port, name="babcom_node", transient=False):
    """
    Prepare a node and start it.
    
    >>> if not os.path.isdir("/tmp/babcom/"): os.makedirs("/tmp/babcom/")
    >>> # CHK@WxRXIGrJLtoTO4cmxVFnALFgPFzctObh-MKz-Bh0DjE,XQU69p6sEySS6cgMfID1aosQAZqGo84EnLcOOJAi9PY,AAMC--8/base_files.tar
    >>> try: tmp = shutil.copy("../freenet/freenet.jar", "../freenet-base_files_nix/base_files/")
    ... except: pass
    >>> _spawn_node("/tmp/babcom/spawn", "../freenet-base_files_nix/base_files", 9499, 8999) # doctest: +ELLIPSIS
    Waiting for Freenet at FCP port 9499 to start up.
    ...
    Build is 1474
    >>> n = fcp.FCPNode(port=9499)
    >>> try: n.kill() # node
    ... except fcp.node.FCPNodeFailure: pass
    _mgrThread: manager thread crashed
    >>> shutil.rmtree("/tmp/babcom/spawn") # cleanup
    """
    if os.path.exists(target_path):
        raise ValueError("Target path exists: " + target_path)

    # get all the basefiles
    shutil.copytree(base_files, target_path)
    # and customize this node
    freenet_ini = """\
fcp.port={}
fproxy.port={}
node.name={}
fproxy.hasCompletedWizard=true
security-levels.physicalThreatLevel=LOW
security-levels.networkThreatLevel=LOW
node.opennet.enabled=true
pluginmanager.loadplugin=UPnP
node.load.threadLimit=1000
logger.priority=ERROR
logger.priorityDetail=freenet.node.updater.RevocationChecker:ERROR
End
""".format(fcp_port, fproxy_port, name)
    if transient: # prepend option: ram for store and cache
        freenet_ini = """\
node.clientCacheType=ram
node.storeType=ram
""" + freenet_ini
    with open(os.path.join(target_path, "freenet.ini"), "w") as ini_file:
        ini_file.writelines(freenet_ini.splitlines(True))
        
    subprocess.check_output([os.path.join(target_path, "run.sh"), "start"])

    logging.info("Waiting for Freenet at FCP port %s to start up.", fcp_port)
    logging.info("Check its status at the local web url http://127.0.0.1:%s", fproxy_port)
    wait_until_online(fcp_port)
    logging.info("Started Freenet.")
    with fcp.FCPNode(port=fcp_port) as n:
        logging.info("Build is %s", n.nodeBuild)
        n.shutdown()


def wait_until_online(fcp_port):
    while True:
        try:
            n = fcp.FCPNode(port=fcp_port)
            n.shutdown()
            return
        except ConnectionRefusedError as e:
            time.sleep(5)


def _get_freenet_basefiles():
    """
    get files needed to spawn a Freenet node and cache it in an appropriate appdir.
    
    :returns: path to the appdir (string)
    
    >>> datadir = appdirs.AppDirs("babcom-ext", "freenetbasedata").user_data_dir
    >>> datadir == _get_freenet_basefiles() # /home/<user>/.local/share/babcom-ext
    True
    >>> list(sorted(os.listdir(datadir)))
    ['Uninstaller', 'bcprov-jdk15on-154.jar', 'bin', 'freenet-ext.jar', 'freenet.jar', 'lib', 'run.sh', 'seednodes.fref', 'wrapper.conf', 'wrapper.jar']
        
    """
    dirs = appdirs.AppDirs("babcom-ext", "freenetbasedata")
    datadir = dirs.user_data_dir
    datatmp = appdirs.AppDirs("babcom-ext-tmp", "freenetbasedata-tmp").user_data_dir
    java_installer_zip = os.path.join(datatmp, "java_installer.zip")
    url_and_name = [
        ("https://github.com/freenet/fred/releases/download/build01486/freenet-build01486.jar", "freenet.jar"),
        ("https://github.com/freenet/fred/releases/download/build01486/bcprov-jdk15on-1.59.jar", "bcprov-jdk15on-1.59.jar"),
        ("https://github.com/freenet/fred/releases/download/build01486/jna-4.5.2.jar", "jna-4.5.2.jar"),
        ("https://github.com/freenet/fred/releases/download/build01486/jna-platform-4.5.2.jar", "jna-platform-4.5.2.jar"),
        ("https://github.com/freenet/fred/releases/download/build01486/freenet-ext-29.jar", "freenet-ext.jar")
    ]
    cache_stale = False
    for url, name in url_and_name:
        if not os.path.exists(os.path.join(datadir, name)):
            cache_stale = True
    if not os.path.exists(os.path.join(datadir, "wrapper.jar")):
        cache_stale = True
    if cache_stale:
        if not os.path.isdir(datatmp):
            os.makedirs(datatmp)
        urllib.request.urlretrieve("https://github.com/freenet/java_installer/archive/next.zip",
                                   java_installer_zip)
        with zipfile.ZipFile(java_installer_zip) as f:
            f.extractall(datatmp)
        os.remove(java_installer_zip)
        java_installer_dir = os.path.join(datatmp, "java_installer-next")
        # recreate the datadir
        if os.path.isdir(datadir):
            shutil.rmtree(datadir)
        shutil.copytree(os.path.join(java_installer_dir, "res/unix/"), datadir)
        # make binaries executable
        os.chmod(os.path.join(datadir, "run.sh"), stat.S_IRWXU)
        for i in glob.glob(os.path.join(datadir, "bin", "*")):
            os.chmod(i, stat.S_IRWXU)
        shutil.copy(os.path.join(java_installer_dir, "res/wrapper.conf"), datadir)
        shutil.copy(os.path.join(java_installer_dir, "bin/wrapper.jar"), datadir)
        shutil.rmtree(datatmp)
        # add freenet, freenet-ext and bcprov
        # FIXME: freenet.jar and freenet-ext.jar do not seem to be up to date! (1474 instead of 1475!)
        # with urllib.request.urlopen(
        #         "https://downloads.freenetproject.org/alpha/freenet-stable-latest.jar.url") as f:
        #     latesturl = f.read().strip().decode("utf-8")
        for url, name in url_and_name:
            urllib.request.urlretrieve(url, os.path.join(datadir, name))
        # add seednodes
        urllib.request.urlretrieve("https://github.com/ArneBab/lib-pyFreenet-staging/releases/download/spawn-ext-data/seednodes.fref",
                                   os.path.join(datadir, "seednodes.fref"))
    return datadir


def _get_spawn_dir(fcp_port):
    return appdirs.AppDirs("babcom-spawn-{}".format(fcp_port), "freenet").user_data_dir


def _run_spawn(spawndir):
    """Start the spawn in the given folder."""
    fproxy_port = None
    with open(os.path.join(spawndir, "freenet.ini")) as f:
        prefix = "fproxy.port="
        for line in f:
            if line.startswith(prefix):
                fproxy_port = line[len(prefix):]
    logging.info("Running spawn in folder %s", spawndir)
    if fproxy_port:
        logging.info("Check its status at the local web url http://127.0.0.1:%s", fproxy_port)
    return subprocess.check_output([os.path.join(spawndir, "run.sh"), "start"])


def choose_free_port(host, starting_port):
    """Find a free port, starting with starting_port."""
    a = socket.socket()
    try:
        a.bind((host, starting_port))
    except socket.error:
        a.bind((host, 0)) # this finds a free port
    port = a.getsockname()[1]
    a.close()
    return port


def spawn_node(fcp_port=None, web_port=None, transient=False):
    """
    Spawn a node.

    :returns: fcp_port
    """
    datadir = _get_freenet_basefiles()
    if fcp_port is None:
        fcp_port = choose_free_port('', random.randint(9490, 9600))
    if web_port is None:
        web_port = choose_free_port('', random.randint(8990, 9100))
    spawndir = _get_spawn_dir(fcp_port)
    if os.path.isdir(spawndir) and os.path.isfile(os.path.join(spawndir, "run.sh")):
        try:
            with fcp.FCPNode(port=fcp_port) as n:
                n.shutdown() # close the fcp connection
        except ConnectionRefusedError:
            _run_spawn(spawndir)
            wait_until_online(fcp_port)
    else:
        _spawn_node(spawndir, datadir, fcp_port, web_port, transient=transient)
    return fcp_port
    

def teardown_node(fcp_port, delete_node_folder=True):
    """
    remove the spawned node.
    """
    with fcp.FCPNode(port=fcp_port) as n:
        try:
            n.kill(waituntilsent=True, **{"async": True})
            n.shutdown()
        except fcp.node.FCPNodeFailure:
            pass # that’s what we wanted.
    if delete_node_folder:
        # the freenet node writes some stuff on shutting down.
        # TODO: use ./run.sh status
        time.sleep(1)
        spawndir = _get_spawn_dir(fcp_port)
        shutil.rmtree(spawndir)
    else:
        logging.info("You can reuse this spawn via %s --port %s.", sys.argv[0], fcp_port)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
