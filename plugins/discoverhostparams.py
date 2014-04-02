#!/usr/bin/python
# discoverhostparams.py -- nagios plugin discovering the host parameters
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
import json
import sys

from glusternagios import utils


def discoverhostparams():
    command_host_name = utils.hostnameCmdPath.cmd
    result_dict = {}
    resultString = ""

    hostname = commands.getoutput(command_host_name)
    result_dict['hostname'] = hostname
    resultString = json.dumps(result_dict)
    print resultString
    sys.exit(utils.PluginStatusCode.OK)


###
#This plugin discovers all the host specific parameters
#Currently it gets only the hostname from the node
#but when we add support for discovering physical
#components like cpu,network,disk etc, all those will be
#addded as part of this module
###
if __name__ == '__main__':
    discoverhostparams()
