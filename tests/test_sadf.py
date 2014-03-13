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

import xml.etree.cElementTree as etree

from testrunner import PluginsTestCase as TestCaseBase
from plugins import sadf


class sadfTests(TestCaseBase):

    def _etree_to_dict_arg_test(self):
        out = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE sysstat PUBLIC "DTD v2.15 sysstat //EN"
"http://pagesperso-orange.fr/sebastien.godard/sysstat-2.15.dtd">
<sysstat>
<sysdata-version>2.15</sysdata-version>
<host nodename="dhcp-0-171.blr.redhat.com">
<sysname>Linux</sysname>
<release>3.11.3-201.fc19.x86_64</release>
<machine>x86_64</machine>
<number-of-cpus>4</number-of-cpus>
<file-date>2014-03-07</file-date>
<statistics>
<timestamp date="2014-03-07" time="05:00:01" utc="1" interval="59">
<memory per="second" unit="kB">
<memfree>6821428</memfree>
<memused>1049448</memused>
<memused-percent>13.33</memused-percent>
<buffers>49416</buffers>
<cached>536932</cached>
<commit>2127484</commit>
<commit-percent>7.38</commit-percent>
<active>361428</active>
<inactive>487048</inactive>
<dirty>1256</dirty>
</memory>
</timestamp>
</statistics>
<restarts>
<boot date="2014-03-07" time="04:58:08" utc="1"/>
</restarts>
</host>
</sysstat>
"""
        tree = etree.fromstring(out)
        expected_dict = \
            {'sysstat': {'host':
                         {'sysname': 'Linux',
                          'statistics': {'timestamp':
                                         {'date': '2014-03-07',
                                          'utc': '1', 'interval': '59',
                                          'time': '05:00:01',
                                          'memory':
                                          {'memused-percent': '13.33',
                                           'cached': '536932',
                                           'unit': 'kB',
                                           'per': 'second',
                                           'memfree': '6821428',
                                           'inactive': '487048',
                                           'commit-percent': '7.38',
                                           'active': '361428',
                                           'commit': '2127484',
                                           'memused': '1049448',
                                           'buffers': '49416',
                                           'dirty': '1256'}}},
                          'nodename': 'dhcp-0-171.blr.redhat.com',
                          'file-date': '2014-03-07',
                          'number-of-cpus': '4',
                          'restarts': {'boot':
                                       {'date': '2014-03-07', 'utc': '1',
                                        'time': '04:58:08'}},
                          'machine': 'x86_64',
                          'release': '3.11.3-201.fc19.x86_64'},
                         'sysdata-version': '2.15'}}

        actual_dict = sadf.etree_to_dict(tree)
        self.assertEquals(actual_dict, expected_dict)

    def _etree_to_dict_string_test(self):
        out = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE sysstat PUBLIC "DTD v2.15 sysstat //EN"
"http://pagesperso-orange.fr/sebastien.godard/sysstat-2.15.dtd">
<sysstat>
<sysdata-version>2.15</sysdata-version>
<host nodename="dhcp-0-171.blr.redhat.com">
<sysname>Linux</sysname>
<release>3.11.3-201.fc19.x86_64</release>
<machine>x86_64</machine>
<number-of-cpus>4</number-of-cpus>
<file-date>2014-03-07</file-date>
<statistics>
<timestamp date="2014-03-07" time="05:00:01" utc="1" interval="59">
<memory per="second" unit="kB">
Test string
<memfree>6821428</memfree>
<memused>1049448</memused>
<memused-percent>13.33</memused-percent>
<buffers>49416</buffers>
<cached>536932</cached>
<commit>2127484</commit>
<commit-percent>7.38</commit-percent>
<active>361428</active>
<inactive>487048</inactive>
<dirty>1256</dirty>
</memory>
</timestamp>
</statistics>
<restarts>
<boot date="2014-03-07" time="04:58:08" utc="1"/>
</restarts>
</host>
</sysstat>
"""
        tree = etree.fromstring(out)
        expected_dict = \
            {'sysstat': {'host':
                         {'sysname': 'Linux',
                          'statistics': {'timestamp':
                                         {'date': '2014-03-07',
                                          'utc': '1', 'interval': '59',
                                          'time': '05:00:01', 'memory':
                                          {'#text': 'Test string',
                                           'memused-percent': '13.33',
                                           'cached': '536932', 'unit': 'kB',
                                           'per': 'second',
                                           'memfree': '6821428',
                                           'inactive': '487048',
                                           'commit-percent': '7.38',
                                           'active': '361428',
                                           'commit': '2127484',
                                           'memused': '1049448',
                                           'buffers': '49416',
                                           'dirty': '1256'}}},
                          'nodename': 'dhcp-0-171.blr.redhat.com',
                          'file-date': '2014-03-07', 'number-of-cpus': '4',
                          'restarts': {'boot': {'date': '2014-03-07',
                                                'utc': '1',
                                                'time': '04:58:08'}},
                          'machine': 'x86_64',
                          'release': '3.11.3-201.fc19.x86_64'},
                         'sysdata-version': '2.15'}}
        actual_dict = sadf.etree_to_dict(tree)
        #print actual_dict
        #exit(0)
        self.assertEquals(actual_dict, expected_dict)

    def _etree_to_dict_empty_test(self):
        out = """<?xml version="1.0" encoding="UTF-8"?>
<sysstat>
<buffers></buffers>
<cached></cached>
<commit>2127484</commit>
<commit-percent>7.38</commit-percent>
<active>361428</active>
<inactive>487048</inactive>
</sysstat>
"""
        tree = etree.fromstring(out)
        expected_dict = \
            {'sysstat': {'cached': None,
                         'inactive': '487048',
                         'commit-percent': '7.38',
                         'active': '361428',
                         'commit': '2127484',
                         'buffers': None}}
        actual_dict = sadf.etree_to_dict(tree)
        self.assertEquals(actual_dict, expected_dict)

    def test_etree_to_dict_test(self):
        self._etree_to_dict_arg_test()
        self._etree_to_dict_string_test()
        self._etree_to_dict_empty_test()
