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

import sadf
import argparse
from glusternagios import utils

_sadfNetCommand = ["sadf", "-x", "--", "-n", "DEV"]


def parse_input():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e", "--exclude", action="append",
                       help="Parameters to be excluded")
    group.add_argument("-i", "--include", action="append",
                       help="Parameters to be included")
    sadf.add_common_args(parser)
    args = parser.parse_args()
    return args


def showNetStat(s, iface_list=None, list_type=None):
    pl_op = {}
    if not s:
        pl_op["message"] = ("IFACE UNKNOWN")
        pl_op['exit_status'] = utils.PluginStatusCode.UNKNOWN
        return pl_op
    devNames = []
    perfLines = []
    try:
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
    except (KeyError, ValueError, TypeError) as e:
        pl_op["message"] = "key: %s not found" % str(e)
        pl_op["exit_status"] = utils.PluginStatusCode.UNKNOWN
        return pl_op

    pl_op["message"] = ("IFACE OK: %s |%s" % (", ".join(devNames),
                                              " ".join(perfLines)))
    pl_op['exit_status'] = utils.PluginStatusCode.OK
    return pl_op

if __name__ == '__main__':
    args = parse_input()
    try:
        st = sadf.getLatestStat(sadf.sadfExecCmd(_sadfNetCommand),
                                args.interval if args.interval else 1)
    except (sadf.SadfCmdExecFailedException,
            sadf.SadfXmlErrorException) as e:
        print str(e)
        exit(utils.PluginStatusCode.UNKNOWN)
    if args.exclude:
        d = showNetStat(st, args.exclude, "exclude")
    elif args.include:
        d = showNetStat(st, args.include, "include")
    else:
        d = showNetStat(st)
    print d["message"]
    exit(d['exit_status'])
