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

from testrunner import PluginsTestCase as TestCaseBase
from plugins import discover_volumes
import json


class TestDiscoverVolumes(TestCaseBase):
    def _getVolumeInfo(self):
        result = {}
        result['V1'] = {"bricksInfo": [{"name": "172.16.53.1:/bricks/v1-1",
                                        "hostUuid": "0000-1111"}],
                        "volumeType": "DISTRIBUTE", "volumeName": "V1",
                        "replicaCount": "1"}
        result['V2'] = {"bricksInfo": [{"name": "172.16.53.2:/bricks/v2-1",
                                        "hostUuid": "0000-1112"}],
                        "volumeType": "DISTRIBUTE", "volumeName": "V2",
                        "replicaCount": "1"}
        return result

    def _mockGetVolumeInfo(self, volumeName):
        volumes = self._getVolumeInfo()
        if volumeName:
            return {volumeName: volumes.get(volumeName)}
        else:
            return volumes

    def _getBrickByHostAndPath(self, bricksList, hostUuid, path):
        for brick in bricksList:
            if brick.get('hostUuid') == hostUuid and \
                    brick.get('brickpath') == path:
                return brick
        return None

    def _verifyVolumeList(self, volDict):
        expectedVolumes = self._getVolumeInfo()
        self.assertEqual(len(expectedVolumes), len(volDict))
        for volName, volumeExpected in expectedVolumes.iteritems():
            vol = volDict[volName]
            self.assertEqual(volumeExpected['volumeType'], vol['type'])
            self.assertEqual(volumeExpected['volumeName'], vol['name'])
            self.assertEqual(vol.get('bricks'), None)

    def _verifyVolumeInfo(self, volDict, volName):
        expectedVolumes = self._mockGetVolumeInfo(volName)
        self.assertEqual(len(expectedVolumes), len(volDict))
        for volName, volumeExpected in expectedVolumes.iteritems():
            vol = volDict[volName]
            self.assertEqual(volumeExpected['volumeType'], vol['type'])
            self.assertEqual(volumeExpected['volumeName'], vol['name'])
            self.assertEqual(len(volumeExpected.get('bricksInfo')),
                             len(vol.get('bricks')))
            for brickExpected in volumeExpected.get('bricksInfo'):
                brick = self._getBrickByHostAndPath(
                    vol.get('bricks'), brickExpected['hostUuid'],
                    brickExpected['name'].split(":")[1])
                self.assertEqual(brick.get('hostUuid'),
                                 brickExpected.get('hostUuid'))

    def testDiscoverVolumesList(self):
        discover_volumes.glustercli.volumeInfo = self._mockGetVolumeInfo
        status, output = discover_volumes.discoverVolumes(None, True)
        volumesList = json.loads(output)
        self._verifyVolumeList(volumesList)

    def testDiscoverVolumesInfo(self):
        discover_volumes.glustercli.volumeInfo = self._mockGetVolumeInfo
        status, output = discover_volumes.discoverVolumes("V1", False)
        volumesList = json.loads(output)
        self._verifyVolumeInfo(volumesList, "V1")

    def testAruguments(self):
        argParser = discover_volumes.get_arg_parser()
        args = argParser.parse_args(["-l", "-v", "V1"])
        self.assertEqual(args.list, True)
        self.assertEqual(args.volume, "V1")
        args = argParser.parse_args(["--list", "--volume", "V1"])
        self.assertEqual(args.list, True)
        self.assertEqual(args.volume, "V1")
        args = argParser.parse_args(["--v", "V1"])
        self.assertEqual(args.volume, "V1")
        self.assertEqual(args.list, False)
        args = argParser.parse_args(["-l"])
        self.assertEqual(args.list, True)
        self.assertEqual(args.volume, None)
