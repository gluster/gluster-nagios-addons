#!/usr/bin/python
# configure_gluster_node.py -- nagios plugin for configuring the node
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

import sys
import argparse

from glusternagios import utils
import nscautils

__SED_CMD_PATH = utils.CommandPath("sed", "/bin/sed")


def configureParam(paramName, value):
    sed_pattern = '/%s=.*/c\\%s=%s' % (paramName, paramName, value)
    command_sed = [__SED_CMD_PATH.cmd, '-i',
                   sed_pattern, nscautils.__NAGIOSSERVER_CONF]
    utils.execCmd(command_sed)


def configureNode(nagiosAddress, clusterName, hostName):
    configureParam("nagios_server", nagiosAddress)
    configureParam("cluster_name", clusterName)
    configureParam("hostname_in_nagios", hostName)
    print "Configured the node successfully"
    sys.exit(utils.PluginStatusCode.OK)


def create_arg_parser():
    parser = argparse.ArgumentParser(description="Gluster Auto Config Tool")
    parser.add_argument('-c', '--cluster', action='store', dest='cluster',
                        type=str, required=True, help='Cluster name')
    parser.add_argument('-n', '--nagios', action='store', dest='nagios',
                        type=str, required=True, help='Nagios Server Address')
    parser.add_argument('-H', '--hostname', action='store', dest='hostname',
                        type=str, required=True,
                        help='Name of the host in Nagios Configuration')
    return parser


if __name__ == '__main__':
    parser = create_arg_parser()
    args = parser.parse_args()
    configureNode(args.nagios, args.cluster, args.hostname)
