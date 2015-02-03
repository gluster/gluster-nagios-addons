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
import plugins


stat = {'date': '2014-04-17',
        'interval': '60',
        'network': {'net-dev': [{'iface': 'tun0',
                                 'rxcmp': '0.00',
                                 'rxkB': '0.01',
                                 'rxmcst': '0.00',
                                 'rxpck': '0.10',
                                 'txcmp': '0.00',
                                 'txkB': '0.01',
                                 'txpck': '0.08'},
                                {'iface': 'wlp3s0',
                                 'rxcmp': '0.00',
                                 'rxkB': '0.00',
                                 'rxmcst': '0.00',
                                 'rxpck': '0.00',
                                 'txcmp': '0.00',
                                 'txkB': '0.00',
                                 'txpck': '0.00'},
                                {'iface': 'lo',
                                 'rxcmp': '0.00',
                                 'rxkB': '0.00',
                                 'rxmcst': '0.00',
                                 'rxpck': '0.00',
                                 'txcmp': '0.00',
                                 'txkB': '0.00',
                                 'txpck': '0.00'},
                                {'iface': 'virbr0-nic',
                                 'rxcmp': '0.00',
                                 'rxkB': '0.00',
                                 'rxmcst': '0.00',
                                 'rxpck': '0.00',
                                 'txcmp': '0.00',
                                 'txkB': '0.00',
                                 'txpck': '0.00'},
                                {'iface': 'virbr0',
                                 'rxcmp': '0.00',
                                 'rxkB': '0.00',
                                 'rxmcst': '0.00',
                                 'rxpck': '0.00',
                                 'txcmp': '0.00',
                                 'txkB': '0.00',
                                 'txpck': '0.00'},
                                {'iface': 'enp0s29u1u2',
                                 'rxcmp': '0.00',
                                 'rxkB': '0.09',
                                 'rxmcst': '0.00',
                                 'rxpck': '1.15',
                                 'txcmp': '0.00',
                                 'txkB': '0.25',
                                 'txpck': '1.65'},
                                {'iface': 'em1',
                                 'rxcmp': '0.00',
                                 'rxkB': '0.00',
                                 'rxmcst': '0.00',
                                 'rxpck': '0.00',
                                 'txcmp': '0.00',
                                 'txkB': '0.00',
                                 'txpck': '0.00'}],
                    'per': 'second'},
        'time': '02:36:01',
        'utc': '1'}

interfaces = {'em1': {'flags': None, 'ipaddr': None},
              'enp0s29u1u2': {'flags': 4163, 'ipaddr': '192.168.42.182'},
              'lo': {'flags': 73, 'ipaddr': '127.0.0.1'},
              'tun0': {'flags': 4305, 'ipaddr': '10.10.63.201'},
              'virbr0': {'flags': 4099, 'ipaddr': '192.168.122.1'},
              'wlp3s0': {'flags': None, 'ipaddr': None}}


class networkTests(TestCaseBase):
    @mock.patch('plugins.network._getNetworkInterfaces')
    def test_network_default(self, _getNetworkInterfaces_mock):
        expected = (0, "OK: tun0:UP,virbr0:DOWN,enp0s29u1u2:UP |"
                    "tun0.rxpck=0.10 tun0.txpck=0.08 "
                    "tun0.rxkB=0.01 tun0.txkB=0.01 "
                    "virbr0.rxpck=0.00 virbr0.txpck=0.00 "
                    "virbr0.rxkB=0.00 virbr0.txkB=0.00 "
                    "enp0s29u1u2.rxpck=1.15 enp0s29u1u2.txpck=1.65 "
                    "enp0s29u1u2.rxkB=0.09 enp0s29u1u2.txkB=0.25")
        _getNetworkInterfaces_mock.return_value = interfaces

        actual = plugins.network._getStatMessage(stat)
        self.assertEquals(expected, actual)

    @mock.patch('plugins.network._getNetworkInterfaces')
    def test_network_all(self, _getNetworkInterfaces_mock):
        expected = (0, "OK: tun0:UP,wlp3s0:DOWN,lo:UP,virbr0-nic:DOWN,"
                    "virbr0:DOWN,enp0s29u1u2:UP,em1:DOWN |"
                    "tun0.rxpck=0.10 tun0.txpck=0.08 "
                    "tun0.rxkB=0.01 tun0.txkB=0.01 "
                    "wlp3s0.rxpck=0.00 wlp3s0.txpck=0.00 "
                    "wlp3s0.rxkB=0.00 wlp3s0.txkB=0.00 "
                    "lo.rxpck=0.00 lo.txpck=0.00 lo.rxkB=0.00 lo.txkB=0.00 "
                    "virbr0-nic.rxpck=0.00 virbr0-nic.txpck=0.00 "
                    "virbr0-nic.rxkB=0.00 virbr0-nic.txkB=0.00 "
                    "virbr0.rxpck=0.00 virbr0.txpck=0.00 "
                    "virbr0.rxkB=0.00 virbr0.txkB=0.00 "
                    "enp0s29u1u2.rxpck=1.15 enp0s29u1u2.txpck=1.65 "
                    "enp0s29u1u2.rxkB=0.09 enp0s29u1u2.txkB=0.25 "
                    "em1.rxpck=0.00 em1.txpck=0.00 "
                    "em1.rxkB=0.00 em1.txkB=0.00")
        _getNetworkInterfaces_mock.return_value = interfaces

        actual = plugins.network._getStatMessage(stat, all=True)
        self.assertEquals(expected, actual)

    @mock.patch('plugins.network._getNetworkInterfaces')
    def test_network_includes(self, _getNetworkInterfaces_mock):
        expected = (1, "WARNING: tun0:UP,em1:DOWN |"
                    "tun0.rxpck=0.10 tun0.txpck=0.08 "
                    "tun0.rxkB=0.01 tun0.txkB=0.01 "
                    "em1.rxpck=0.00 em1.txpck=0.00 "
                    "em1.rxkB=0.00 em1.txkB=0.00")
        _getNetworkInterfaces_mock.return_value = interfaces

        actual = plugins.network._getStatMessage(stat,
                                                 includes=('tun0', 'em1'))
        self.assertEquals(expected, actual)

    @mock.patch('plugins.network._getNetworkInterfaces')
    def test_network_excludes(self, _getNetworkInterfaces_mock):
        expected = (0, "OK: virbr0:DOWN,enp0s29u1u2:UP |"
                    "virbr0.rxpck=0.00 virbr0.txpck=0.00 "
                    "virbr0.rxkB=0.00 virbr0.txkB=0.00 "
                    "enp0s29u1u2.rxpck=1.15 enp0s29u1u2.txpck=1.65 "
                    "enp0s29u1u2.rxkB=0.09 enp0s29u1u2.txkB=0.25")
        _getNetworkInterfaces_mock.return_value = interfaces

        actual = plugins.network._getStatMessage(stat,
                                                 excludes=('tun0', ))
        self.assertEquals(expected, actual)
