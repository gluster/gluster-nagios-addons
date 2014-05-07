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

import argparse

import check_proc_util
from glusternagios import utils
from glusternagios import glustercli


_NFS = "NFS"
_SMB = "SMB"
_CTDB = "CTDB"
_SHD = "SHD"
_QUOTA = "QUOTA"
_BRICK = "BRICK"
_GLUSTERD = "GLUSTERD"


def parse_input():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", action="store", dest="type",
                        required=True,
                        help="Type of status to be shown. Possible values:",
                        choices=[_NFS, _SMB, _CTDB, _SHD, _QUOTA, _BRICK,
                                 _GLUSTERD])
    parser.add_argument("-v", "--volume", action="store", required=False,
                        help="Name of the volume for status")
    parser.add_argument("-b", "--brickPath", action="store", required=False,
                        help="Brick Path")
    args = parser.parse_args()
    return args


def _findBrickName(volInfo, brickPath):
    hostUuid = glustercli.hostUUIDGet()
    for volumeName, volumeInfo in volInfo.iteritems():
        for brick in volumeInfo['bricksInfo']:
            if brick.get('hostUuid') == hostUuid \
                    and brick['name'].split(':')[1] == brickPath:
                return brick['name']


if __name__ == '__main__':
    args = parse_input()
    status, msg = check_proc_util.getGlusterdStatus()
    if status == utils.PluginStatusCode.OK:
        if args.type == _NFS:
            status, msg = check_proc_util.getNfsStatus(glustercli.volumeInfo())
        elif args.type == _SMB:
            status, msg = check_proc_util.getSmbStatus(glustercli.volumeInfo())
        elif args.type == _SHD:
            status, msg = check_proc_util.getShdStatus(glustercli.volumeInfo())
        elif args.type == _QUOTA:
            status, msg = check_proc_util.getQuotadStatus(
                glustercli.volumeInfo())
        elif args.type == _CTDB:
            volInfo = glustercli.volumeInfo()
            nfsStatus, nfsMsg = check_proc_util.getNfsStatus(volInfo)
            smbStatus, smbMsg = check_proc_util.getSmbStatus(volInfo)
            status, msg = check_proc_util.getCtdbStatus(smbStatus, nfsStatus)
        elif args.type == _BRICK:
            volInfo = glustercli.volumeInfo(args.volume)
            brickName = _findBrickName(volInfo, args.brickPath)
            if brickName:
                status, msg = check_proc_util.getBrickStatus(args.volume,
                                                             brickName)
            else:
                status = utils.PluginStatusCode.CRITICAL
                msg = "Brick - %s not found" % args.brickPath
    elif args.type != _GLUSTERD:
        msg = "UNKNOWN: Could not determine %s status " % args.type
        status = utils.PluginStatusCode.UNKNOWN
    print msg
    exit(status)
