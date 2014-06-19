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
import ethtool
import logging

import sadf
from glusternagios import utils

_description = "Network plugin for Nagios provides status and performance " \
               "data of network interfaces.  By default, it provides " \
               "details of all the interfaces having IP addresses"
_sadfNetCommand = ["sadf", "-x", "--", "-n", "DEV"]
_defaultExcludeList = ['lo']


class InterfaceStatus:
    UP = 'UP'
    DOWN = 'DOWN'


def parse_cmdargs():
    parser = argparse.ArgumentParser(description=_description)
    sadf.add_common_args(parser)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-e", "--exclude", action="append",
                       help="exclude given interface")
    group.add_argument("-i", "--include", action="append",
                       help="add given interface for monitoring")
    group.add_argument("-a", "--all", action="store_true", default=False,
                       help="get status of all interfaces")

    args = parser.parse_args()
    return args


def _getNetworkInterfaces(interfaces=()):
    if interfaces:
        devices = interfaces
    else:
        devices = ethtool.get_active_devices()

    info = {}
    for dev in devices:
        try:
            info[dev] = {'ipaddr': ethtool.get_ipaddr(dev),
                         'flags': ethtool.get_flags(dev)}
        except IOError as e:
            logging.error("unable to get ipaddr/flags for %s: %s" % (dev, e))
            info[dev] = {'ipaddr': None,
                         'flags': None}

    return info


def _getStatMessage(stat, all=False, includes=(), excludes=()):
    excludeList = _defaultExcludeList
    if excludes:
        excludeList += excludes

    rc = utils.PluginStatus.OK
    interfaces = _getNetworkInterfaces()
    devNames = []
    perfLines = []

    for info in stat['network']['net-dev']:
        ipaddr = interfaces.get(info['iface'], {}).get('ipaddr')
        flags = interfaces.get(info['iface'], {}).get('flags')
        if flags and (flags & ethtool.IFF_UP) and \
           (flags & ethtool.IFF_RUNNING):
            status = InterfaceStatus.UP
        else:
            status = InterfaceStatus.DOWN

        if includes:
            if info['iface'] not in includes:
                continue
        elif not all:
            if not ipaddr:
                continue
            elif info['iface'] in excludeList:
                continue

        if includes and (status == InterfaceStatus.DOWN):
            rc = utils.PluginStatus.WARNING

        devNames.append("%s:%s" % (info['iface'], status))
        perfLines.append("%s.rxpck=%s %s.txpck=%s %s.rxkB=%s %s.txkB=%s"
                         % (info['iface'], info['rxpck'],
                            info['iface'], info['txpck'],
                            info['iface'], info['rxkB'],
                            info['iface'], info['txkB']))

    return (getattr(utils.PluginStatusCode, rc),
            "%s: %s |%s" % (rc,
                            ",".join(devNames),
                            " ".join(perfLines)))


def main():
    args = parse_cmdargs()

    try:
        stat = sadf.getLatestStat(sadf.sadfExecCmd(_sadfNetCommand),
                                  args.interval)
        (rc, msg) = _getStatMessage(stat, all=args.all,
                                    includes=args.include,
                                    excludes=args.exclude)
        print msg
        sys.exit(rc)
    except (sadf.SadfCmdExecFailedException,
            sadf.SadfXmlErrorException,
            KeyError) as e:
        logging.error("unable to get network status: %s" % e)
        print "UNKNOWN"
        sys.exit(utils.PluginStatusCode.UNKNOWN)


if __name__ == '__main__':
    main()
