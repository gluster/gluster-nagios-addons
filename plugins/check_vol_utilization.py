#!/usr/bin/python
# check_vol_utilization.py -- nagios plugin uses libgfapi output for perf data
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
import argparse
import capacity
from glusternagios import utils
from glusternagios import glustercli


def showVolumeUtilization(vname, warnLevel, critLevel):
    buf = {}
    try:
        buf = capacity.statvfs(vname, "localhost")
    except Exception:
        sys.stdout.write("UNKNOWN: Failed to get the "
                         "Volume Utilization Data\n")
        sys.exit(utils.PluginStatusCode.UNKNOWN)
####################################################################
#statvfs.frsize * statvfs.f_blocks# Size of filesystem in bytes    #
#statvfs.frsize * statvfs.f_bfree # Actual number of free bytes    #
#statvfs.frsize * statvfs.f_bavail# Number of free bytes that      #
#ordinary users are allowed to use (excl. reserved space           #
####################################################################
    #total size in KB
    total_size = (buf['f_bsize'] * buf['f_blocks']) / 1024.0
    #Available free size in KB
    free_size = (buf['f_bsize'] * buf['f_bavail']) / 1024.0
    #used size in KB
    used_size = total_size - ((buf['f_bsize'] * buf['f_bfree']) / 1024.0)
    vol_utilization = (used_size / total_size) * 100
    perfLines = []
    perfLines.append(("utilization=%.2f%%;%d;%d total=%0.2f "
                      "used=%0.2f free=%0.2f" % (vol_utilization, warnLevel,
                                                 critLevel, total_size,
                                                 used_size, free_size)))
    if int(vol_utilization) > critLevel:
        sys.stdout.write(
            ("CRITICAL: Utilization:%0.2f%%"
             "| %s\n" % (vol_utilization, " ".join(perfLines))))
        sys.exit(utils.PluginStatusCode.CRITICAL)
    elif int(vol_utilization) > warnLevel:
        sys.stdout.write(
            ("WARNING: Utilization:%0.2f%%"
             "| %s\n" % (vol_utilization, " ".join(perfLines))))
        sys.exit(utils.PluginStatusCode.WARNING)
    else:
        sys.stdout.write(
            ("OK: Utilization:%0.2f%%"
             "| %s\n" % (vol_utilization, " ".join(perfLines))))
        sys.exit(utils.PluginStatusCode.OK)


def check_volume_status(volume):
    try:
        volumes = glustercli.volumeInfo(volume)
        if volumes.get(volume) is None:
            sys.stdout.write("CRITICAL: Volume not found\n")
            sys.exit(utils.PluginStatusCode.CRITICAL)
        elif volumes[volume]["volumeStatus"] == \
                glustercli.VolumeStatus.OFFLINE:
            sys.stdout.write("CRITICAL: Volume is stopped\n")
            sys.exit(utils.PluginStatusCode.CRITICAL)
    except glustercli.GlusterCmdFailedException:
        sys.stdout.write("UNKNOWN: Failed to get the "
                         "Volume Utilization Data\n")
        sys.exit(utils.PluginStatusCode.UNKNOWN)


def parse_input():

    parser = argparse.ArgumentParser(
        usage='%(prog)s [-h] <volume> -w <Warning> -c <Critical>')
    parser.add_argument("volume",
                        help="Name of the volume to get the Utilization")
    parser.add_argument("-w",
                        "--warning",
                        action="store",
                        type=int,
                        help="Warning Threshold in percentage")
    parser.add_argument("-c",
                        "--critical",
                        action="store",
                        type=int,
                        help="Critical Threshold in percentage")
    args = parser.parse_args()
    if not args.critical or not args.warning:
        print "UNKNOWN:Missing critical/warning threshold value."
        sys.exit(3)
    if args.critical <= args.warning:
        print "UNKNOWN:Critical must be greater than Warning."
        sys.exit(3)
    return args

if __name__ == '__main__':
    args = parse_input()
    #check the volume status before getting the volume utilization
    check_volume_status(args.volume)
    showVolumeUtilization(args.volume, args.warning, args.critical)
