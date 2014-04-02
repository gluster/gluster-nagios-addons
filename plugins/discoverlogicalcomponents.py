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
import commands
import json
import sys

from glusternagios import utils


def discoverbricks(vol_info_out):
    bricklist = []
    xmlElemList = utils.parseXml(vol_info_out,
                                 "./volInfo/volumes/volume/bricks/brick")
    for brick in xmlElemList:
        brickdict = {}
        brickstr = brick.text
        brickproplist = brickstr.split(':')
        brickdict['hostip'] = brickproplist[0]
        brickdict['brickpath'] = brickproplist[1]
        bricklist.append(brickdict)

    return bricklist


def discovervolumes(vol_info_out):
    vollist = []

    #Get the volume info
    xmlElemList = utils.parseXml(vol_info_out, "./volInfo/volumes/volume")
    for volume in xmlElemList:
        voldict = {}
        voldict['name'] = volume.find('name').text
        voldict['typeStr'] = volume.find('typeStr').text
        vollist.append(voldict)

    return vollist


def discoverlogicalelements():
    resultlist = {}
    resultstring = ""
    command_vol_info = utils.sudoCmdPath.cmd + " " + \
        utils.glusterCmdPath.cmd + " volume info --xml"
    vol_info_out = commands.getoutput(command_vol_info)
    resultlist['volumes'] = discovervolumes(vol_info_out)
    resultlist['bricks'] = discoverbricks(vol_info_out)
    #convert to string
    resultstring = json.dumps(resultlist)
    print resultstring
    sys.exit(utils.PluginStatusCode.OK)


if __name__ == '__main__':
    discoverlogicalelements()
