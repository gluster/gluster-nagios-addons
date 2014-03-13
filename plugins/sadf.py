#!/usr/bin/python
# sadf.py -- nagios plugin uses sadf output for perf data
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
import shlex
import subprocess
import datetime
import argparse
import xml.etree.ElementTree as ET
from collections import defaultdict
_twoMinutes = datetime.timedelta(minutes=2)
_sadfCpuCommand = "sadf -x -- -P ALL"
_sadfMemoryCommand = "sadf -x -- -r"
_sadfNetworkCommand = "sadf -x -- -n DEV"
_sadfSwapSpaceCommand = "sadf -x -- -S"


class sadfCmdExecFailedException(Exception):
    message = "sadf command failed"

    def __init__(self, rc=0, out=(), err=()):
        self.rc = rc
        self.out = out
        self.err = err

    def __str__(self):
        o = '\n'.join(self.out)
        e = '\n'.join(self.err)
        if o and e:
            m = o + '\n' + e
        else:
            m = o or e

        s = self.message
        if m:
            s += '\nerror: ' + m
        if self.rc:
            s += '\nreturn code: %s' % self.rc
        return s


def execCmd(command):
    proc = subprocess.Popen(command,
                            close_fds=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    return (proc.returncode, out, err)


def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
        x = {}
        for k, v in dd.iteritems():
            x[k] = v[0] if len(v) == 1 else v
        d = {t.tag: x}
    if t.attrib:
        d[t.tag].update((k, v) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def _sadfExecCmd(sadfCmd):
    now = datetime.datetime.now()
    start = (now - _twoMinutes).strftime("%H:%M:%S")
    end = now.strftime("%H:%M:%S")
    cmd = sadfCmd + " -s %s -e %s" % (start, end)

    try:
        (rc, out, err) = execCmd(shlex.split(cmd))
    except (OSError, ValueError) as e:
        raise sadfCmdExecFailedException(err=[str(e)])

    if rc != 0:
        raise sadfCmdExecFailedException(rc, [out], [err])

    root = ET.fromstring(out)
    d = etree_to_dict(root)
    return d['sysstat']['host']['statistics']['timestamp']


def _getLatestStat(stats):
    if not stats:
        return {}
    if not isinstance(stats, list):
        return stats
    lstat = stats[0]
    latestTime = datetime.datetime.strptime(lstat['time'],
                                            "%H:%M:%S")
    for s in stats[1:]:
        thisTime = datetime.datetime.strptime(s['time'],
                                              "%H:%M:%S")
        if latestTime < thisTime:
            lstat = s
            latestTime = thisTime

    return lstat


def getLatestSadfCpuStat():
    return _getLatestStat(_sadfExecCmd(_sadfCpuCommand))


def getLatestSadfMemStat():
    return _getLatestStat(_sadfExecCmd(_sadfMemoryCommand))


def getLatestSadfNetStat():
    return _getLatestStat(_sadfExecCmd(_sadfNetworkCommand))


def getLatestSadfSwapStat():
    return _getLatestStat(_sadfExecCmd(_sadfSwapSpaceCommand))


def showCpuStat(warnLevel, critLevel):
    s = getLatestSadfCpuStat()
    if not s:
        sys.stdout.write("CPU UNKNOWN\n")
        sys.exit(3)
    perfLines = []
    idleCpu = 0
    for cpu in s['cpu-load']['cpu']:
        if cpu['number'] == 'all':
            idleCpu = cpu['idle']
        perfLines.append(
            ("cpu_%s_total=%s%%;%s;%s cpu_%s_system=%s%% "
             "cpu_%s_user=%s%% cpu_%s_idle=%s%%" % (
                 cpu['number'], 100-float(cpu['idle']),
                 warnLevel, critLevel,
                 cpu['number'], cpu['system'],
                 cpu['number'], cpu['user'],
                 cpu['number'], cpu['idle'])))
        if len(s['cpu-load']['cpu'])-1 == 1:
            break
    totalCpuUsage = 100 - float(idleCpu)
    if totalCpuUsage > critLevel:
        sys.stdout.write(
            ("CPU Status CRITICAL: Total CPU:%s%% Idle CPU:%s%% "
             "| num_of_cpu=%s %s\n" % (totalCpuUsage, idleCpu,
                                       len(s['cpu-load']['cpu'])-1,
                                       " ".join(perfLines))))
    elif totalCpuUsage > warnLevel:
        sys.stdout.write(
            ("CPU Status WARNING: Total CPU:%s%% Idle CPU:%s%% "
             "| num_of_cpu=%s %s\n" % (totalCpuUsage, idleCpu,
                                       len(s['cpu-load']['cpu'])-1,
                                       " ".join(perfLines))))
    else:
        sys.stdout.write(
            ("CPU Status OK: Total CPU:%s%% Idle CPU:%s%% "
             "| num_of_cpu=%s %s\n" % (totalCpuUsage, idleCpu,
                                       len(s['cpu-load']['cpu'])-1,
                                       " ".join(perfLines))))

    sys.exit(0)


def showSwapStat(warning, critical):
    s = getLatestSadfSwapStat()
    if not s:
        sys.stdout.write("IFACE UNKNOWN\n")
        sys.exit(3)
    totalSwap = int(s['memory']['swpfree']) + int(s['memory']['swpused'])
    crit_value = (totalSwap * critical) / 100
    war_value = (totalSwap * warning) / 100
    if int(s['memory']['swpused']) >= crit_value:
        sys.stdout.write("CRITICAL")
        eStat = 2
    elif int(s['memory']['swpused']) >= war_value:
        sys.stdout.write("WARNING")
        eStat = 1
    else:
        sys.stdout.write("OK")
        eStat = 0
    sys.stdout.write("- %.2f%% used(%skB out of %skB)|Used=%skB;%s;"
                     "%s;0;%s\n" % (float(s['memory']['swpused-percent']),
                                    s['memory']['swpused'],
                                    totalSwap,
                                    s['memory']['swpused'],
                                    war_value,
                                    crit_value,
                                    totalSwap))
    sys.exit(eStat)


def showMemStat(warning, critical):
    s = getLatestSadfMemStat()
    if not s:
        sys.stdout.write("IFACE UNKNOWN\n")
        sys.exit(3)
    totalMem = int(s['memory']['memfree']) + int(s['memory']['memused'])
    crit_value = (totalMem * critical) / 100
    war_value = (totalMem * warning) / 100
    if int(s['memory']['memused']) >= crit_value:
        sys.stdout.write("CRITICAL")
        eStat = 2
    elif int(s['memory']['memused']) >= war_value:
        sys.stdout.write("WARNING")
        eStat = 1
    else:
        sys.stdout.write("OK")
        eStat = 0
    sys.stdout.write("- %.2f%% used(%skB out of %skB)|Total=%skB;%s;%s;0;%s"
                     " Used=%skB Buffered=%skB"
                     " Cached=%skB\n" % (float(s['memory']['memused-percent']),
                                         s['memory']['memused'],
                                         totalMem,
                                         totalMem,
                                         war_value,
                                         crit_value,
                                         totalMem,
                                         s['memory']['memused'],
                                         s['memory']['buffers'],
                                         s['memory']['cached']))
    sys.exit(eStat)


def showNetStat(iface_list=None, list_type=None):
    s = getLatestSadfNetStat()
    if not s:
        sys.stdout.write("IFACE UNKNOWN\n")
        sys.exit(3)

    devNames = []
    perfLines = []
    for dev in s['network']['net-dev']:
        if list_type == "exclude":
            if dev['iface'] in iface_list:
                continue
        elif list_type == "include":
            if dev['iface'] not in iface_list:
                continue
        devNames.append(dev['iface'])
        perfLines.append("%s.rxpck=%s %s.txpck=%s %s.rxkB=%s %s.txkB=%s"
                         % (dev['iface'], dev['rxpck'],
                            dev['iface'], dev['txpck'],
                            dev['iface'], dev['rxkB'],
                            dev['iface'], dev['txkB']))

    sys.stdout.write("IFACE OK: %s |%s\n" % (", ".join(devNames),
                                             " ".join(perfLines)))
    sys.exit(0)


def parse_input():
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] (\
\n-m -w <warning> -c <critical> |\n-s -w <warning> -c <critical>\
 |\n-cp -w <warning> -c <critical> |\n-n [-e <exclude>\
 | -i <include>])')
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('-m', '--memory', action='store_true',
                        help="Gives details related to memory")
    group1.add_argument('-s', '--swap', action='store_true',
                        help="Gives details related to swap")
    group1.add_argument('-cp', '--cpu', action='store_true',
                        help="Gives details related to cpu")
    group1.add_argument('-n', '--network', action='store_true',
                        help="Gives details related to network")
    parser.add_argument("-w", "--warning", action="store", type=int,
                        help="Warning threshold in percentage")
    parser.add_argument("-c", "--critical", action="store", type=int,
                        help="Critical threshold in percentage")
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("-e", "--exclude", action="append",
                        help="Parameters to be excluded")
    group2.add_argument("-i", "--include", action="append",
                        help="Parameters to be included")
    args = parser.parse_args()
    if args.memory or args.swap or args.cpu:
        if not args.critical or not args.warning:
            print "UNKNOWN:Missing critical/warning threshold value."
            sys.exit(3)
        if args.exclude or args.include:
            print "UNKNOWN:Exclude/Include is not valid for the given option."
            sys.exit(3)
        if args.critical <= args.warning:
            print "UNKNOWN:Critical must be greater than Warning."
            sys.exit(3)
    else:
        if args.critical or args.warning:
            print "UNKNOWN:Warning/Critical is not valid for the given option."
            sys.exit(3)
    return args


if __name__ == '__main__':
    args = parse_input()
    if args.memory:
        showMemStat(args.warning, args.critical)
    if args.swap:
        showSwapStat(args.warning, args.critical)
    if args.cpu:
        showCpuStat(args.warning, args.critical)
    if args.network:
        if args.exclude:
            showNetStat(args.exclude, "exclude")
        if args.include:
            showNetStat(args.include, "include")
        showNetStat()
