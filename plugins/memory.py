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
import argparse
import sadf
from glusternagios import utils

_sadfMemCommand = ["sadf", "-x", "--", "-r"]


def parse_input():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--warning", action="store",
                        required=True, type=int,
                        help="Warning threshold in percentage")
    parser.add_argument("-c", "--critical", action="store",
                        required=True, type=int,
                        help="Critical threshold in percentage")
    sadf.add_common_args(parser)
    args = parser.parse_args()
    return args


def showMemStat(warning, critical, s):
    pl_op = {}
    if not s:
        pl_op["message"] = ("MEMORY STATUS UNKNOWN")
        pl_op['exit_status'] = utils.PluginStatusCode.UNKNOWN
        return pl_op
    try:
        totalMem = utils.convertSize((int(s['memory']['memfree'])
                                      + int(s['memory']['memused'])),
                                     "KB", "GB")
    except (KeyError, ValueError) as e:
        pl_op["message"] = "key: %s not found" % str(e)
        pl_op["exit_status"] = utils.PluginStatusCode.UNKNOWN
        return pl_op

    crit_value = (totalMem * critical) / 100
    war_value = (totalMem * warning) / 100
    usedMem = utils.convertSize(int(s['memory']['memused']) - int(
        s['memory']['cached']), "KB", "GB")
    usedPercent = usedMem * 100.0 / totalMem
    if usedMem >= crit_value:
        pl_op["message"] = utils.PluginStatus.CRITICAL
        pl_op['exit_status'] = utils.PluginStatusCode.CRITICAL
    elif usedMem >= war_value:
        pl_op["message"] = utils.PluginStatus.WARNING
        pl_op['exit_status'] = utils.PluginStatusCode.WARNING
    else:
        pl_op["message"] = utils.PluginStatus.OK
        pl_op['exit_status'] = utils.PluginStatusCode.OK
    try:
        pl_op["message"] += ("- %.2f%% used(%.2fGB out of %.2fGB)|"
                             "Total=%.2fGB;%.2f;%.2f;0;%.2f"
                             " Used=%.2fGB Buffered=%.2fGB"
                             " Cached=%.2fGB" % (
                                 usedPercent,
                                 usedMem,
                                 totalMem,
                                 totalMem,
                                 war_value,
                                 crit_value,
                                 totalMem,
                                 usedMem,
                                 utils.convertSize(int(s['memory']['buffers']),
                                                   "KB", "GB"),
                                 utils.convertSize(int(s['memory']['cached']),
                                                   "KB", "GB")))
    except (KeyError, ValueError, TypeError) as e:
        pl_op["message"] = "key: %s not found" % str(e)
        pl_op["exit_status"] = utils.PluginStatusCode.UNKNOWN
        return pl_op
    return pl_op

if __name__ == '__main__':
    args = parse_input()
    if args.critical <= args.warning:
        print "UNKNOWN:Critical must be greater than Warning."
        sys.exit(utils.PluginStatusCode.UNKNOWN)
    try:
        st = sadf.getLatestStat(sadf.sadfExecCmd(_sadfMemCommand),
                                args.interval if args.interval else 1)
    except (sadf.SadfCmdExecFailedException,
            sadf.SadfXmlErrorException) as e:
        print str(e)
        exit(utils.PluginStatusCode.UNKNOWN)
    d = showMemStat(args.warning, args.critical, st)
    print d["message"]
    sys.exit(d['exit_status'])
