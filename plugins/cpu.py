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
from glusternagios import utils
import sadf

_sadfCpuCommand = ["sadf", "-x", "--", "-P", "ALL"]


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


def showCpuStat(warnLevel, critLevel, s):
    pl_op = {}
    if not s:
        pl_op["message"] = ("CPU STATUS UNKNOWN")
        pl_op['exit_status'] = utils.PluginStatusCode.UNKNOWN
        return pl_op
    perfLines = []
    idleCpu = 0
    try:
        for cpu in s['cpu-load']['cpu']:
            if cpu['number'] == 'all':
                idleCpu = cpu['idle']
            perfLines.append(
                ("cpu_%s_total=%s%%;%s;%s cpu_%s_system=%s%% "
                 "cpu_%s_user=%s%% cpu_%s_idle=%s%%" % (
                     cpu['number'], 100 - float(cpu['idle']),
                     warnLevel, critLevel,
                     cpu['number'], cpu['system'],
                     cpu['number'], cpu['user'],
                     cpu['number'], cpu['idle'])))
            if len(s['cpu-load']['cpu']) - 1 == 1:
                break
    except (KeyError, ValueError, TypeError) as e:
        pl_op["message"] = "key: %s not found" % str(e)
        pl_op["exit_status"] = utils.PluginStatusCode.UNKNOWN
        return pl_op

    totalCpuUsage = 100 - float(idleCpu)
    if totalCpuUsage > critLevel:
        pl_op["message"] = ("CPU Status CRITICAL: Total CPU:"
                            "%s%% Idle CPU:%s%% "
                            "| num_of_cpu=%s %s" % (
                                totalCpuUsage, idleCpu,
                                len(s['cpu-load']['cpu']) - 1,
                                " ".join(perfLines)))
        pl_op['exit_status'] = utils.PluginStatusCode.CRITICAL
    elif totalCpuUsage > warnLevel:
        pl_op["message"] = ("CPU Status WARNING: Total CPU"
                            ":%s%% Idle CPU:%s%% "
                            "| num_of_cpu=%s %s" % (
                                totalCpuUsage, idleCpu,
                                len(s['cpu-load']['cpu']) - 1,
                                " ".join(perfLines)))
        pl_op['exit_status'] = utils.PluginStatusCode.WARNING
    else:
        pl_op["message"] = ("CPU Status OK: Total CPU:%s%% Idle CPU:%s%% "
                            "| num_of_cpu=%s %s" % (
                                totalCpuUsage, idleCpu,
                                len(s['cpu-load']['cpu']) - 1,
                                " ".join(perfLines)))
        pl_op['exit_status'] = utils.PluginStatusCode.OK
    return pl_op


if __name__ == '__main__':
    args = parse_input()
    if args.critical <= args.warning:
        print "UNKNOWN:Critical must be greater than Warning."
        sys.exit(utils.PluginStatusCode.UNKNOWN)
    try:
        st = sadf.getLatestStat(sadf.sadfExecCmd(_sadfCpuCommand),
                                args.interval if args.interval else 1)
    except (sadf.SadfCmdExecFailedException,
            sadf.SadfXmlErrorException) as e:
        print str(e)
        exit(utils.PluginStatusCode.UNKNOWN)
    d = showCpuStat(args.warning, args.critical, st)
    print d["message"]
    exit(d['exit_status'])
