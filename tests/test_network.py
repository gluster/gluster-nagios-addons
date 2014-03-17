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
from plugins import network
import test_network_dataFile


class networkTests(TestCaseBase):

    def _showNetStatus_unknown_test(self):
        actual = network.showNetStat(
            test_network_dataFile.SHOW_NETWORK_STATUS_UNKNOWN_IP
        )
        self.assertEquals(
            actual,
            test_network_dataFile.SHOW_NETWORK_STATUS_UNKNOWN_OP
        )

    def _showNetStatus_ok_test(self):
        actual = network.showNetStat(
            test_network_dataFile.SHOW_NETWORK_STATUS_OK_IP
        )
        self.assertEquals(
            actual,
            test_network_dataFile.SHOW_NETWORK_STATUS_OK_OP
        )

    def _showNetStatus_include_test(self):
        in_list = ["lo"]
        list_type = "include"
        actual = network.showNetStat(
            test_network_dataFile.SHOW_NETWORK_STATUS_INCLUDE_IP,
            in_list,
            list_type
        )
        self.assertEquals(
            actual,
            test_network_dataFile.SHOW_NETWORK_STATUS_INCLUDE_OP
        )

    def _showNetStatus_exclude_test(self):
        ex_list = ["lo"]
        list_type = "exclude"
        actual = network.showNetStat(
            test_network_dataFile.SHOW_NETWORK_STATUS_EXCLUDE_IP,
            ex_list,
            list_type
        )
        self.assertEquals(
            actual,
            test_network_dataFile.SHOW_NETWORK_STATUS_EXCLUDE_OP
        )

    def _showNetStatus_exception_test(self):
        actual = network.showNetStat(
            test_network_dataFile.SHOW_NETWORK_STATUS_EXCEPTION_IP
        )
        self.assertEquals(
            actual,
            test_network_dataFile.SHOW_NETWORK_STATUS_EXCEPTION_OP
        )

    def test_showNetStatus(self):
        self._showNetStatus_unknown_test()
        self._showNetStatus_ok_test()
        self._showNetStatus_include_test()
        self._showNetStatus_exclude_test()
        self._showNetStatus_exception_test()
