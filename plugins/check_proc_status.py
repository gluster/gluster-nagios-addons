#!/usr/bin/python
# Copyright (C) 2014 Red Hat Inc
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
#

import sys
import errno
import lockfile
import logging
import psutil
import time
from daemon import runner
from logging import handlers
import nscautils
import glusternagios

from glusternagios import utils
from glusternagios import glustercli


_checkProc = utils.CommandPath('check_proc',
                               '/usr/lib64/nagios/plugins/check_procs')

_glusterVolPath = "/var/lib/glusterd/vols"
_checkNfsCmd = [_checkProc.cmd, "-c", "1:", "-C", "glusterfs", "-a", "nfs"]
_checkShdCmd = [_checkProc.cmd, "-c", "1:", "-C", "glusterfs", "-a",
                "glustershd"]
_checkSmbCmd = [_checkProc.cmd, "-c", "1:", "-C", "smbd"]
_checkQuotaCmd = [_checkProc.cmd, "-c", "1:", "-C", "glusterfs", "-a",
                  "quotad"]
_checkBrickCmd = [_checkProc.cmd, "-C", "glusterfsd"]
_checkGlusterdCmd = [_checkProc.cmd, "-c", "1:", "-w", "1:1", "-C", "glusterd"]
_checkCtdbCmd = [_checkProc.cmd, "-c", "1:", "-C", "ctdbd"]
_nfsService = "NFS"
_shdService = "Self-Heal"
_smbService = "CIFS"
_brickService = "Brick - "
_glusterdService = "Gluster Management"
_quotadService = "Quota"
_ctdbdService = "CTDB"


def getBrickStatus(volInfo):
    bricks = {}
    hostUuid = glustercli.hostUUIDGet()
    status = None
    for volumeName, volumeInfo in volInfo.iteritems():
        if volumeInfo['volumeStatus'] == glustercli.VolumeStatus.OFFLINE:
            continue
        for brick in volumeInfo['bricksInfo']:
            if brick.get('hostUuid') != hostUuid:
                continue
            brickPath = brick['name'].split(':')[1]
            brickService = "Brick Status - %s" % brickPath
            pidFile = brick['name'].replace(
                ":/", "-").replace("/", "-") + ".pid"
            try:
                with open("%s/%s/run/%s" % (
                        _glusterVolPath, volumeName, pidFile)) as f:
                    if psutil.pid_exists(int(f.read().strip())):
                        status = utils.PluginStatusCode.OK
                    else:
                        status = utils.PluginStatusCode.CRITICAL
            except IOError, e:
                if e.errno == errno.ENOENT:
                    status = utils.PluginStatusCode.CRITICAL
                else:
                    status = utils.PluginStatusCode.UNKNOWN
                    msg = "UNKNOWN: Brick %s: %s" % (brickPath, str(e))
            finally:
                if status == utils.PluginStatusCode.OK:
                    msg = "OK: Brick %s" % brickPath
                elif status != utils.PluginStatusCode.UNKNOWN:
                    msg = "CRITICAL: Brick %s is down" % brickPath
                bricks[brickService] = [status, msg]
    return bricks


def getNfsStatus(volInfo):
    # if nfs is already running we need not to check further
    status, msg, error = utils.execCmd(_checkNfsCmd)
    if status == utils.PluginStatusCode.OK:
        return status, msg[0] if len(msg) > 0 else ""

    # if nfs is not running and any of the volume uses nfs
    # then its required to alert the user
    for volume, volumeInfo in volInfo.iteritems():
        if volumeInfo['volumeStatus'] == glustercli.VolumeStatus.OFFLINE:
            continue
        nfsStatus = volumeInfo.get('options', {}).get('nfs.disable', 'off')
        if nfsStatus == 'off':
            msg = "CRITICAL: Process glusterfs-nfs is not running"
            status = utils.PluginStatusCode.CRITICAL
            break
    else:
        msg = "OK: No gluster volume uses nfs"
        status = utils.PluginStatusCode.OK
    return status, msg


def getCtdbStatus(smbStatus, nfsStatus):
    if smbStatus != utils.PluginStatusCode.OK and \
       nfsStatus != utils.PluginStatusCode.OK:
        return (utils.PluginStatusCode.OK,
                "CTDB ignored as SMB and NFS are not running")

    status, msg, error = utils.execCmd(_checkCtdbCmd)
    if status != utils.PluginStatusCode.OK:
        return utils.PluginStatusCode.UNKNOWN, "CTDB not configured"

    # CTDB, SMB/NFS are running
    status, msg, error = utils.execCmd(['ctdb', 'nodestatus'])
    if status == utils.PluginStatusCode.OK:
        if len(msg) > -1:
            message = msg[0].split()
            if len(message) > 1:
                msg = "Node status: %s" % message[2]
                if message[2] == 'UNHEALTHY':
                    status = utils.PluginStatusCode.WARNING
                elif message[2] in ['DISCONNECTED', 'BANNED', 'INACTIVE']:
                    status = utils.PluginStatusCode.CRITICAL
                else:
                    status = utils.PluginStatusCode.UNKNOWN
    return status, msg


def getSmbStatus(volInfo):
    status, msg, error = utils.execCmd(_checkSmbCmd)
    if status == utils.PluginStatusCode.OK:
        return status, msg[0] if len(msg) > 0 else ""

    # if smb is not running and any of the volume uses smb
    # then its required to alert the user
    for k, v in volInfo.iteritems():
        cifsStatus = v.get('options', {}).get('user.cifs', 'enable')
        smbStatus = v.get('options', {}).get('user.smb', 'enable')
        if cifsStatus == 'enable' and smbStatus == 'enable':
            msg = "CRITICAL: Process smb is not running"
            status = utils.PluginStatusCode.CRITICAL
            break
    else:
        msg = "OK: No gluster volume uses smb"
        status = utils.PluginStatusCode.OK
    return status, msg


def getQuotadStatus(volInfo):
    # if quota is already running we need not to check further
    status, msg, error = utils.execCmd(_checkQuotaCmd)
    if status == utils.PluginStatusCode.OK:
        return status, msg[0] if len(msg) > 0 else ""

    # if quota is not running and any of the volume uses quota
    # then the quotad process should be running in the host
    for k, v in volInfo.iteritems():
        quotadStatus = v.get('options', {}).get('features.quota', '')
        if quotadStatus == 'on':
            msg = "CRITICAL: Process quotad is not running"
            utils.PluginStatusCode.CRITICAL
            break
    else:
        msg = "OK: Quota not enabled"
        status = utils.PluginStatusCode.OK
    return status, msg


def getShdStatus(volInfo):
    status, msg, error = utils.execCmd(_checkShdCmd)
    if status == utils.PluginStatusCode.OK:
        return status, msg[0] if len(msg) > 0 else ""

    hostUuid = glustercli.hostUUIDGet()
    for volumeName, volumeInfo in volInfo.iteritems():
        if volumeInfo['volumeStatus'] == glustercli.VolumeStatus.OFFLINE:
            continue
        if hasBricks(hostUuid, volumeInfo['bricksInfo']) and \
           int(volumeInfo['replicaCount']) > 1:
            status = utils.PluginStatusCode.CRITICAL
            msg = "CRITICAL: Gluster Self Heal Daemon not running"
            break
    else:
        msg = "OK: Process Gluster Self Heal Daemon"
        status = utils.PluginStatusCode.OK
    return status, msg


def hasBricks(hostUuid, bricks):
    for brick in bricks:
        if brick['hostUuid'] == hostUuid:
            return True
    return False


class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/null'
        self.pidfile_path = '/var/run/glusterpmd.pid'
        self.pidfile_timeout = 5

    def run(self):
        hostName = nscautils.getCurrentHostNameInNagiosServer()
        sleepTime = int(nscautils.getProcessMonitorSleepTime())
        glusterdStatus = None
        nfsStatus = None
        smbStatus = None
        shdStatus = None
        quotaStatus = None
        ctdbStatus = None
        brickStatus = {}
        while True:
            if not hostName:
                hostName = nscautils.getCurrentHostNameInNagiosServer()
                if not hostName:
                    logger.warn("Hostname is not configured")
                    time.sleep(sleepTime)
                    continue
            status, msg, error = utils.execCmd(_checkGlusterdCmd)
            if status != glusterdStatus or \
                    status == utils.PluginStatusCode.CRITICAL:
                glusterdStatus = status
                msg = msg[0] if len(msg) > 0 else ""
                nscautils.send_to_nsca(hostName, _glusterdService, status, msg)

            # Get the volume status only if glusterfs is running to avoid
            # unusual delay
            if status != utils.PluginStatusCode.OK:
                logger.warn("Glusterd is not running")
                time.sleep(sleepTime)
                continue

            try:
                volInfo = glustercli.volumeInfo()
            except glusternagios.glustercli.GlusterCmdFailedException:
                logger.error("failed to find volume info")
                time.sleep(sleepTime)
                continue

            status, msg = getNfsStatus(volInfo)
            if status != nfsStatus or \
                    status == utils.PluginStatusCode.CRITICAL:
                nfsStatus = status
                nscautils.send_to_nsca(hostName, _nfsService, status, msg)

            status, msg = getSmbStatus(volInfo)
            if status != smbStatus or \
                    status == utils.PluginStatusCode.CRITICAL:
                smbStatus = status
                nscautils.send_to_nsca(hostName, _smbService, status, msg)

            status, msg = getCtdbStatus(smbStatus, nfsStatus)
            if status != ctdbStatus or \
                    status == utils.PluginStatusCode.CRITICAL:
                ctdbStatus = status
                nscautils.send_to_nsca(hostName, _ctdbdService, status, msg)

            status, msg = getShdStatus(volInfo)
            if status != shdStatus or \
                    status == utils.PluginStatusCode.CRITICAL:
                shdStatus = status
                nscautils.send_to_nsca(hostName, _shdService, status, msg)

            status, msg = getQuotadStatus(volInfo)
            if status != quotaStatus or \
                    status == utils.PluginStatusCode.CRITICAL:
                quotaStatus = status
                nscautils.send_to_nsca(hostName, _quotadService, status, msg)

            brick = getBrickStatus(volInfo)
            # brickInfo contains status, and message
            for brickService, brickInfo in brick.iteritems():
                if brickInfo[0] != brickStatus.get(brickService, [None])[0] \
                   or brickInfo[0] == utils.PluginStatusCode.CRITICAL:
                    brickStatus[brickService] = brickInfo
                    nscautils.send_to_nsca(hostName, brickService,
                                           brickInfo[0], brickInfo[1])
            time.sleep(sleepTime)

if __name__ == '__main__':
    app = App()
    logger = logging.getLogger("GlusterProcLog")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = handlers.TimedRotatingFileHandler(
        "/var/log/glusterpmd.log", 'midnight')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    daemonRunner = runner.DaemonRunner(app)
    daemonRunner.daemon_context.files_preserve = [handler.stream]
    try:
        daemonRunner.do_action()
    except lockfile.LockTimeout:
        logger.error("failed to aquire lock")
    except runner.DaemonRunnerStopFailureError:
        logger.error("failed to get the lock file")
    sys.exit(utils.PluginStatusCode.OK)
