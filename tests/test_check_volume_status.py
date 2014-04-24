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
import json
import mock

from testrunner import PluginsTestCase as TestCaseBase
from plugins import check_volume_status
from glusternagios import utils
from glusternagios import glustercli


class ArgParseMock(object):
    def __init__(self, cluster, volume, type="info"):
        self.cluster = cluster
        self.volume = volume
        self.type = type


class TestCheckVolumeStatus(TestCaseBase):

    # Method to test volume status
    @mock.patch('glusternagios.glustercli.volumeInfo')
    def test_checkVolumeStatus(self, mock_volumeInfo):
        mock_volumeInfo.return_value = _getVolume()
        args = ArgParseMock('test-cluster', 'test-vol')
        exitStatusCode, exitStatusMsg = (check_volume_status
                                         .getVolumeStatus(args))
        print exitStatusMsg
        print _expectedVolume()
        assert exitStatusMsg == ("OK: Volume is up \n%s" % _expectedVolume())
        assert exitStatusCode == utils.PluginStatusCode.OK

    # Method to test volume status when no volume
    @mock.patch('glusternagios.glustercli.volumeInfo')
    def test_checkVolumeStatusNoVol(self, mock_volumeInfo):
        mock_volumeInfo.return_value = _getEmptyVolume()
        args = ArgParseMock('test-cluster', 'test-vol')
        exitStatusCode, exitStatusMsg = (check_volume_status
                                         .getVolumeStatus(args))
        assert exitStatusCode == utils.PluginStatusCode.CRITICAL

    @mock.patch('glusternagios.glustercli.volumeQuotaStatus')
    def test_checkVolumeQuotaStatus(self, mock_volumeQuotaStatus):
        mock_volumeQuotaStatus.return_value = glustercli.\
            VolumeQuotaStatus.EXCEEDED
        args = ArgParseMock('test-cluster', 'test-vol', 'quota')
        exitStatusCode, exitStatusMsg = (check_volume_status
                                         .getVolumeQuotaStatus(args))
        assert exitStatusCode == utils.PluginStatusCode.WARNING

    @mock.patch('glusternagios.glustercli.volumeGeoRepStatus')
    def test_checkVolumeGeoRepStatus(self, mock_GeoRepStatus):
        mock_GeoRepStatus.return_value = _getGeoRepStatus(glustercli
                                                          .GeoRepStatus.FAULTY)
        args = ArgParseMock('test-cluster', 'test-vol', 'geo-rep')
        exitStatusCode, exitStatusMsg = (check_volume_status
                                         .getVolumeGeoRepStatus(args))
        assert exitStatusCode == utils.PluginStatusCode.CRITICAL
        mock_GeoRepStatus.return_value = _getGeoRepStatus(glustercli
                                                          .GeoRepStatus
                                                          .PARTIAL_FAULTY)
        exitStatusCode, exitStatusMsg = (check_volume_status
                                         .getVolumeGeoRepStatus(args))
        assert exitStatusCode == utils.PluginStatusCode.WARNING


def _getVolume():
    vol = {'test-vol': {'brickCount': 2,
                        'bricks': ['server1:/path1', 'server2:/path2'],
                        'options': {'option': 'val'},
                        'transportType': ['tcp'],
                        'uuid': '0000-0000-0000-1111',
                        'volumeName': 'test-vol',
                        'volumeStatus': 'ONLINE',
                        'volumeType': 'DISTRIBUTED'},
           'test-vol2': {'brickCount': 2,
                         'bricks': ['server1:/path1', 'server2:/path2'],
                         'options': {'option': 'val'},
                         'transportType': ['tcp'],
                         'uuid': '0000-0000-0000-1111',
                         'volumeName': 'test-vol',
                         'volumeStatus': 'ONLINE',
                         'volumeType': 'DISTRIBUTED'}}
    return vol


def _expectedVolume():
    vol = {'test-vol': {'brickCount': 2,
                        'bricks': ['server1:/path1', 'server2:/path2'],
                        'options': {},
                        'transportType': ['tcp'],
                        'uuid': '0000-0000-0000-1111',
                        'volumeName': 'test-vol',
                        'volumeStatus': 'ONLINE',
                        'volumeType': 'DISTRIBUTED'}}
    return json.dumps(vol)


def _getEmptyVolume():
    return {}


def _getGeoRepStatus(status):
    return {'test-vol': {'status': status,
                         'detail': "rhs3-2.novalocal - faulty;"}}
