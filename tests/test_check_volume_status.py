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
        assert exitStatusMsg == "OK: Volume : DISTRIBUTED type - Volume is up"
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
        args = ArgParseMock('test-cluster', 'test-vol', 'quota')
        mock_volumeQuotaStatus.return_value = _getQuotaStatusHardLimit()
        exitStatusCode, exitStatusMsg = (check_volume_status
                                         .getVolumeQuotaStatus(args))
        assert exitStatusCode == utils.PluginStatusCode.CRITICAL
        self.assertEqual("QUOTA:hard limit reached on dir1, dir2; "
                         "soft limit exceeded on dir3", exitStatusMsg)
        mock_volumeQuotaStatus.return_value = _getQuotaStatusOk()
        exitStatusCode, exitStatusMsg = (check_volume_status
                                         .getVolumeQuotaStatus(args))
        assert exitStatusCode == utils.PluginStatusCode.OK
        self.assertEqual("QUOTA: OK", exitStatusMsg)
        mock_volumeQuotaStatus.return_value = _getQuotaStatusSoftLimit()
        exitStatusCode, exitStatusMsg = (check_volume_status
                                         .getVolumeQuotaStatus(args))
        assert exitStatusCode == utils.PluginStatusCode.WARNING
        self.assertEqual("QUOTA:soft limit exceeded on dir3", exitStatusMsg)

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


def _getEmptyVolume():
    return {}


def _getQuotaStatusHardLimit():
    return {'status': 'HARD_LIMIT_EXCEEDED',
            'hard_ex_dirs': ['dir1', 'dir2'],
            'soft_ex_dirs': ['dir3']}


def _getQuotaStatusSoftLimit():
    return {'status': 'SOFT_LIMIT_EXCEEDED',
            'hard_ex_dirs': [],
            'soft_ex_dirs': ['dir3']}


def _getQuotaStatusOk():
    return {'status': 'OK',
            'hard_ex_dirs': [],
            'soft_ex_dirs': []}


def _getGeoRepStatus(status):
    return {'test-vol': {'slaves':
                         {'10.70.43.68::slave-vol':
                          {'faulty': 1,
                           'nodecount': 2,
                           'notstarted': 0,
                           'stopped': 0,
                           'detail': 'rhs3.novalocal:/bricks/b3 '
                                     '- Passive;'
                                     'rhs3-2.novalocal:/bricks/b3 '
                                     '- FAULTY;',
                           'status': status},
                          '10.70.43.68::slave-vol2':
                          {'faulty': 0,
                           'nodecount': 2,
                           'notstarted': 2,
                           'stopped': 0,
                           'detail': 'rhs3.novalocal:/bricks/b3 '
                                     '- NOT_STARTED;'
                                     'rhs3-2.novalocal:/bricks/b3 '
                                     '- NOT_STARTED;',
                           'status': "NOT_STARTED"}
                          }}}
