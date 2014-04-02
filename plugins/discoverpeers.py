#!/usr/bin/python
# discoverpeers.py -- nagios plugin for discovering gluster peers
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

import commands
import sys
import json

from glusternagios import utils


def discoverhosts():
    xmlElemList = []
    nrpe_out_list = []
    resltdict = {}
    resultstring = ""

    command_peer_status = utils.sudoCmdPath.cmd + " " \
        + utils.glusterCmdPath.cmd + " peer status --xml"
    peer_status_out = commands.getoutput(command_peer_status)

    xmlElemList = utils.parseXml(peer_status_out, "./peerStatus/peer")
    for peer in xmlElemList:
        if (peer.find('connected').text == "1"):
            resltdict['hostip'] = peer.find('hostname').text
            nrpe_out_list.append(resltdict)
    resultstring = json.dumps(nrpe_out_list)
    print resultstring
    sys.exit(utils.PluginStatusCode.OK)


if __name__ == '__main__':
    discoverhosts()
