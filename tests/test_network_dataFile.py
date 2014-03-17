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

SHOW_NETWORK_STATUS_UNKNOWN_IP = {}

SHOW_NETWORK_STATUS_UNKNOWN_OP = \
    {'message': "IFACE UNKNOWN", 'exit_status': 3}

SHOW_NETWORK_STATUS_OK_IP = \
    {'date': '2014-03-11',
     'utc': '1', 'interval': '60',
     'network':
     {'net-dev':
      [{'rxmcst': '0.00',
        'iface': 'tun0', 'rxkB': '11.44',
        'rxpck': '13.28', 'txpck': '13.51',
        'txkB': '1.28', 'txcmp': '0.00',
        'rxcmp': '0.00'},
       {'rxmcst': '0.00', 'iface': 'wlp3s0',
        'rxkB': '12.60', 'rxpck': '13.73',
        'txpck': '13.60', 'txkB': '2.72',
        'txcmp': '0.00', 'rxcmp': '0.00'},
       {'rxmcst': '0.00', 'iface': 'lo',
        'rxkB': '0.04', 'rxpck': '0.12',
        'txpck': '0.12', 'txkB': '0.04',
        'txcmp': '0.00', 'rxcmp': '0.00'},
       {'rxmcst': '0.00', 'iface': 'virbr0-nic',
        'rxkB': '0.00', 'rxpck': '0.00',
        'txpck': '0.00', 'txkB': '0.00',
        'txcmp': '0.00', 'rxcmp': '0.00'},
       {'rxmcst': '0.00', 'iface': 'virbr0',
        'rxkB': '0.00', 'rxpck': '0.00',
        'txpck': '0.00', 'txkB': '0.00',
        'txcmp': '0.00', 'rxcmp': '0.00'},
       {'rxmcst': '0.02', 'iface': 'em1',
        'rxkB': '0.21', 'rxpck': '2.23',
        'txpck': '0.40', 'txkB': '0.03',
        'txcmp': '0.00', 'rxcmp': '0.00'}],
      'per': 'second'},
     'time': '07:00:01'}

SHOW_NETWORK_STATUS_OK_OP = \
    {'message': "IFACE OK: tun0, wlp3s0, lo, "
     "virbr0-nic, virbr0, em1 |tun0.rxpck=13.28 "
     "tun0.txpck=13.51 tun0.rxkB=11.44 tun0.txkB="
     "1.28 wlp3s0.rxpck=13.73 wlp3s0.txpck=13.60 "
     "wlp3s0.rxkB=12.60 wlp3s0.txkB=2.72 lo.rxpck="
     "0.12 lo.txpck=0.12 lo.rxkB=0.04 lo.txkB=0.04"
     " virbr0-nic.rxpck=0.00 virbr0-nic.txpck=0.00"
     " virbr0-nic.rxkB=0.00 virbr0-nic.txkB=0.00 "
     "virbr0.rxpck=0.00 virbr0.txpck=0.00 "
     "virbr0.rxkB=0.00 virbr0.txkB=0.00 em1.rxpck="
     "2.23 em1.txpck=0.40 em1.rxkB=0.21 em1.txkB="
     "0.03", 'exit_status': 0}

SHOW_NETWORK_STATUS_INCLUDE_IP = \
    {'date': '2014-03-11',
     'utc': '1', 'interval': '60',
     'network':
     {'net-dev':
      [{'rxmcst': '0.00',
        'iface': 'tun0', 'rxkB': '11.44',
        'rxpck': '13.28', 'txpck': '13.51',
        'txkB': '1.28', 'txcmp': '0.00',
        'rxcmp': '0.00'},
       {'rxmcst': '0.00', 'iface': 'wlp3s0',
        'rxkB': '12.60', 'rxpck': '13.73',
        'txpck': '13.60', 'txkB': '2.72',
        'txcmp': '0.00', 'rxcmp': '0.00'},
       {'rxmcst': '0.00', 'iface': 'lo',
        'rxkB': '0.04', 'rxpck': '0.12',
        'txpck': '0.12', 'txkB': '0.04',
        'txcmp': '0.00', 'rxcmp': '0.00'},
       {'rxmcst': '0.00', 'iface': 'virbr0-nic',
        'rxkB': '0.00', 'rxpck': '0.00',
        'txpck': '0.00', 'txkB': '0.00',
        'txcmp': '0.00', 'rxcmp': '0.00'},
       {'rxmcst': '0.00', 'iface': 'virbr0',
        'rxkB': '0.00', 'rxpck': '0.00',
        'txpck': '0.00', 'txkB': '0.00',
        'txcmp': '0.00', 'rxcmp': '0.00'},
       {'rxmcst': '0.02', 'iface': 'em1',
        'rxkB': '0.21', 'rxpck': '2.23',
        'txpck': '0.40', 'txkB': '0.03',
        'txcmp': '0.00', 'rxcmp': '0.00'}],
      'per': 'second'},
     'time': '07:00:01'}

SHOW_NETWORK_STATUS_INCLUDE_OP = \
    {'message': "IFACE OK: lo |lo.rxpck=0.12 "
     "lo.txpck=0.12 lo.rxkB=0.04 lo.txkB=0.04",
     'exit_status': 0}

SHOW_NETWORK_STATUS_EXCLUDE_IP = \
    {'date': '2014-03-11',
     'utc': '1', 'interval': '60',
     'network':
     {'net-dev':
      [{'rxmcst': '0.00',
        'iface': 'tun0', 'rxkB': '11.44',
        'rxpck': '13.28', 'txpck': '13.51',
        'txkB': '1.28', 'txcmp': '0.00',
        'rxcmp': '0.00'},
       {'rxmcst': '0.00', 'iface': 'wlp3s0',
        'rxkB': '12.60', 'rxpck': '13.73',
        'txpck': '13.60', 'txkB': '2.72',
        'txcmp': '0.00', 'rxcmp': '0.00'},
       {'rxmcst': '0.00', 'iface': 'lo',
        'rxkB': '0.04', 'rxpck': '0.12',
        'txpck': '0.12', 'txkB': '0.04',
        'txcmp': '0.00', 'rxcmp': '0.00'},
       {'rxmcst': '0.00', 'iface': 'virbr0-nic',
        'rxkB': '0.00', 'rxpck': '0.00',
        'txpck': '0.00', 'txkB': '0.00',
        'txcmp': '0.00', 'rxcmp': '0.00'},
       {'rxmcst': '0.00', 'iface': 'virbr0',
        'rxkB': '0.00', 'rxpck': '0.00',
        'txpck': '0.00', 'txkB': '0.00',
        'txcmp': '0.00', 'rxcmp': '0.00'},
       {'rxmcst': '0.02', 'iface': 'em1',
        'rxkB': '0.21', 'rxpck': '2.23',
        'txpck': '0.40', 'txkB': '0.03',
        'txcmp': '0.00', 'rxcmp': '0.00'}],
      'per': 'second'},
     'time': '07:00:01'}

SHOW_NETWORK_STATUS_EXCLUDE_OP = \
    {'message': "IFACE OK: tun0, wlp3s0, virbr0-nic"
     ", virbr0, em1 |tun0.rxpck=13.28 tun0.txpck=13.51"
     " tun0.rxkB=11.44 tun0.txkB=1.28 wlp3s0.rxpck=13.73"
     " wlp3s0.txpck=13.60 wlp3s0.rxkB=12.60 wlp3s0.txkB="
     "2.72 virbr0-nic.rxpck=0.00 virbr0-nic.txpck=0.00 "
     "virbr0-nic.rxkB=0.00 virbr0-nic.txkB=0.00 "
     "virbr0.rxpck=0.00 virbr0.txpck=0.00 virbr0.rxkB="
     "0.00 virbr0.txkB=0.00 em1.rxpck=2.23 em1.txpck="
     "0.40 em1.rxkB=0.21 em1.txkB=0.03", 'exit_status': 0}

SHOW_NETWORK_STATUS_EXCEPTION_IP = \
    {'date': '2014-03-11',
     'utc': '1', 'interval': '60',
     'network': "test"}

SHOW_NETWORK_STATUS_EXCEPTION_OP = \
    {'message': 'key: string indices must be integers'
     ', not str not found', 'exit_status': 3}
