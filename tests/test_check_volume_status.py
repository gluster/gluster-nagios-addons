#
# Copyright 2014 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#
import argparse

import mock

from testrunner import PluginsTestCase as TestCaseBase
from plugins import check_volume_status
from glusternagios import utils

class ArgParseMock(object):
     def __init__(self, cluster, volume):
         self.cluster = cluster
         self.volume = volume

class TestCheckVolumeStatus(TestCaseBase):

    # Method to test volume status
    @mock.patch('glusternagios.glustercli.volumeInfo')
    def test_checkVolumeStatus(self, mock_volumeInfo):
        mock_volumeInfo.return_value = _getVolume()
        args = ArgParseMock('test-cluster', 'test-vol')
        exitStatusCode, exitStatusMsg = (check_volume_status
                                         .getVolumeStatus(args))
        assert exitStatusCode == utils.PluginStatusCode.OK

    # Method to test volume status when no volume
    @mock.patch('glusternagios.glustercli.volumeInfo')
    def test_checkVolumeStatusNoVol(self, mock_volumeInfo):
        mock_volumeInfo.return_value = _getEmptyVolume()
        args = ArgParseMock('test-cluster', 'test-vol')
        exitStatusCode, exitStatusMsg = (check_volume_status
                                         .getVolumeStatus(args))
        assert exitStatusCode == utils.PluginStatusCode.CRITICAL



def _getVolume():
    vol = {'test-vol': {'brickCount': 2,
                      'bricks': ['server1:/path1', 'server2:/path2'],
                      'options': {'option':'val'},
                      'transportType': ['tcp'],
                      'uuid': '0000-0000-0000-1111',
                      'volumeName': 'test-vol',
                      'volumeStatus': 'ONLINE',
                      'volumeType': 'DISTRIBUTED'}}
    return vol


def _getEmptyVolume():
    return {}

