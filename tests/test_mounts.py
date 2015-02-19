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
import os

from testrunner import PluginsTestCase as TestCaseBase
from plugins import check_mounts


class diskTests(TestCaseBase):
    def mock_getMountPoint(self, mount):
        return mount

    def mock_open(self, filename, mode):
        return open('mounts.txt', 'r')

    def test_parseProcMounts(self):
        check_mounts.open = self.mock_open
        expected = {
            '/bricks/brick2': {
                'device': '/dev/mapper/mygroup-thinv2',
                'mountOptions': 'rw,relatime,attr2,delaylog,'
                'logbsize=64k,sunit=128,swidth=128,noquota',
                'fsType': 'xfs'},
            '/bricks/brick1': {
                'device': '/dev/mapper/mygroup-thinv1',
                'mountOptions': 'rw,relatime,attr2,delaylog,'
                'logbsize=64k,sunit=128,swidth=128,noquota',
                'fsType': 'xfs'},
            '/home': {
                'device': '/dev/mapper/vg_dhcp42149-lv_home',
                'mountOptions': 'rw,relatime,barrier=1,'
                'data=ordered',
                'fsType': 'ext4'},
            '/boot': {
                'device': '/dev/vda1',
                'mountOptions': 'rw,relatime,barrier=1,'
                'data=ordered',
                'fsType': 'ext4'},
            '/': {
                'device': '/dev/mapper/vg_dhcp42149-lv_root',
                'mountOptions': 'rw,relatime,barrier=1,data=ordered',
                'fsType': 'ext4'},
            '/proc/bus/usb': {
                'device': '/proc/bus/usb',
                'mountOptions': 'rw,relatime',
                'fsType': 'usbfs'}
        }
        actual = check_mounts._parseProcMounts()
        self.assertEquals(expected, actual)

    def mock_os_statvfs(self):
        f_bsize = 4096
        f_frsize = 4096
        f_blocks = 12868767
        f_bfree = 11503139
        f_bavail = 10847779
        f_files = 3276800
        f_ffree = 3220784
        f_favail = 3220784
        f_flag = 4096
        f_namemax = 255
        return os.statvfs_result((f_bsize, f_frsize,
                                 f_blocks, f_bfree,
                                 f_bavail, f_files,
                                 f_ffree, f_favail,
                                 f_flag, f_namemax))

    @mock.patch('plugins.check_mounts.os.statvfs')
    def test_getStats(self, mock_os_statvfs):
        mock_os_statvfs.return_value = self.mock_os_statvfs()
        expected = {'used_percent': 10.611956840931228,
                    'used': 5.2094573974609375,
                    'free_inode': 3220784,
                    'used_inode': 56016,
                    'total_inode': 3276800,
                    'used_percent_inode': 1.70947265625,
                    'total': 49.090450286865234,
                    'free': 43.8809928894043}
        actual = check_mounts._getStats("mount_point")
        self.assertEquals(expected, actual)

    def mock_utils_execCommand(self):
        rc = 0
        out = ['  LVM2_LV_UUID=jTHoCy-qFBS-K1FS-WSUp-SG8J-4R7W-2hI01n$LVM2_LV'
               '_NAME=mythinpool$LVM2_DATA_PERCENT=1.09$LVM2_POOL_LV=$LVM2_LV'
               '_ATTR=twi-a-tz--$LVM2_LV_SIZE=1024.00$LVM2_LV_PATH=$LVM2_LV_'
               'METADATA_SIZE=4.00$LVM2_METADATA_PERCENT=1.07$LVM2_VG_NAME='
               'mygroup']
        err = []
        return rc, out, err

    @mock.patch('plugins.check_mounts.utils.execCmd')
    def test_getLvs(self, mock_utils_execCmd):
        mock_utils_execCmd.return_value = self.mock_utils_execCommand()
        expected = {
            'mygroup/mythinpool': {
                'LVM2_LV_PATH': '',
                'LVM2_DATA_PERCENT': '1.09',
                'LVM2_LV_ATTR': 'twi-a-tz--',
                'LVM2_POOL_LV': '',
                'LVM2_LV_NAME': 'mythinpool',
                'LVM2_METADATA_PERCENT': '1.07',
                'LVM2_VG_NAME': 'mygroup',
                'LVM2_LV_SIZE': '1024.00',
                'LVM2_LV_UUID': 'jTHoCy-qFBS-K1FS-WSUp-SG8J-4R7W-2hI01n',
                'LVM2_LV_METADATA_SIZE': '4.00'}
        }
        actual = check_mounts.getLvs()
        self.assertEquals(expected, actual)

    def mock_getStats(self):
        return {'used_percent': 3.194726947731752,
                'used': 0.031635284423828125,
                'free_inode': 1048562,
                'used_inode': 14,
                'total_inode': 1048576,
                'used_percent_inode': 1,
                'total': 0.990234375,
                'free': 0.9585990905761719}

    def mock_parseProcMounts(self):
        return {
            '/brick/brk1': {
                'device': '/dev/mapper/mygroup-thinv1',
                'mountOptions': 'rw,seclabel,relatime,'
                'attr2,inode64,noquota',
                'fsType': 'xfs'},
            '/': {
                'device': '/dev/mapper/fedora_dhcp43--63-root',
                'mountOptions': 'rw,seclabel,relatime,data=ordered',
                'fsType': 'ext4'}
        }

    def mock_getLvs(self):
        return {
            '/dev/mygroup/lvol0': {
                'LVM2_LV_PATH': '/dev/mygroup/lvol0',
                'LVM2_DATA_PERCENT': '',
                'LVM2_LV_ATTR': '-wi-------',
                'LVM2_POOL_LV': '',
                'LVM2_LV_NAME': 'lvol0',
                'LVM2_METADATA_PERCENT': '',
                'LVM2_VG_NAME': 'mygroup',
                'LVM2_LV_SIZE': '4.00',
                'LVM2_LV_UUID': 'NDYC4q-Z57a-DKY3-FQt1-FT63-BuHd-ZScwJZ',
                'LVM2_LV_METADATA_SIZE': ''},
            'mygroup/mythinpool': {
                'LVM2_LV_PATH': '/dev/mygroup/mythinpool',
                'LVM2_DATA_PERCENT': '1.21',
                'LVM2_LV_ATTR': 'twi-a-tz--',
                'LVM2_POOL_LV': '',
                'LVM2_LV_NAME': 'mythinpool',
                'LVM2_METADATA_PERCENT': '1.37',
                'LVM2_VG_NAME': 'mygroup',
                'LVM2_LV_SIZE': '1536.00',
                'LVM2_LV_UUID': 'viQeR0-JHrs-5g27-vVTp-WoOw-bWFy-goaJfO',
                'LVM2_LV_METADATA_SIZE': '4.00'},
            '/dev/dm-7': {
                'LVM2_LV_PATH': '/dev/mygroup/thinv1',
                'LVM2_DATA_PERCENT': '1.04',
                'LVM2_LV_ATTR': 'Vwi-aotz--',
                'LVM2_POOL_LV': 'mythinpool',
                'LVM2_LV_NAME': 'thinv1',
                'LVM2_METADATA_PERCENT': '',
                'LVM2_VG_NAME': 'mygroup',
                'LVM2_LV_SIZE': '1024.00',
                'LVM2_LV_UUID': 'am1XA3-AgYh-IKL4-LfeB-7XR7-dm8U-vbX2Fr',
                'LVM2_LV_METADATA_SIZE': ''}
        }

    def mock_getThinpoolStat(self):
        return {'metadata_used': 5.351562500000018e-05,
                'thinpool_used_percent': 1.21,
                'thinpool_used': 0.01814999999999989,
                'metadata_used_percent': 1.37,
                'metadata_size': 0.00390625,
                'metadata_free': 0.003852734375,
                'thinpool_size': 1.5,
                'thinpool_free': 1.4818500000000001}

    @mock.patch('plugins.check_mounts.getLvs')
    @mock.patch('plugins.check_mounts._getStats')
    @mock.patch('plugins.check_mounts.os.path.realpath')
    @mock.patch('plugins.check_mounts._parseProcMounts')
    @mock.patch('plugins.check_mounts._getMountPoint')
    def test_getMountStats(self, mock_getMountPoint, mock_parseProcMounts,
                           mock_os_path_realpath,
                           mock_getStats, mock_getLvs):
        mock_getMountPoint.return_value = '/brick/brk1'
        mock_os_path_realpath.return_value = '/dev/dm-7'
        mock_parseProcMounts.return_value = self.mock_parseProcMounts()
        mock_getLvs.return_value = self.mock_getLvs()
        mock_getStats.return_value = self.mock_getStats()
        expected = {'/brick/brk1': {
            'used_percent': 3.194726947731752,
            'used': 0.031635284423828125,
            'free_inode': 1048562,
            'used_inode': 14,
            'free': 0.9585990905761719,
            'total_inode': 1048576,
            'mount_point': '/brick/brk1',
            'metadata_used_percent': 1.37,
            'total': 0.990234375,
            'thinpool_free': 1.4818500000000001,
            'metadata_used': 5.351562500000018e-05,
            'thinpool_used_percent': 1.21,
            'used_percent_inode': 1,
            'thinpool_used': 0.01814999999999989,
            'metadata_size': 0.00390625,
            'metadata_free': 0.003852734375,
            'thinpool_size': 1.5}
        }
        include = ['/brick/brk1']
        exclude = []
        actual = check_mounts.getMountStats(exclude, include)
        self.assertEquals(expected, actual)

    def _getDetail(self):
        return {'used_percent': 3.194726947731752,
                'used': 0.031635284423828125,
                'free_inode': 1048562,
                'used_inode': 14,
                'free': 0.9585990905761719,
                'total_inode': 1048576,
                'mount_point': '/run/gluster/snaps/680bdbbeed47'
                '44a9bcba941580a5feed/brick1',
                'metadata_used_percent': 1.37,
                'total': 0.990234375,
                'thinpool_free': 1.4818500000000001,
                'metadata_used': 5.351562500000018e-05,
                'thinpool_used_percent': 1.21,
                'used_percent_inode': 1,
                'thinpool_used': 0.01814999999999989,
                'metadata_size': 0.00390625,
                'metadata_free': 0.003852734375,
                'thinpool_size': 1.5}

    def test_getOutputTest(self):
        detail = self._getDetail()
        actual = check_mounts._getOutputText(detail)
        expected = "/run/gluster/snaps/680bdbbeed4744a9bcba941580a5feed/" \
                   "brick1 - {space - free: 0.959 GiB, used: 3.195%}, " \
                   "{inode - free: 1048562 , used: 1.000%}, {thinpool-data " \
                   "- free: 1.482 GiB, used: 1.210%}, {thinpool-metadata " \
                   "- free: 0.004 GiB, used: 1.370%}"
        self.assertEquals(actual, expected)

    def test_getPerfdata(self):
        detail = self._getDetail()
        warn = 80
        crit = 90
        actual = check_mounts._getPerfdata(detail, warn, crit)
        expected = "/run/gluster/snaps/680bdbbeed4744a9bcba941580a5feed/" \
                   "brick1=3.195%;80;90;0;0.990 /run/gluster/snaps/" \
                   "680bdbbeed4744a9bcba941580a5feed/brick1.inode=1.000%;80;" \
                   "90;0;1048576 /run/gluster/snaps/680bdbbeed4744a9bcba941" \
                   "580a5feed/brick1.thinpool=1.210%;80;90;0;1.500 /run/" \
                   "gluster/snaps/680bdbbeed4744a9bcba941580a5feed/brick1." \
                   "thinpool-metadata=1.370%;80;90;0;0.004"
        self.assertEquals(actual, expected)

    def test_getStatusInfo(self):
        detail = self._getDetail()
        warn = 2
        crit = 4
        actual = check_mounts._getStatusInfo(detail, warn, crit)
        expected = ('WARNING',
                    "mount point /run/gluster/snaps/"
                    "680bdbbeed4744a9bcba941580a5feed/brick1 "
                    "{space used 0.032 / 0.990 GiB}")
        self.assertEquals(actual, expected)

    def test_getPrintableStatus(self):
        mountDetail = {
            '/home': {
                'used_percent': 0.24067115853902976,
                'used': 0.0429229736328125,
                'free_inode': 1196017,
                'used_inode': 15,
                'free': 17.79177474975586,
                'total_inode': 1196032,
                'mount_point': '/home',
                'metadata_used_percent': None,
                'total': 17.834697723388672,
                'thinpool_free': None,
                'metadata_used': None,
                'thinpool_used_percent': None,
                'used_percent_inode': 1,
                'thinpool_used': None,
                'metadata_size': None,
                'metadata_free': None,
                'thinpool_size': None},
            '/boot': {
                'used_percent': 13.709776644000229,
                'used': 0.06375885009765625,
                'free_inode': 127662,
                'used_inode': 354,
                'free': 0.4013023376464844,
                'total_inode': 128016,
                'mount_point': '/boot',
                'metadata_used_percent': None,
                'total': 0.4650611877441406,
                'thinpool_free': None,
                'metadata_used': None,
                'thinpool_used_percent': None,
                'used_percent_inode': 1,
                'thinpool_used': None,
                'metadata_size': None,
                'metadata_free': None,
                'thinpool_size': None},
            '/brick/brk1': {
                'used_percent': 3.194726947731752,
                'used': 0.031635284423828125,
                'free_inode': 1048562,
                'used_inode': 14,
                'free': 0.9585990905761719,
                'total_inode': 1048576,
                'mount_point': '/brick/brk1',
                'metadata_used_percent': 1.37,
                'total': 0.990234375,
                'thinpool_free': 1.4818500000000001,
                'metadata_used': 5.351562500000018e-05,
                'thinpool_used_percent': 1.21,
                'used_percent_inode': 1,
                'thinpool_used': 0.01814999999999989,
                'metadata_size': 0.00390625,
                'metadata_free': 0.003852734375,
                'thinpool_size': 1.5
            }
        }
        expRc = 'CRITICAL'
        expMsg = ['mount point /boot {space used 0.064 / 0.465 GiB}',
                  'mount point /brick/brk1 '
                  '{space used 0.032 / 0.990 GiB}']
        expOut = ['/boot - {space - free: 0.401 GiB, used: 13.710%},'
                  ' {inode - free: 127662 , used: 1.000%}',
                  '/brick/brk1 - {space - free: 0.959 GiB, used: 3.195%},'
                  ' {inode - free: 1048562 , used: 1.000%}, '
                  '{thinpool-data - free: 1.482 GiB, used: 1.210%},'
                  ' {thinpool-metadata - free: 0.004 GiB, used: 1.370%}',
                  '/home - {space - free: 17.792 GiB, used: 0.241%},'
                  ' {inode - free: 1196017 , used: 1.000%}']
        expPerfData = ['/boot=13.710%;2;4;0;0.465 /boot.inode='
                       '1.000%;2;4;0;128016',
                       '/brick/brk1=3.195%;2;4;0;0.990 '
                       '/brick/brk1.inode=1.000%;2;4;0;1048576 '
                       '/brick/brk1.thinpool=1.210%;2;4;0;1.500 '
                       '/brick/brk1.thinpool-metadata=1.370%;2;4;0;0.004',
                       '/home=0.241%;2;4;0;17.835 '
                       '/home.inode=1.000%;2;4;0;1196032']
        warning = 2
        critical = 4
        actRc, actMsg, actOut, actPerfData = check_mounts.getPrintableStatus(
            mountDetail,
            warning,
            critical
        )
        self.assertEquals(actRc, expRc)
        self.assertEquals(actMsg, expMsg)
        self.assertEquals(actOut, expOut)
        self.assertEquals(actPerfData, expPerfData)
