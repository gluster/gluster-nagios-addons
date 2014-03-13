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
from plugins.check_remote_host import *


class TestHello(TestCaseBase):
    # Method to test the execCmd() method
    @mock.patch('check_remote_host.subprocess.Popen')
    def testExecCmd(self, mock_popen):
        reference = subprocess.Popen('any command', close_fds=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        out = "sample output"
        err = ""
        reference.communicate.return_value = (out, err)
        self.assertTrue(reference.communicate, "communicate called")

     # Method to test the getPingStatus() method
    @mock.patch('check_remote_host.execCmd')
    def testGetPingStatus(self, mock_execCmd):
        rc = 0
        out = "sample output"
        err = ""
        mock_execCmd.return_value = (rc, out, err)
        getPingStatus('dummy host')
        mock_execCmd.assert_called_with([
            '/usr/lib64/nagios/plugins/check_ping', '-H', 'dummy', 'host',
            '-w', '3000.0,80%', '-c', '5000.0,100%'])
        self.assertRaises(OSError, execCmd,
                          ['/usr/lib64/nagios/plugins/check_ping', '-H',
                           'dummy', 'host', '-w', '3000.0,80%', '-c',
                           '5000.0,100%'])

    # Method to test the checkLiveStatus() method
    @mock.patch('check_remote_host.socket.socket')
    def testCheckLiveStatus(self, mock_socket):
        reference = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.assertTrue(mock_socket, "called")
        reference.recv.return_value = "0\n"
        checkLiveStatus("dummy host", "dummy srvc")
        reference.connect.assert_called_with('/var/spool/nagios/cmd/live')
        reference.send.assert_called_with("GET services\nColumns: state\n"
                                          "Filter: description = dummy srvc\n"
                                          "Filter: host_address = "
                                          "dummy host\n")
        self.assertEquals(0, checkLiveStatus("dummy host", "dummy srvc"))
