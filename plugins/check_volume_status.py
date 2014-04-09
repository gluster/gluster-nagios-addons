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
from glusternagios import utils
from glusternagios import glustercli


def getVolumeStatus(args):
    exitstatus = 0
    message = ""
    try:
        volumes = glustercli.volumeInfo(args.volume)
        if volumes.get(args.volume) is None:
            exitstatus = utils.PluginStatusCode.CRITICAL
            message = "CRITICAL: Volume not found"
            return exitstatus, message
        elif volumes[args.volume]["volumeStatus"] == (glustercli.
                                                      VolumeStatus.ONLINE):
            exitstatus = utils.PluginStatusCode.OK
            message = "OK: Volume is up"
        elif volumes[args.volume]["volumeStatus"] == (glustercli.
                                                      VolumeStatus.OFFLINE):
            exitstatus = utils.PluginStatusCode.CRITICAL
            message = "CRITICAL: Volume is stopped"
    except glustercli.GlusterCmdFailedException as e:
        out = "UNKNOWN: Command execution failed"
        return utils.PluginStatusCode.UNKNOWN,out

    return exitstatus, message

def parse_input():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--volume", action="store",
                        required=True,
                        help="Name of the volume for which"
                             " status is to be shown")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_input()
    exitstatus, message = getVolumeStatus(args)
    print message
    exit(exitstatus)
