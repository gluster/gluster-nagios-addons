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

import sys
import json

from glusternagios import utils
from glusternagios import glustercli


def discoverhosts():
    resultlist = []
    peers = glustercli.peerStatus()
    for peer in peers:
        peerDict = {}
        peerDict['hostip'] = peer['hostname']
        peerDict['uuid'] = peer['uuid']
        peerDict['status'] = peer['status']
        resultlist.append(peerDict)
    resultstring = json.dumps(resultlist)
    print resultstring
    sys.exit(utils.PluginStatusCode.OK)


if __name__ == '__main__':
    discoverhosts()
