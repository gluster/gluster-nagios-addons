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
import socket
import psutil
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
_checkSmbCmd = [_checkProc.cmd, "-C", "smb"]
_checkQuotaCmd = [_checkProc.cmd, "-c", "1:", "-C", "glusterfs", "-a",
                  "quotad"]
_checkBrickCmd = [_checkProc.cmd, "-C", "glusterfsd"]
_checkGlusterdCmd = [_checkProc.cmd, "-c", "1:", "-w", "1:1", "-C", "glusterd"]
_nfsService = "Glusterfs NFS Daemon"
_shdService = "Glusterfs Self-Heal Daemon"
_smbService = "CIFS"
_brickService = "Brick Status - "
_glusterdService = "Gluster Management Daemon"
_quotadService = "Gluster Quota Daemon"


def sendBrickStatus(hostName, volInfo):
    hostUuid = glustercli.hostUUIDGet()
    status = None
    for volumeName, volumeInfo in volInfo.iteritems():
        if volumeInfo['volumeStatus'] == glustercli.VolumeStatus.OFFLINE:
            continue
        for brick in volumeInfo['bricksInfo']:
            if brick.get('hostUuid') != hostUuid:
                continue
            brickService = "Brick Status - %s" % brick['name']
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
                    msg = "UNKNOWN: Brick %s: %s" % (brick['name'], str(e))
            finally:
                if status == utils.PluginStatusCode.OK:
                    msg = "OK: Brick %s" % brick['name']
                elif status != utils.PluginStatusCode.UNKNOWN:
                    msg = "CRITICAL: Brick %s is down" % brick['name']
                nscautils.send_to_nsca(hostName, brickService, status, msg)


def sendNfsStatus(hostName, volInfo):
    # if nfs is already running we need not to check further
    status, msg, error = utils.execCmd(_checkNfsCmd)
    if status == utils.PluginStatusCode.OK:
        nscautils.send_to_nsca(hostName, _nfsService, status, msg)
        return

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
    nscautils.send_to_nsca(hostName, _nfsService, status, msg)


def sendSmbStatus(hostName, volInfo):
    status, msg, error = utils.execCmd(_checkSmbCmd)
    if status == utils.PluginStatusCode.OK:
        nscautils.send_to_nsca(hostName, _smbService, status, msg)
        return

    # if smb is not running and any of the volume uses smb
    # then its required to alert the use
    for k, v in volInfo.iteritems():
        cifsStatus = v.get('options', {}).get('user.cifs', '')
        smbStatus = v.get('options', {}).get('user.smb', '')
        if cifsStatus == 'disable' or smbStatus == 'disable':
            msg = "CRITICAL: Process smb is not running"
            status = utils.PluginStatusCode.CRITICAL
            break
    else:
        msg = "OK: No gluster volume uses smb"
        status = utils.PluginStatusCode.OK
    nscautils.send_to_nsca(hostName, _smbService, status, msg)


def sendQuotadStatus(hostName, volInfo):
    # if quota is already running we need not to check further
    status, msg, error = utils.execCmd(_checkQuotaCmd)
    if status == utils.PluginStatusCode.OK:
        nscautils.send_to_nsca(hostName, _quotadService, status, msg)
        return

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
    nscautils.send_to_nsca(hostName, _quotadService, status, msg)


def sendShdStatus(hostName, volInfo):
    status, msg, error = utils.execCmd(_checkShdCmd)
    if status == utils.PluginStatusCode.OK:
        nscautils.send_to_nsca(hostName, _shdService, status, msg)
        return

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
    nscautils.send_to_nsca(hostName, _shdService, status, msg)


def hasBricks(hostUuid, bricks):
    for brick in bricks:
        if brick['hostUuid'] == hostUuid:
            return True
    return False


if __name__ == '__main__':
    hostName = nscautils.getCurrentHostNameInNagiosServer()
    if not hostName:
        hostName = socket.getfqdn()
    if hostName == "localhost.localdomain" or hostName == "localhost":
        sys.stderr.write("failed to find localhost fqdn")

    ### service check ###
    status, msg, error = utils.execCmd(_checkGlusterdCmd)
    nscautils.send_to_nsca(hostName, _glusterdService, status, msg)

    # Get the volume status only if glusterfs is running to avoid
    # unusual delay
    if status != utils.PluginStatusCode.OK:
        sys.exit(status)

    try:
        volInfo = glustercli.volumeInfo()
    except glusternagios.glustercli.GlusterCmdFailedException as e:
        sys.exit(utils.PluginStatusCode.UNKNOWN)

    sendNfsStatus(hostName, volInfo)
    sendSmbStatus(hostName, volInfo)
    sendShdStatus(hostName, volInfo)
    sendQuotadStatus(hostName, volInfo)
    sendBrickStatus(hostName, volInfo)

    sys.exit(utils.PluginStatusCode.OK)
