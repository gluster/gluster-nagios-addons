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
from datetime import datetime
import xml.etree.cElementTree as etree
from testrunner import PluginsTestCase as TestCaseBase

import plugins


class sadfTests(TestCaseBase):
    @mock.patch('plugins.sadf.utcnow')
    def test_getLatestStat_success(self, utcnow_mock):
        expectedDict = {'cpu-load': {'cpu': {'idle': '96.62',
                                             'iowait': '0.17',
                                             'nice': '0.00',
                                             'number': 'all',
                                             'steal': '0.00',
                                             'system': '1.20',
                                             'user': '2.01'}},
                        'date': '2014-03-19',
                        'interval': '60',
                        'time': '10:19:01',
                        'utc': '1'}
        utcnow_mock.return_value = datetime(2014, 3, 19, 10, 19, 22,
                                            164227)
        with open("getLatestStat_success.xml") as f:
            out = f.read()
            tree = etree.fromstring(out)
        outDict = plugins.sadf.getLatestStat(tree)
        self.assertEquals(expectedDict, outDict)

    def test_getLatestStat_failure(self):
        expectedValue = None
        with open("getLatestStat_success.xml") as f:
            out = f.read()
            tree = etree.fromstring(out)
        outValue = plugins.sadf.getLatestStat(tree)
        self.assertEquals(expectedValue, outValue)

    def test_getLatestStat_exception(self):
        def _getLatestStat():
            with open("getLatestStat_exception.xml") as f:
                out = f.read()
            tree = etree.fromstring(out)
            plugins.sadf.getLatestStat(tree)

        self.assertRaises(plugins.sadf.SadfXmlErrorException, _getLatestStat)
