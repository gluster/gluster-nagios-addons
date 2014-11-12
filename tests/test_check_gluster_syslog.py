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
from plugins import check_gluster_syslog
from glusternagios import utils


class TestGlusterSyslog(TestCaseBase):

    # Method to test volume perf data when no matching host method
    @mock.patch('plugins.nscautils.getNagiosClusterName')
    @mock.patch('plugins.nscautils.send_to_nsca_subproc')
    def test_checkProcessMsg(self, mock_send_to_nsca,
                             mock_getNagiosClusterName):
        mock_getNagiosClusterName.return_value = "test-cluster"
        message = ("-/USER/CRIT/GLUSTERFSD [2014-04-06T21:45:33.378443+05:30] "
                   "glusterfsd: [2014-04-06 15:46:59.390038] "
                   "A [quota.c:3670:quota_log_usage] 0-test-vol-quota:"
                   "Usage is above soft limit: 300.0KB used by /test/")
        check_gluster_syslog.processMsg(message)
        mock_send_to_nsca.assert_called_with("test-cluster",
                                             "Volume Quota - test-vol",
                                             utils.PluginStatusCode.WARNING,
                                             "QUOTA: Usage is "
                                             "above soft limit: "
                                             "300.0KB used by /test/")

    @mock.patch('plugins.nscautils.getNagiosClusterName')
    @mock.patch('plugins.nscautils.send_to_nsca_subproc')
    def test_checkProcessMsgForQuorum(self, mock_send_to_nsca,
                                      mock_getNagiosClusterName):
        mock_getNagiosClusterName.return_value = "test-cluster"
        message = ("-/DAEMON/CRIT/ETC-GLUSTERFS-GLUSTERD.VOL "
                   "[2014-05-02T12:40:14.562509+00:00]  "
                   "[2014-05-02 12:40:14.559662] C [MSGID: 106002] "
                   "[glusterd-utils.c:3376:glusterd_do_volume_quorum_action] "
                   "0-management: Server quorum lost for volume dist. "
                   "Stopping local bricks. ")
        check_gluster_syslog.processMsg(message)
        mock_send_to_nsca.assert_called_with("test-cluster",
                                             "Cluster - Quorum",
                                             utils.PluginStatusCode.CRITICAL,
                                             "QUORUM: Cluster server-side "
                                             "quorum lost.")

    @mock.patch('plugins.nscautils.getNagiosClusterName')
    @mock.patch('plugins.nscautils.send_to_nsca_subproc')
    def test_checkProcessInvalidMsgForQuorum(self, mock_send_to_nsca,
                                             mock_getNagiosClusterName):
        mock_getNagiosClusterName.return_value = "test-cluster"
        message = ("-/DAEMON/CRIT/ETC-GLUSTERFS-GLUSTERD.VOL "
                   "[2014-05-02T12:40:14.562509+00:00]  "
                   "[2014-05-02 12:40:14.559662] C "
                   "[glusterd-utils.c:3376:glusterd_do_volume_quorum_action] "
                   "0-management: Random quorum message ")
        check_gluster_syslog.processMsg(message)
        assert not mock_send_to_nsca.called, "send nsca should not be called"
