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
import mock

from testrunner import PluginsTestCase as TestCaseBase
from plugins import check_quorum_status
from glusternagios import utils


class TestCheckQuorumStatus(TestCaseBase):

    # Method to test quorum status when quorum not set
    @mock.patch('glusternagios.glustercli.volumeInfo')
    def test_checkStatusNoQuorum(self, mock_volumeInfo):
        mock_volumeInfo.return_value = _getVolumes('none')
        exitStatusCode, exitStatusMsg = (check_quorum_status
                                         .getClusterQuorumStatus())
        print exitStatusMsg
        assert exitStatusMsg == "Server quorum not turned on for any volume"
        assert exitStatusCode == utils.PluginStatusCode.UNKNOWN
        mock_volumeInfo.return_value = _getEmptyVolume()
        exitStatusCode, exitStatusMsg = (check_quorum_status
                                         .getClusterQuorumStatus())
        assert exitStatusMsg == "Server quorum not turned on for any volume"
        assert exitStatusCode == utils.PluginStatusCode.UNKNOWN

    # Method to test quorum status when options are turned on
    @mock.patch('glusternagios.glustercli.volumeInfo')
    def test_checkStatusWithQuorum(self, mock_volumeInfo):
        mock_volumeInfo.return_value = _getVolumes('server')
        exitStatusCode, exitStatusMsg = (check_quorum_status
                                         .getClusterQuorumStatus())
        assert exitStatusCode == utils.PluginStatusCode.OK
        assert exitStatusMsg == "Server quorum turned on " \
                                "for test-vol,test-vol2"


def _getVolumes(quorumVal):
    vol = {'test-vol': {'brickCount': 2,
                        'bricks': ['server1:/path1', 'server2:/path2'],
                        'options': {'cluster.quorum-type': 'none',
                                    'cluster.server-quorum-type': quorumVal,
                                    'changelog.changelog': 'on'},
                        'transportType': ['tcp'],
                        'uuid': '0000-0000-0000-1111',
                        'volumeName': 'test-vol',
                        'volumeStatus': 'ONLINE',
                        'volumeType': 'DISTRIBUTED'},
           'test-vol2': {'brickCount': 2,
                         'bricks': ['server1:/path1', 'server2:/path2'],
                         'options': {'cluster.quorum-type': 'none',
                                     'cluster.server-quorum-type': quorumVal,
                                     'changelog.changelog': 'on'},
                         'transportType': ['tcp'],
                         'uuid': '0000-0000-0000-1111',
                         'volumeName': 'test-vol',
                         'volumeStatus': 'ONLINE',
                         'volumeType': 'DISTRIBUTED'}}
    return vol


def _getEmptyVolume():
    return {}
