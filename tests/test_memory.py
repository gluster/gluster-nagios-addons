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
from plugins import memory
import test_memory_dataFile


class memoryTests(TestCaseBase):

    def _showMemStatus_unknown_test(self):
        w = 80
        c = 90
        actual = memory.showMemStat(
            w, c,
            test_memory_dataFile.SHOW_MEMORY_STATUS_UNKNOWN_IP
        )
        self.assertEquals(
            actual,
            test_memory_dataFile.SHOW_MEMORY_STATUS_UNKNOWN_OP
        )

    def _showMemStatus_ok_test(self):
        w = 60
        c = 70
        actual = memory.showMemStat(
            w, c,
            test_memory_dataFile.SHOW_MEMORY_STATUS_OK_IP
        )
        self.assertEquals(
            actual,
            test_memory_dataFile.SHOW_MEMORY_STATUS_OK_OP
        )

    def _showMemStatus_warning_test(self):
        w = 40
        c = 60
        actual = memory.showMemStat(
            w, c,
            test_memory_dataFile.SHOW_MEMORY_STATUS_WARNING_IP
        )
        self.assertEquals(
            actual,
            test_memory_dataFile.SHOW_MEMORY_STATUS_WARNING_OP
        )

    def _showMemStatus_critical_test(self):
        w = 30
        c = 40
        actual = memory.showMemStat(
            w, c,
            test_memory_dataFile.SHOW_MEMORY_STATUS_CRITICAL_IP
        )
        self.assertEquals(
            actual,
            test_memory_dataFile.SHOW_MEMORY_STATUS_CRITICAL_OP
        )

    def _showMemStatus_exception_test(self):
        w = 30
        c = 40
        actual = memory.showMemStat(
            w, c,
            test_memory_dataFile.SHOW_MEMORY_STATUS_EXCEPTION_IP
        )
        self.assertEquals(
            actual,
            test_memory_dataFile.SHOW_MEMORY_STATUS_EXCEPTION_OP
        )

    def test_showMemStatus(self):
        self._showMemStatus_unknown_test()
        self._showMemStatus_ok_test()
        self._showMemStatus_warning_test()
        self._showMemStatus_critical_test()
        self._showMemStatus_exception_test()
