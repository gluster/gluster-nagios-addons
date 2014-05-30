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

import os
import commands
from testrunner import PluginsTestCase as TestCaseBase
from plugins import check_disk_and_inode as checkDisk


class TestDisk(TestCaseBase):
    def mock_osaccess(self, path=None, osflag=None):
        return True

    def mock_getstatusoutput(self, i):
        out = [
            "Filesystem      Size  Used Avail Use% Mounted on",
            "/dev/sda1       290G  174G  102G  64% /",
            "/dev/sdb1        3.9G     0  3.9G   0% /var",
            "/dev/sdc1       290G  200G  100G  40% /mnt1",
            "/dev/mapper/vg_test1-lv_one "
            "35852      1774     32257   85% /lvm1",
            "-                          994         1       994   1% /dev",
            "/dev/mapper/vg_demonode2-lv1 "
            "50G   11G   36G  24% /mnt/lv4",
            "/dev/vda1             485M   36M  424M   8% /mnt/abc1",
            "/dev/mapper/vg_demonode2-lv_2 "
            "5.5G  4.3G  933M  83% /mnt/abc2",
            "none                     0     0     0   -  "
            "/proc/sys/fs/binfmt_misc",
            "10.70.43.190:/exports/abc    50G   11G   36G  24% /mnt",
            "10.70.43.190:vol3      50G   11G   36G  24% /mnt/vol3",
            "10.70.43.190:vol2  52846MB   23228MB   26934MB  47% /mnt/vol2"]

        if type(i) is str:
            disk = i.split()[-1]
            for diskDetail in out:
                if diskDetail.find(disk) >= 0:
                    return 0, diskDetail
        else:
            return 0, out[0] + out[i]
        return 0, ""

    def mock_open(self, fileName):
        out = ["/dev/mapper/vg_demonode2-lv_1 /mnt/abc1 ext4 rw 0 0",
               "proc /proc proc rw 0 0",
               "sysfs /sys sysfs rw 0 0",
               "devpts /dev/pts devpts rw,gid=5,mode=620 0 0",
               "tmpfs /dev/shm tmpfs rw 0 0",
               "/dev/sda1 /boot ext4 rw 0 0",
               "/dev/mapper/vg_demonode2-lv_2 /mnt/abc2 ext4 rw 0 0",
               "none /proc/sys/fs/binfmt_misc binfmt_misc rw 0 0",
               "sunrpc /var/lib/nfs/rpc_pipefs rpc_pipefs rw 0 0",
               "10.70.43.190:/exports/abc /mnt nfs rw,vers=4,addr=10.70.43.190"
               ",clientaddr=10.70.43.190 0 0",
               "10.70.43.190:vol2 /mnt/vol2 nfs rw,addr=10.70.43.190 0 0",
               "10.70.43.190:vol3 /mnt/vol3 nfs rw,addr=10.70.43.190 0 0"]

        class file():
            def readlines(self):
                return out

            def close(self):
                return None
        return file()

    def test_getUsageAndFree(self):
        commands.getstatusoutput = self.mock_getstatusoutput
        os.access = self.mock_osaccess
        disk = checkDisk.getUsageAndFree(1, "", 80, 90, "")
        self.assertEqual(disk['usePcent'], 64)
        self.assertEqual(disk['availPcent'], 36)
        self.assertEqual(disk['used'], 174)
        self.assertEqual(disk['avail'], 102)
        self.assertEqual(disk['path'], '/')

        disk = checkDisk.getUsageAndFree(2, "", 80, 90, "")
        self.assertEqual(disk['usePcent'], 0)
        self.assertEqual(disk['availPcent'], 100)
        self.assertEqual(disk['used'], 0)
        self.assertEqual(disk['avail'], 3.0)
        self.assertEqual(disk['path'], '/var')

        disk = checkDisk.getUsageAndFree(3, "", 80, 90, "")
        self.assertEqual(disk['usePcent'], 40)
        self.assertEqual(disk['availPcent'], 60)
        self.assertEqual(disk['used'], 200)
        self.assertEqual(disk['avail'], 100)
        self.assertEqual(disk['path'], '/mnt1')

        disk = checkDisk.getUsageAndFree(4, "", 80, 90, "")
        self.assertEqual(disk['usePcent'], 85)
        self.assertEqual(disk['availPcent'], 15)
        self.assertEqual(disk['used'], 1774)
        self.assertEqual(disk['avail'], 32257)
        self.assertEqual(disk['path'], '/lvm1')

    def test_getMounts(self):
        checkDisk.open = self.mock_open
        mounts = checkDisk.getMounts("/", [])
        self.assertEqual(mounts[0], "/dev/mapper/vg_demonode2-lv_1")
        self.assertEqual(mounts[1], "/dev/sda1")
        self.assertEqual(mounts[2], "/dev/mapper/vg_demonode2-lv_2")

        mounts = checkDisk.getMounts("/dev/mapper", [])
        self.assertEqual(mounts[0], "/dev/mapper/vg_demonode2-lv_1")
        self.assertEqual(mounts[1], "/dev/mapper/vg_demonode2-lv_2")

        mounts = checkDisk.getMounts("", [])
        self.assertEqual(len(mounts), 12)

    def test_diskUsage(self):
        commands.getstatusoutput = self.mock_getstatusoutput
        checkDisk.open = self.mock_open
        os.access = self.mock_osaccess
        mounts = checkDisk.getMounts("/", [])

        self.assertEqual(checkDisk.showDiskUsage(80,
                                                 90,
                                                 [mounts[1]],
                                                 True,
                                                 usage='BGB'),
                         (0, '64.0% used (174.0BGB out of 290.0BGB)\n'
                          ':mount(s): (/dev/sda1=/)',
                          ['/=174.0BGB;232.0;261.0;0;290.0 '
                           '/=174.0;139.2;156.6;0;290.0']))

        self.assertEqual(checkDisk.showDiskUsage(80,
                                                 90,
                                                 [mounts[1]],
                                                 True),
                         (0, '64.0% used (174.0GB out of 290.0GB)\n'
                          ':mount(s): (/dev/sda1=/)',
                          ['/=64.00%;80;90;0;290.0GB '
                           '/=64.00%;80;90;0;290.0']))

        self.assertEqual(checkDisk.showDiskUsage(80,
                                                 90,
                                                 [mounts[1]], True),
                         (0, '64.0% used (174.0GB out of 290.0GB)\n'
                          ':mount(s): (/dev/sda1=/)',
                          ['/=64.00%;80;90;0;290.0GB '
                           '/=64.00%;80;90;0;290.0']))

        self.assertEqual(checkDisk.showDiskUsage(80,
                                                 90,
                                                 ["/mnt/vol2"], True),
                         (0, '47.0% used (22.68359375TB out of '
                          '51.607421875TB)\n'
                          ':mount(s): (10.70.43.190:vol2=/mnt/vol2)',
                          ['/mnt/vol2=47.00%;80;90;0;52846.0GB '
                           '/mnt/vol2=47.00%;80;90;0;52846.0']))

        self.assertEqual(checkDisk.showDiskUsage(10,
                                                 20,
                                                 ["/mnt/vol2"], True),
                         (2, '47.0% used (22.68359375TB out of '
                          '51.607421875TB)\n'
                          ':mount(s): (10.70.43.190:vol2=/mnt/vol2)',
                          ['/mnt/vol2=47.00%;10;20;0;52846.0GB '
                           '/mnt/vol2=47.00%;10;20;0;52846.0']))

        # negative test
        self.assertEqual(checkDisk.showDiskUsage(1,
                                                 100,
                                                 ["/mnt/vol2"], True),
                         (1, '47.0% used (22.68359375TB out of '
                          '51.607421875TB)\n'
                          ':mount(s): (10.70.43.190:vol2=/mnt/vol2)',
                          ['/mnt/vol2=47.00%;1;100;0;52846.0GB '
                           '/mnt/vol2=47.00%;1;100;0;52846.0']))
