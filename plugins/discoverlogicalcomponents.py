#!/usr/bin/python
# discoverlogicalcomponents.py -- nagios plugin for discovering
#logical gluster components
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
import json
import sys

from glusternagios import utils
from glusternagios import glustercli


def discoverlogicalelements():
    resultlist = {}
    resultlist['volumes'] = []

    volumes = glustercli.volumeInfo()
    for volume in volumes.values():
        volDict = {}
        volDict['name'] = volume['volumeName']
        volDict['type'] = volume['volumeType']
        volDict['bricks'] = []
        for brickstr in volume['bricks']:
            brickproplist = brickstr.split(':')
            volDict['bricks'].append({'hostip': brickproplist[0],
                                      'brickpath': brickproplist[1]})
        resultlist['volumes'].append(volDict)

    resultstring = json.dumps(resultlist)
    print resultstring
    sys.exit(utils.PluginStatusCode.OK)


if __name__ == '__main__':
    discoverlogicalelements()
